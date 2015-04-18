from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^objects$', views.object_upload_init, name='lfs_object_upload_init'),
    url(r'^objects/upload$', views.object_upload, name='lfs_object_upload'),
    url(r'^objects/(?P<oid>[^/]+)$', views.object_meta, name='lfs_object_meta'),
    url(r'^objects/(?P<oid>[^/]+)/download$', views.object_download, name='lfs_object_download'),
    url(r'^objects/(?P<oid>[^/]+)/verify', views.object_verify, name='lfs_object_verify'),
]
