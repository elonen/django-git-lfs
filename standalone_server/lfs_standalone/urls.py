from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    #url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^info/lfs/', include('djlfs_batch.urls'), name='lfs_batch'),
    url(r'^xattr_authz/', include('djlfs_xattr_id_authz.urls'), name='xattr_authz'),
    
    #url(r'^info/lfs/', include('git_lfs_server.urls'), name='lfs'),
]
