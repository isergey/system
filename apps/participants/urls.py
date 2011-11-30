# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('participants.views',
    url(r'^$', 'index', name="participants_index"),
    url(r'^cbs/(?P<code>[a-zA-Z\d]+)/$', 'cbs_list', name="participants_cbs_detail"),

    url(r'^cbs/detail/(?P<code>[a-zA-Z\d]+)/$', 'detail_by_cbs', name="participants_detail_by_cbs"),
    url(r'^districts/detail/(?P<code>[a-zA-Z\d]+)/$', 'detail_by_district', name="participants_detail_by_district"),
    url(r'^districts/$', 'districts', name="participants_districts"),
    url(r'^districts/(?P<id>\d+)/$', 'by_district', name="participants_by_district"),
)

