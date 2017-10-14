from django.conf.urls import url
from . import views

app_name = 'djlfs_batch'
urlpatterns = [
    url(r'^objects/batch$', views.batch_action_init, name='init'),
    url(r'^objects/put/(?P<oid>[^/]+)$', views.batch_upload, name='upload'),
    url(r'^objects/get/(?P<oid>[^/]+)$', views.batch_download, name='download'),
    url(r'^objects/check-token/(?P<op>download|upload)$', views.check_token, name='checktoken'),
    #url(r'^objects/verify/(?P<oid>[^/]+)$', views.batch_verify, name='djlfs_batch_verify'),
]
