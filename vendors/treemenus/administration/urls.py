# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('treemenus.administration.views',
    url(r'^$', 'index', name="administration_menus_index"),
    url(r'^create$', 'create', name="administration_menus_create"),
    url(r'^edit/(?P<id>\d+)/$', 'edit', name="administration_menus_edit"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="administration_menus_delete"),
)

