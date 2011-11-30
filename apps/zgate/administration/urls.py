# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.zgate.administration.views',
    url(r'^$', 'index', name="administration_zgate_index"),
    url(r'^create$', 'create', name="administration_zgate_create"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="administration_zgate_edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="administration_zgate_delete"),
)

