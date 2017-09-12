from django.conf.urls import patterns
from django.conf.urls import url

from horizon_openfoam.instances import views

INSTANCES = r'^(?P<instance_id>[^/]+)/%s$'
VIEW_MOD = 'horizon_openfoam.instances.views'

urlpatterns = patterns(
    VIEW_MOD,
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<instance_id>[^/]+)/$',
        views.DetailView.as_view(), name='detail'),
    url(INSTANCES % 'console', 'console', name='console'),
    url(INSTANCES % 'download', 'download', name='download'),
)
