from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('profiles.views',
    url(r'^import', 'import_transcript'),
    url(r'^register', 'register'),
    url(r'^activate', 'activate'),
)
