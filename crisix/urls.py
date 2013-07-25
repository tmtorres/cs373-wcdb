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
    url(r'^$', 'crisix.views.index', name='index'),
    #url(r'^$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^people/(?P<id>\w{6})/$', 'crisix.views.people'),
    url(r'^crises/(?P<id>\w{6})/$', 'crisix.views.crises'),
    url(r'^organizations/(?P<id>\w{6})/$', 'crisix.views.organizations'),
    url(r'^utility/', include('database.urls')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
