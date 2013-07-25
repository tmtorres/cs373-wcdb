try:
    from django.conf.urls import patterns, include, url
except ImportError: # django < 1.4
    from django.conf.urls.defaults import patterns, include, url

from django.views.static import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wcdb.views.home', name='home'),
    # url(r'^wcdb/', include('wcdb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', 'database.views.utility', name='utility'),
    url(r'^import/$', 'database.views.upload'),
    url(r'^export/$', 'database.views.download'),
    url(r'^test/$', 'database.views.test', name='test'),
    url(r'^results/$', 'database.views.results'),
)
