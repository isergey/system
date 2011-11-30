# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.news.administration.views',
    url(r'^$', 'index', name="administration_news_index"),
    url(r'^create$', 'create', name="administration_news_create"),
    url(r'^edit/(?P<news_id>\d+)/$', 'edit', name="administration_news_edit"),
    url(r'^delete/(?P<news_id>\d+)/$', 'delete', name="administration_news_delete"),

    url(r'^type/(?P<type>\w+)/$', 'index', name="administration_news_by_type"),
)