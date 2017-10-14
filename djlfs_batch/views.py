from _ast import keyword
import json, re, hashlib, os
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404, FileResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.detail import BaseDetailView

from .utils import LfsError, validate_oid, get_env_or_django_conf, verify_token, make_token
from .storage_filesys import LocalFileStorage

import logging
logger = logging.getLogger(__name__)
 

class JsonUtilsMixin(object):
    '''Helper to parse JSON input, and always apply Git LFS -specific CONTENT-TYPE.'''

    def json_response(self, json_data, **kwargs):
        kwargs.setdefault('content_type', 'application/vnd.git-lfs+json')
        return JsonResponse(json_data, **kwargs)

    def get_json_body_or_raise_error(self):
        try:
            return self._json_request_body
        except AttributeError:
            try:
                self._json_request_body = json.loads(self.request.body.decode('utf-8'))
                return self._json_request_body
            except Exception as e:
                raise LfsError('Bad batch request. Missing JSON request data. %s' % str(e), status_code=400)



class ActionInitView(JsonUtilsMixin, View):
    '''
    Handler for POST /objects/batch
    Client calls this to initiate uploads and downloads for given OIDs.
    ''' 

    def post(self, request, *args, **kwargs):
        try:
            json_body = self.get_json_body_or_raise_error()
            logger.debug('Init request: ' + str(json_body))

            # Validate client arguments first

            op = json_body.get('operation')
            if op != 'download' and op != 'upload':
                raise LfsError(
                    "Unknown batch request. Operation aws '%s', this server only understands 'upload' or 'download'." % str(op),
                    status_code=400)

            objs = json_body.get('objects')
            if objs is None or len(objs)==0:
                raise LfsError("Bad batch request. No 'objects' given.", status_code=400)

            transfers = json_body.get('transfers')
            if transfers is not None and 'basic' not in transfers:
                raise LfsError("Unsupported transfer method list. This serrver only supports 'basic'.", status_code=501)

            storage = LocalFileStorage()
            expire_secs = get_env_or_django_conf('DJLFS_BATCH_TOKEN_EXPIRE_SECS', required=False) or 60*15

            # Handle all OID requests in sequence
            res_objects = []
            for obj_parms in objs:
                oid = obj_parms.get('oid')
                size = obj_parms.get('size')

                try:
                    # Validate some more
                    if oid is None:
                        raise LfsError("OID not given.", status_code=400)
                    elif size is None or size < 0:
                        raise LfsError('Bad size specified: %s' % str(size), status_code=400)
                    validate_oid(oid)

                    res = {'oid': str(oid), 'size': size, 'authenticated': True}

                    # Check if the file exists (by reading its size)
                    real_size = None
                    try:
                        real_size = storage.get_size(oid)
                    except OSError as e:
                        pass

                    # Check for missing / already existing files
                    if op=='download' and real_size is None:
                        raise LfsError('OID not found.', status_code=404)
                    elif op=='upload' and  real_size is not None:
                        # User offered to upload object we already have -> omit actions:
                        if real_size == size:
                            logger.debug('Client offered to upload already existing object. Skipping.')
                            res_objects.append(res)
                            continue
                        else:
                            logger.warning('Existing object has different size than client announced! Letting them re-upload.')

                    open_mode = 'r' if op=='download' else 'w'
                    as_url = storage.open_as_url(oid, open_mode)

                    auth_headers = { 'lfs-batch-token': make_token(op, expire_secs) }

                    if as_url is not None:
                        # URL (HTTP server)
                        logger.debug('open_as_url returned OK: ' + str(as_url))
                        auth_headers.update(as_url[1]) # add possible extra headers
                        res['actions'] = {
                            op: {
                                'href': as_url[0],
                                'header': auth_headers,
                                'expires_in': expire_secs,  # actually never
                                }
                            }
                    else:
                        # Local file (internal view)
                        as_file = storage.open_as_file(oid, open_mode)
                        if not as_file:
                            raise LfsError('Bad file storage backend: no download method available.', status_code=500)
                        logger.debug('open_as_file returned OK: ' + str(as_file))
                        as_file[2]() # close and delete
                        action_view = 'djlfs_batch:' + ('download' if op=='download' else 'upload')
                        res['actions'] = {
                            op: {
                                'href': self.request.build_absolute_uri(reverse(action_view, kwargs={"oid": oid})),
                                'header': auth_headers,
                                'expires_in': expire_secs,
                                }
                            }

                    res_objects.append(res)

                # Object specific errors still return HTTP 200, but report
                # the errors in a JSON list per object.
                except LfsError as e:
                        res_objects.append({
                                'oid': str(oid), 'size': size or 0,
                                'error': {'code': e.status_code, 'message': e.message }
                            })
                except OSError as e:
                        res_objects.append({
                                'oid': str(oid), 'size': size or 0,
                                'error': {'code': 404, 'message': str(e) }
                            })

            # All done. Return JSON and status 200
            ret = { 'transfer': 'basic', 'objects': res_objects }
            #logger.debug('RESPONSE = %s' % json.dumps(ret, indent=2))
            return self.json_response(ret)

        # These are only reached if the whole batch request failed.
        except LfsError as e:
            logger.error('LfsError: %s' % str(e))
            return e.as_http_response()
        except Exception as e:
            logger.error('Generic exception: %s' % str(e))
            return LfsError('Internal server error: ' + str(e), status_code=500).as_http_response()

batch_action_init = csrf_exempt(ActionInitView.as_view())



class ObjectDownloadView(JsonUtilsMixin, View):
    '''
    Validate given OID and just serve a local file.
    '''
    def get(self, request, *args, **kwargs):
        try:
            if not get_env_or_django_conf('DJLFS_BATCH_ALLOW_LOCAL_FS_DOWNLOAD_WITHOUT_TOKEN', required=False):
                verify_token(request, 'download')
            oid = self.kwargs.get('oid', '')
            f = LocalFileStorage().open_as_file(oid, 'r')
            return FileResponse(f[0])
        except LfsError as e:
            logger.error('Catched LfsError: %s' % str(e))
            return e.as_http_response()

batch_download = csrf_exempt(ObjectDownloadView.as_view())



class ObjectUploadView(JsonUtilsMixin, View):
    '''
    Receive a file from the client, verify checksum
    and if it matches, make it available for download.
    If not, just delete it and return an error.
    '''
    CHUNK_SIZE = 1024 * 1024
    def put(self, request, *args, **kwargs):
        f = None
        try:
            oid = self.kwargs.get('oid', '')
            verify_token(request, 'upload')
            f = LocalFileStorage().open_as_file(oid, 'w')

            chunk = True
            hash_func = hashlib.sha256()
            while chunk:
                chunk = request.read(self.CHUNK_SIZE)
                f[0].write(chunk)
                hash_func.update(chunk)

            calc_hash = hash_func.hexdigest().lower()
            if calc_hash != oid.lower():
                if len(calc_hash) != len(oid):
                    raise LfsError("Given OID doesn't seem to be sha256?", status_code=400)
                else:
                    raise LfsError('OID of request does not match file contents', status_code=400)

            f[1]() # Call success callback (to move temp file in final place)
            return HttpResponse()  # Just return status 200

        except LfsError as e:
            logger.debug('Catched LfsError: %s' % str(e))
            if f:
                f[2]() # Call failure callback
            return e.as_http_response()

        except Exception as e:
            logger.debug('Catched generic exception: %s' % str(e))
            if f:
                f[2]() # Call failure callback
            return LfsError('Internal server error: ' + str(e), status_code=500).as_http_response()

batch_upload = csrf_exempt(ObjectUploadView.as_view())


class ObjectCheckTokenView(JsonUtilsMixin, View):
    '''
    Only validate token from header and return status 200 if ok,
    or an error code if not. This is intended to be
    used as an external HTTP auth handler for Nginx or such.
    '''
    def get(self, request, *args, **kwargs):
        try:
            op = self.kwargs.get('op', '')
            verify_token(request, op)
            return HttpResponse()   # just return status 200 if token is ok
        except LfsError as e:
            logger.error('Catched LfsError: %s' % str(e))
            return e.as_http_response()

check_token = csrf_exempt(ObjectCheckTokenView.as_view())
