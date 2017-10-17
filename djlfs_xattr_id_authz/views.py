from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.shortcuts import render

import logging
logger = logging.getLogger(__name__)

import posix1e
import string
import grp
import re, os
from subprocess import Popen, PIPE

def _do_check_acl(filename, username):
  '''
  Check which ACLs given user has for given file.

  @param filename       Absolute path to file to read ACL from
  @param username       Username to check ACL against
  '''

  # Get ACL and traditional group lists for the file
  file_acl = posix1e.ACL(file=filename)
  stat_info = os.stat(filename)
  unix_group = grp.getgrgid(stat_info.st_gid).gr_name

  # Sanitize username before invoking shell
  valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
  username = ''.join(c for c in username if c in valid_chars)

  # List user's groups with 'id' command
  p = Popen(["id", "-n", "-G", "-z", username], stdin=PIPE, stdout=PIPE, stderr=PIPE)
  output, err = p.communicate(b'')
  if b'no such user' in err:
    raise Exception('No such user: %s' % str(username))
  elif p.returncode != 0:
    raise Exception('Non-zero returncode from "id" command.')
  user_groups = output.decode('utf-8').split('\0')

  # Walk through file's ACLs and compare to user's
  can_read = False
  can_write = False

  for l in [s.strip() for s in str(file_acl).splitlines()]:
    group = None
    perm = ''

    # Handle other ("everyone")
    if l[0:7] == 'other::':
      parts = l.split(':')
      perm = parts[2]

    # Handle actual group memberships
    elif l[0:6] == 'group:':
      parts = l.split(':')
      group = parts[1]

      # Check default unix group in addition to ACLs
      if group == '':
        group = unix_group

      if group in user_groups:
        perm = parts[2]

    can_write = can_write or ('w' in perm)
    can_read = can_read or ('r' in perm)

  return {'r':can_read, 'w':can_write}


# Create your views here.
@csrf_exempt
def check_acl(request, method, username, filepath):

    # Validate username
    valid_username = re.compile("^[a-zA-Z0-9 @._-]+$")
    if not valid_username.match(str(username)):
        raise SuspiciousOperation("Unacceptable username: '%s'" % str(username))

    filepath = '/' + filepath

    try:
        perms = _do_check_acl(filepath, username)
        logger.info('check_acl() on "%s" for user "%s" = %s' % (str(filepath), str(username), str(perms)))
    except Exception as e:
        logger.error('Failed to check ACL for user "%s" on path: "%s": %s' % (str(username), str(filepath), str(e)))
        return HttpResponse('ACL check failed: %s' % str(e), status=403)

    # Depending on HTTP method, check either read or write permissions
    read_methods = ('OPTIONS', 'PROPFIND', 'GET', 'REPORT', 'HEAD')
    write_methods = ('MKACTIVITY', 'PROPPATCH', 'PUT', 'POST', 'CHECKOUT', 'MKCOL', 'MOVE', 'COPY', 'DELETE', 'LOCK', 'UNLOCK', 'MERGE', 'PATCH')

    if (perms['r'] and (method.upper() in read_methods)) or (perms['w'] and (method.upper() in write_methods)):
        return HttpResponse('OK %s' % str(perms), status=200)

    if (method not in write_methods) and (method not in read_methods):
        logger.warning('check_acl() UNSUPPORTED METHOD: %s (USER=%s FILEPATH=%s)' % (method, username, filepath))
        return HttpResponse('405 Method not allowed: %s' % method, status=405)

    msg = '403 Forbidden: check_acl() DENIED: USER=%s PATH=%s METHOD=%s PERMS=%s' % (username, filepath, method, str(perms))
    logger.info(msg)

    # Ugly hack: posing error message as an invalid XML element was the only way I could
    # persuade Svn client to actually show it:
    if method not in ('GET', 'POST'):
        msg = '<?xml version="1.0" encoding="utf-8" ?><%s/>' % (re.sub('[^a-zA-Z0-9_.-]', '_', msg))

    return HttpResponse('403 Forbidden: %s' % str(msg), status=403)
