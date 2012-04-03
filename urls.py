from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

STATIC_DIR = settings.STATIC_ROOT

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'courses.views.home'),
    url(r'user/', include('profiles.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    #Static files
    url(r'^css/(?P<path>.+)$', 'django.views.static.serve', {'document_root': '%s/css' % STATIC_DIR}),
    url(r'^img/(?P<path>.+)$', 'django.views.static.serve', {'document_root': '%s/img' % STATIC_DIR}),
    url(r'^js/(?P<path>.+)$', 'django.views.static.serve', {'document_root': '%s/js' % STATIC_DIR}),
)
