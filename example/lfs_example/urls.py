from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'lfs_example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^info/lfs/', include('djlfs_batch.urls'), name='lfs_batch'),
    #url(r'^info/lfs/', include('git_lfs_server.urls'), name='lfs'),
]
