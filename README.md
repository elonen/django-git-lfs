# DJLFS – Git LFS (batch API) implementation in Django

This is a Django implementation of Git LFS server. It supports basic upload / download through the _batch API_.

## Quick start

The easiest way to get rolling is running the automated tests. I'm developing on OSX, but Linux probably works just as well.

### OPTION 1: Run tests with local Git repository

1. Install Git LFS and Python 3 (including `pyvenv` command)
2. `./setup_and_run.sh`
3. If the server starts ok, open a new shell (or hit Ctrl-Z and put it in background with `bg`)
4. `./test_git_lfs.sh`

This option does a little more thorough tests than WSGI one, as it has direct access to the LFS storage dir it creates in `test_temp/lfs_storage_dir/tmp` (peek in after running the test to see how the files are stored). It only supports one repository, though.

### OPTION 2: Run test with NGINX + uWSGI using Vagrant

1. Install Vagrant
2. `cd wsgi-test && vagrant up`
3. Open https://127.0.0.1:44300/ in a browser and accept the self-signed test certificate. You should see Debian/NGINX default page (served from inside Vagrant VM).
4. `cd.. ; ./test_git_lfs.sh https://127.0.0.1:44300/git/repo1`

You can repeat the last step for `repo2` and `repo3` if you wish – the included server configuration supports multiple repositories, and stores their large files in separate directories. Do `vagrant ssh` from _wsgi-test_ directory, and look in `/opt/` to see what they look like.

## Features

* Batch server only needs a directory for storing files, **no database**
* By design, **no authentication, repository management or HTTPS** – this is intended as a web server backend with security mostly handled by HTTPD

## Installing on NGINX

See `wsgi-test/vagrant_bootstrap.sh` to see how to set up the server from scratch on a vanilla Debian Stretch (with _git-lfs_ package picked from Buster). Then see `wsgi-test/lfs_example_nginx_site` for an example configuration file.

The example sets up a Git server for multiple repositories over HTTP (NGINX + fastcgi + git-http-backend) as well as the LFS server, but you can fully well omit it, and only use the LFS server if you wish.

## Multiple repository support

The LFS batch server always thinks it's serving files to/from a single LFS repository. Separating them happens on HTTPD. See `wsgi-test/lfs_example_nginx_site` for an example. It extracts repository name from request URL and sets two environment variables before calling the Django app:

* `DJLFS_BATCH_LOCAL_STORAGE_DIR` – Directory where current LFS repository's content is stored. 
* `DJLFS_BATCH_LOCAL_STORAGE_HTTP_URL_TEMPLATE_GET` – An URL template to _GET_ LFS objects directly through NGINX, bypassing Django for superior performance. The NGINX configuration example shows how to make it efficiently block download attempts that aren't initiated by the LFS batch request.

## Checking user permissions (authorization)

Like authentication, authorization is also left to the HTTPD.

It sufficies to check permissions when the Git LFS client makes a POST to the batch initialization URI, `/info/lfs/objects/batch`. The batch initialization provides the client with a temporary stateless token (JWT), that oid GET and PUT handlers then check before allowing download or upload of LFS objects.

While the batch app knows nothing about authorization, there's an independent NGINX `auth_request` compatible authz handler app `djlfs_xattr_id_authz`, that can be used for this purpose. It checks Unix (or Winbind) groups against file permissions (traditional and FACL) on the server. It's completely separate from the LFS batch app, and can just as well be used for any other NGINX based HTTP file server application.

## Implementation status

* Batch API works and can be used as a Git LFS server.
* Locking API is not implemented, at least not yet. Unlike the upload / download API, locking will probably require a database.

This is originally a fork of https://github.com/ddanier/django-git-lfs , but will likely diverge fast.

## Contributing

Pull requests and issues are welcome.

## LFS specs

See:

* https://github.com/blog/1986-announcing-git-large-file-storage-lfs
* https://github.com/github/git-lfs
* https://github.com/github/git-lfs/blob/master/docs/api.md
