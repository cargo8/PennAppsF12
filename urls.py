from django.views.generic.simple import direct_to_template, redirect_to
from django.conf.urls.defaults import patterns, include, url

from emailr.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pennappsf12.views.home', name='home'),
    # url(r'^pennappsf12/', include('pennapps12.foo.urls')),

    # url(r'^$', direct_to_template, {'template': 'postcard.html'}),
    # url(r'^render/', renderEmail),

    url(r'^$', index),
    url(r'^signup/$', signup),
    url(r'receiveEmail/$', receiveEmail),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
