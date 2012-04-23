from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('administrator.views',
    url(r'^create_degree', 'create_degree'),
    url(r'^edit_degree', 'edit_degree'),
    url(r'^create_admin', 'create_admin'),
)
