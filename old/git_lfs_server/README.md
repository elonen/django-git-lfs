# Django app "git_lfs_server"

This is a Git LFS server app for Django.

## Quick start

1. Add the app to your INSTALLED_APPS setting like this
```
    INSTALLED_APPS = [
        ...
        'git_lfs_server',
    ]
```
2. Include the URLconf in your project urls.py like this
```
    url(r'^lfs/info/', include('git_lfs_server.urls')),
```

3. Run `python manage.py migrate` to create the models.

4. Set Git LFS URL to `http://127.0.0.1:8000/lfs/info` and try to push some large files.