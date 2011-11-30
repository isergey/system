# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('news.views',
    url(r'^$', 'index', name="news_index"),
    url(r'^(?P<news_id>\d+)/$', 'show', name="news_show"),
    #url(r'^create/$', 'create', name="news_create"),
    #url(r'^(?P<news_id>\d+)/edit/$','edit', name="news_edit"),
    #url(r'^(?P<news_id>\d+)/delete/$','edit', name="news_delete"),
)

