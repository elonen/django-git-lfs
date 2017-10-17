from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'method/(?P<method>[a-zA-Z]+)/user/(?P<username>[a-zA-Z0-9 @._-]+)/path/(?P<filepath>.*)$', views.check_acl, name='check_acl')
]
