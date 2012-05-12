from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('student.views',
    url(r'^$', 'progress'),
    url(r'^courses/manage/', 'courses_manage'),
    url(r'^courses/list/', 'courses_list'),
    url(r'^courses/remove/', 'courses_remove'),
    url(r'^courses/in_section/(?P<id>\d+)/', 'courses_in_section'),
    url(r'^courses/add/(?P<id>\d*)', 'courses_add'),                     
    url(r'^degrees/manage/', 'degrees_manage'),
    url(r'^degrees/list/', 'degrees_list'),
    url(r'^degrees/remove/', 'degrees_remove'),
    url(r'^degrees/in_college/(?P<id>\d+)/', 'degrees_in_college'),
    url(r'^degrees/add/(?P<id>\d*)', 'degrees_add'),                      
    url(r'^transcript/import', 'transcript_import'),
    url(r'^transcript/submit', 'transcript_submit'),
)
