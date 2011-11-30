# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('filebrowser.views',
    url(r'^$', 'index', name="filebrowser_index"),
)