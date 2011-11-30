# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('guestbook.views',
    url(r'^$', 'index', name="guestbook_index"),
    url(r'^add/$', 'add_feedback', name="guestbook_add_feedback"),
    #url(r'^(?P<news_id>\d+)/$', 'show', name="news_show"),
    #url(r'^create/$', 'create', name="news_create"),
    #url(r'^(?P<news_id>\d+)/edit/$','edit', name="news_edit"),
    #url(r'^(?P<news_id>\d+)/delete/$','edit', name="news_delete"),
)

