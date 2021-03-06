from django.views.generic.simple import direct_to_template, redirect_to
from django.conf.urls.defaults import patterns, include, url

from emailr.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
#    url(r'^render/', testRender),
    url(r'^$', index),   
    url(r'^learn/$', learn),
    url(r'^home/', home),

    url(r'^signup/$', signup),
    url(r'^register/$', register),

    url(r'login/', login),
    url(r'logout/$', logout),

    url(r'^receiveEmail/$', receiveEmail),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
