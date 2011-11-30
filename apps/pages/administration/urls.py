# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.pages.administration.views',
    url(r'^$', 'index', name="administration_pages_index"),
    url(r'^create$', 'create', name="administration_pages_create"),
    url(r'^edit/(?P<page_id>\d+)/$', 'edit', name="administration_pages_edit"),
    url(r'^delete/(?P<page_id>\d+)/$', 'delete', name="administration_pages_delete"),
)

