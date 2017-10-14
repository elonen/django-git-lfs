import os, re, time, datetime, hashlib
from django.http import JsonResponse
import jwt, django.conf
from django.conf import settings

class LfsError(Exception):

    def __init__(self, message, status_code):
        super(LfsError, self).__init__(message)
        assert(status_code > 0)
        assert(message is not None)
        self.status_code = status_code
        self.message = message

    def as_http_response(self):
        return JsonResponse(
            {'message': str(self.message)},
            content_type = 'application/vnd.git-lfs+json',
            status = self.status_code )

    def __str__(self):
        return '[STATUS %s] %s' % (str(self.status_code), str(self.message))


def validate_oid(oid: str):
    oid_format = re.compile("^([a-f0-9]+)$")
    if not oid_format.match(str(oid)):
        raise LfsError('Malformed LFS OID: %s' % str(oid), status_code=400)


def get_env_or_django_conf(conf_key: str, required=True) -> str:
    res = os.environ.get(conf_key)
    if res is None:
        try:
             res = getattr(settings, conf_key)
        except Exception:
            pass
    if not res and required:
        raise LfsError("Configuration error: LFS variable '%s' not configured." % str(conf_key), status_code=500)
    return res

def _token_subject(op):
    '''
    Create a repository specific 'subject' for the token. This allows using the same
    django instance for different repositories (by only changing some environment variable
    between calls), and using a separate access token for each one.
    '''
    assert(op in ('download', 'upload'))
    configs_str = '%s\0%s\0%s' % (
        get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_DIR', required=False),
        get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_HTTP_URL_TEMPLATE_GET', required=False),
        get_env_or_django_conf('DJLFS_BATCH_LOCAL_STORAGE_HTTP_URL_TEMPLATE_PUT', required=False))
    return '%s-%s' % (op, hashlib.md5(configs_str.encode()).hexdigest()[:8])

def make_token(op, valid_secs=60*60*24):
    payload = {'sub': _token_subject(op), 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}
    return jwt.encode(payload, settings.SECRET_KEY).decode('ascii')

def verify_token(request, op):
    assert(op in ('download', 'upload'))
    try:
        token = request.META['HTTP_LFS_BATCH_TOKEN']
        payload = jwt.decode(token, settings.SECRET_KEY)
        if payload['sub'] != _token_subject(op):
            raise LfsError('Mismatching token subject (was %s, expected %s)' % (str(payload['sub']), str(op)), status_code=401)
    except KeyError as e:
        raise LfsError('Auth token missing', status_code=401)
    except jwt.ExpiredSignatureError as e:
        raise LfsError('Token expired: %s)' % str(e), status_code=401)
    except jwt.exceptions.InvalidTokenError as e:
        raise LfsError('Invalid token: %s)' % str(e), status_code=401)
