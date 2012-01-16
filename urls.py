# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from orders.views import index
from django.contrib import admin
from django.contrib.auth.views import login, logout
from ldaccounts.views import login
admin.autodiscover()

from pages.views import show_main

def redirect(request):
    return  HttpResponseRedirect('http://old.ksob.spb.ru/cgi-bin/zgate?'+request.META['QUERY_STRING'])

urlpatterns = patterns('',
    (r'^cgi-bin/zgate/$', redirect),
    url(r'^$',include('site_index.urls'), name="site_index"),
    (r'^zgate/', include('zgate.urls')),
    (r'^orders/', include('orders.urls')),
    (r'^gallery/', include('gallery.urls')),
    (r'^news/', include('news.urls')),
    (r'^events/', include('events.urls')),
    (r'^pages/', include('pages.urls')),
    (r'^administration/', include('administration.urls')),
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^accounts/login/$',  login, name="accounts_login"),
    url(r'^accounts/logout/$',  logout, name="accounts_logout"),
    (r'^participants/', include('participants.urls')),
    (r'^feedbacks/', include('guestbook.urls')),
    (r'^polls/', include('polls.urls')),
    (r'^professional/', include('professional.urls')),
    (r'^reginlib/', include('reginlib.urls')),
    (r'^api/', include('api.urls')),
#    (r'^searcher/', include('searcher.urls')),

    (r'^captcha/', include('captcha.urls')),
        
    (r'^accounts/', include('ldaccounts.urls')),
    (r'^admin/', include(admin.site.urls)),
    #url(r'^admin/$',  include(admin.site.urls), name="admin_index"),
#    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
#            {'document_root': settings.MEDIA_ROOT}),
)
