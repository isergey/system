# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.events.administration.views',
    url(r'^$', 'index', name="administration_events_index"),
    url(r'^create$', 'create', name="administration_events_create"),
    url(r'^edit/(?P<event_id>\d+)/$', 'edit', name="administration_events_edit"),
    url(r'^delete/(?P<event_id>\d+)/$', 'delete', name="administration_events_delete"),
)

