from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('administrator.views',
    url(r'^new_degree', 'new_degree'),
    url(r'^open_degree', 'open_degree'),
    url(r'^edit_degree/(?P<id>\d+)', 'edit_degree'),
    url(r'^create_admin', 'create_admin'),
)
