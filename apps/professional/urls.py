# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('professional.views',
    url(r'^$', 'index', name="professional_index"),
    url(r'^news/(?P<news_id>\d+)/$', 'show_news', name="professional_show_news"),
)

