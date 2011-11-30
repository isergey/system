# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('site_index.views',
    url(r'^$', 'index', name="site_index"),
)

