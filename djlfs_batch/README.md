# Django app "djlfs_batch"

This is a Git LFS _batch API_ server app for Django.

## Quick start

1. Add the app to your INSTALLED_APPS setting like this
```
    INSTALLED_APPS = [
        ...
        'djlfs_batch',
    ]
```
2. Include the URLconf in your project urls.py like this
```
    url(r'^info/lfs/', include('djlfs_batch.urls'), name='lfs_batch'),
```

3. Set Git LFS URL to `http://127.0.0.1:8000/lfs/info` and try to push some large files.
