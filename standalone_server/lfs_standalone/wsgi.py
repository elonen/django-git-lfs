"""
WSGI config for lfs_standalone project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lfs_standalone.settings")

_application = get_wsgi_application()

def application(environ, start_response):
    # pass the WSGI environment variables on through to os.environ    
    for var, val in environ.items():
        if 'DJLFS_' in var:
            os.environ[var] = val
    return _application(environ, start_response)
