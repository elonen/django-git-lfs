# DJLFS – Git LFS (batch API) implementation in Django

This is a Django implementation of Git LFS server. It supports basic upload / download through the _batch API_.

## Quick start

1. Install Python 3 (including `pyvenv` command)
2. Run `./setup_and_run.sh`
3. If the server starts ok, open a new shell (or hit Ctrl-Z and put it in background with `bg`)
4. Run `./test_git_lfs.sh` to test upload and download with git LFS client

## Installation

(TBD - how to make this work nice with Apache)

## Features

* Batch server only needs a directory for storing files, **no database**
* By design **no authentication or HTTPS** – this is intended as a web server backend

## Implementation status

* Batch API works and can be used as a LFS backend.
* Locking API is not (yet?) implemented

This is a fork of https://github.com/ddanier/django-git-lfs , but I'm probably going to *remove all auth code*. My plan is to make this a functional LFS backend for an environment where Apache / Nginx is doing all the authentication (for multiple repositories).

## LFS specs

See:

* https://github.com/blog/1986-announcing-git-large-file-storage-lfs
* https://github.com/github/git-lfs
* https://github.com/github/git-lfs/blob/master/docs/api.md
