# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.filebrowser.administration.views',
    url(r'^$', 'index', name="administration_filebrowser_index"),
    url(r'^upload/$', 'upload', name="administration_filebrowser_upload"),
    url(r'^delete/$', 'delete', name="administration_filebrowser_delete"),
)