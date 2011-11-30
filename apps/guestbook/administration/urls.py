# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.guestbook.administration.views',
    url(r'^$', 'index', name="administration_guestbook_index"),
    url(r'^edit/(?P<message_id>\d+)/$', 'edit', name="administration_guestbook_message_edit"),
    url(r'^delete/(?P<message_id>\d+)/$', 'delete', name="administration_guestbook_message_delete"),
)