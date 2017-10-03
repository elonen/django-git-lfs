from django.core.exceptions import ImproperlyConfigured
import io, os, re, collections, tempfile
from os.path import dirname, sep as SEP
from typing import Tuple, Mapping, Callable

from .storage import DjlfsBatchStorageBase
from .utils import LfsError, validate_oid, get_env_or_django_conf

import logging
logger = logging.getLogger(__name__)


'''
os.environ['DJANGO_SECRET_KEY'] = 'RANDOM_SECRET_KEY_HERE'

Django: request.get_full_path()

Apache 2.4.8+
-------------
<LocationMatch "^/combined/(?<sitename>[^/]+)">
    require ldap-group cn=%{env:MATCH_SITENAME},ou=combined,o=Example
</LocationMatch>
'''

def _path_for_oid(oid: str) -> str:
    try:
        validate_oid(oid)
        lsdir = get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_DIR')
        if not os.path.exists(lsdir):
            raise FileNotFoundError('LFS config error: storage dir does not exist.')

        return lsdir.rstrip(SEP) + SEP + oid[0:2] + SEP + oid[2:4] + SEP + oid

    except AttributeError as e:
        raise ImproperlyConfigured('Local storage dir not configured: %s' % str(e))


class LocalFileStorage(DjlfsBatchStorageBase):

    def get_size(self, oid:str) -> int:
        return os.stat(_path_for_oid(oid)).st_size


    def open_as_url(self, oid:str, mode:str) -> Tuple[ str, Mapping[str, str] ]:
        '''
        Read URL template from env or Django config (in that order), and try to
        construct an upload / download URL from them. If extra headers are specified,
        the LFS client is instructed to include then when later getting/putting the file.
        '''
        assert(mode=='r' or mode=='w')        
        http_mode = 'GET' if mode=='r' else 'PUT'
        url_template = get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_HTTP_URL_TEMPLATE_%s' % http_mode, required=False)
        if url_template is None:
            return None

        extra_headers = get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_HTTP_HEADERS_%s' % http_mode, required=False) or {}
        if not isinstance(extra_headers, collections.Mapping):
            raise LfsError('Configuration error: DJLFS_BATCH_LOCAL_STORAGE_HTTP_HEADERS_* must be dict-like.', status_code=500)

        try:
            if str(url_template).strip() != '':
                return (url_template.format(oid=oid),
                        extra_headers)
            else:
                return None
        except KeyError as e:
            raise LfsError('Configuration error: bad URL template. It can contain variable {oid}.', status_code=500)

        validate_oid(oid)


    def open_as_file(self, oid:str, mode:str) -> Tuple[ io.RawIOBase, Callable, Callable ]:
        '''
        Open given object for read / write on a local directory, specified in either
        env or Django settings (in that order).

        Read simply returns a File objects as-is.
        Write creates a tempory file for the client to write in, and then renames/moves it
        to the final place after succesful upload (or deletes on failure).
        '''
        assert(mode=='r' or mode=='w')
        final_path = _path_for_oid(oid)
        logger.debug('open_as_file(), path = "%s", mode = "%s"' % (final_path, mode))

        if mode == 'r':
            # Read
            f = open(final_path, 'rb')
            def _close():
                try:
                    f.close()
                except Exception:
                    pas
            return (f, _close, _close)

        else:
            # Write

            storage_dir = get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_DIR').rstrip(SEP)
            if not os.path.exists(storage_dir):
                raise FileNotFoundError('LFS config error: storage dir does not exist.')

            # Create temp file to write in

            tempdir = storage_dir + SEP + 'tmp'
            os.makedirs(tempdir, exist_ok=True)
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=tempdir)
            tpath = temp_file.name

            def ok_rename_temp():
                temp_file.close()
                try:
                    logger.debug('mkdir %s' % dirname(final_path))
                    os.makedirs(dirname(final_path), exist_ok=True)

                    logger.debug('Upload success. Renaming %s -> %s' % (tpath, final_path))
                    os.rename(tpath, final_path)
                    
                except Exception as e:
                    logger.error("Failed to move uploaded file in place: " + str(e))
                    try:
                        os.remove(tpath)
                    except Exception:
                        pass

            def failed_delete_temp():
                try:
                    temp_file.close()
                    os.remove(tpath)
                except Exception as e:
                    logger.info("failed_delete_temp() couldn't delete temp file: %s" % str(tpath))
                    pass

            return (temp_file, ok_rename_temp, failed_delete_temp)

DjlfsBatchStorageBase.register(LocalFileStorage)
