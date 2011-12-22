# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('api.views',
    url(r'^auth/$', 'auth', name="api_auth"),
)

