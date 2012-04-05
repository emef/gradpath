from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('student.views',
    url(r'^$', 'progress'),
    url(r'^courses/manage/', 'courses_manage'),
    url(r'^courses/list/', 'courses_list'),                       
    url(r'^degrees/manage/', 'degrees_manage'),
    url(r'^degrees/list/', 'degrees_list'),                       
    url(r'^transcript/import', 'transcript_import'),
    url(r'^transcript/submit', 'transcript_submit'),
)
