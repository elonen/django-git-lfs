# Django app "djlfs_xattr_id_authz"

This is a generic file authorization (not authentication!) app for Django, mainly for use with NGINX.

It provides an HTTP handler that checks given Unix username's groups (with `id` command) against given path's file permissions (traditional and facl), and returns either 200 (OK) or 403 (Forbidden), depending on wether or not the given user has read and/or write access. The groups can be anything local Unix groups or, for example, Windows Domain groups if the server has Winbind talking to a domain controller.

The app is designed to be used with the `auth_request` feature of NGINX.

Example request: /xattr_auth/method/*POST*/user/*some.username*/path/*some/absolute/path*

This will return status 200 if any of the groups returned by Unix command `id some.user` has write permissions to `/some/absolute/path`. If the method had been `GET` (instead of `POST`), read permissions on `/some/absolute/path` would have sufficed.

The app itself does not keep any authorization cache, but you can boost performance significantly by applying an NGINX proxy cache on the authorization URI. This is especially effective if you are making many subsequent requests and can check base directory instead of individial files (e.g. have set group sticky bit to a Git repository dir, so you know that all files inside it will have the same permissions).

## Installation

1. Add the app to your INSTALLED_APPS setting like this
```
    INSTALLED_APPS = [
        ...
        'djlfs_xattr_id_authz',
    ]
```
2. Include the URLconf in your project urls.py like this
```
    url(r'^xattr_auth/', include('djlfs_xattr_id_authz.urls'), name='xattr_id_authz'),
```

3. Install the _pylibacl_ package (also listed in requirements.txt). The app uses posix1e module from it to read file permissions.

4. Configure NGINX to check authorization with the `auth_request` keyword. How exactly to do this depends on your specific environment, but you'll probably want to deduce the accessed file/directory from `$request_uri`, and then use it and `$remote_user` to build an handler authz handler.
