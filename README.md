# Django app git_lfs_server

This is a ~proof of concept~ simple but working git-lfs storage server implementation, see:

* https://github.com/blog/1986-announcing-git-large-file-storage-lfs
* https://github.com/github/git-lfs
* https://github.com/github/git-lfs/blob/master/docs/api.md

## Quick start

1. Install Python 3 (including `pyvenv` command)
2. Run ./setup_and_run.sh

## TODO, missing features

* Secure perms handler for adding new access tokens
* Returning the correct HTTP status codes for responses
* Tests and documentation
* Anything besides beeing a proof of concept ;-)

## Done

* Authentication
* Bind this to any real world usage -> See https://github.com/ddanier/gitolite-git-lfs

## Why a Django based implementation?

* Runs on many setups, with many webservers, with many databases, with many …
* Reusable app, so this may be part of some bigger project
* May use Django storage backends (Amazon S3, Dropbox, …), see https://www.djangopackages.com/grids/g/storage-backends/
* I personally like it :)
