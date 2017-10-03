import os, re
from django.http import JsonResponse
import django.conf
import lfs_example

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
    res = os.environ.get(conf_key) or lfs_example.settings.__dict__.get(conf_key)
    if not res and required:
        raise LfsError("Configuration error: LFS variable '%s' not configured." % str(conf_key), status_code=500)
    return res
