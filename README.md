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

### OPTION 2: Run test with WSGI / Apache 2.4 using Vagrant

1. Install Vagrant
2. `cd wsgi-test && vagrant up`
3. Open http://127.0.0.1:8000/ in a browser. You should see Debian/Apache default "It worked!" page (served from inside Vagrant VM).
4. `cd.. ; ./test_git_lfs.sh http://127.0.0.1:8000/repo1`

You can repeat the last step for `repo2` and `repo3` if you wish – the included server configuration supports multiple repositories, and stores their large files in separate directories. Do `vagrant ssh` from _wsgi-test_ directory, and look in `/opt/`.

## Features

* Batch server only needs a directory for storing files, **no database**
* By design, **no authentication or HTTPS** – this is intended as a web server backend with auth handled by HTTPD

## Installing on Apache

See `wsgi-test/vagrant_bootstrap.sh` to see how to set up the server from scratch on a vanilla Debian Stretch (with _git-lfs_ package picked from Buster). Then see `wsgi-test/lfs_example_apache_site.conf` for an example configuration file for Apache 2.4.

They set up a Git for multiple repositories over HTTP (Apache) as well as the LFS server, but you can fully well omit it and only use the LFS server if you wish.

## Implementation status

* Batch API works and can be used as an LFS server
* Locking API is not implemented, at least yet

This is a fork of https://github.com/ddanier/django-git-lfs , but I'm most likely going to *remove all auth code*.

## Contributing

Pull requests and issues are welcome.

## LFS specs

See:

* https://github.com/blog/1986-announcing-git-large-file-storage-lfs
* https://github.com/github/git-lfs
* https://github.com/github/git-lfs/blob/master/docs/api.md
