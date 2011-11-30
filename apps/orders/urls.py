# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('orders.views',
    url(r'^$', 'index', name="orders_index"),
    url(r'^delete/(?P<order_id>[a-z0-9]+)/$', 'delete_order', name="orders_delete"),
    url(r'^makeorder/$', 'make_order', name="orders_make_order"),
    url(r'^orgbydistrict/$', 'org_by_district', name="orders_orgbydistrict"),
    url(r'^orgbycode/$', 'org_by_code', name="orders_orgbycode"),
    url(r'^(?P<order_type>[a-z]+)/$', 'order', name="orders_order"),
    url(r'^(?P<order_type>[a-z]+)/(?P<org_id>\d+)/$', 'order', name="orders_reserv"),

    #url(r'^(?P<news_id>\d+)/$', 'show', name="news_show"),
    #url(r'^create/$', 'create', name="news_create"),
    #url(r'^(?P<news_id>\d+)/edit/$','edit', name="news_edit"),
    #url(r'^(?P<news_id>\d+)/delete/$','edit', name="news_delete"),
)

