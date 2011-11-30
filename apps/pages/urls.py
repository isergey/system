# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('pages.views',
    url(r'^$', 'index', name="pages_index"),

    url(r'^(?P<page_id>\d+)/$', 'show', name="pages_show"),
    url(r'^s/(?P<slug>[-_\w]+)/$', 'show', name="pages_show_slug"),
    #url(r'^create/$', 'create', name="news_create"),
    #url(r'^(?P<news_id>\d+)/edit/$','edit', name="news_edit"),
    #url(r'^(?P<news_id>\d+)/delete/$','edit', name="news_delete"),
)

