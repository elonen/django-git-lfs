# DJLFS -- Git LFS (batch API) implementation in Django

This is a Django implementation of Git LFS server. It supports basic upload / download through the _batch API_.

## Quick start

1. Install Python 3 (including `pyvenv` command)
2. Run `./setup_and_run.sh`
3. If the server starts ok, hit CTRL-Z and put it background with `bg`
4. Run `test_git_lfs.sh` to test upload and download with git LFS client

## Features

* Batch server requires no' 'database for basic upload / download, just a local directory for file storage.

## Implementation status

* Batch API works and can be used as a LTFS backend.
* Locking API is not yet implemented.

This is a fork of *ddanier/django-git-lfs*, but I'm probably going to *remove all auth code*. My plan is to make this a functional LFS backend for an environment where Apache / Nginx is doing all the authentication (for multiple repositories).

## LFS specs

See:

* https://github.com/blog/1986-announcing-git-large-file-storage-lfs
* https://github.com/github/git-lfs
* https://github.com/github/git-lfs/blob/master/docs/api.md
