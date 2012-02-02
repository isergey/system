# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('events.views',
    url(r'^$', 'index', name="events_index"),
    url(r'^date/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'filer_by_date', name="events_by_date"),
    url(r'^(?P<event_id>\d+)/$', 'show', name="events_show"),
    url(r'^comment/(?P<event_id>\d+)/$', 'comment_event', name="events_comment"),
    url(r'^calendar/$', 'calendar', name="events_calendar"),
    url(r'^favorits/$', 'favorits', name="events_favorits"),
    url(r'^favorits/(?P<event_id>\d+)/$', 'favorits_detail', name="events_favorits_detail"),
    url(r'^favorits/add/(?P<event_id>\d+)/$', 'add_to_favorits', name="events_add_to_favorits"),
    url(r'^search/$', 'search', name="events_search"),
    url(r'^insert/$', 'insert', name="events_insert"),
    #url(r'^create/$', 'create', name="news_create"),
    #url(r'^(?P<news_id>\d+)/edit/$','edit', name="news_edit"),
    #url(r'^(?P<news_id>\d+)/delete/$','edit', name="news_delete"),
)

