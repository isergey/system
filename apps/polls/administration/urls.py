# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.polls.administration.views',
    url(r'^$', 'index', name="administration_polls_index"),
    url(r'^create$', 'create', name="administration_polls_create"),
    url(r'^edit/(?P<poll_id>\d+)/$', 'edit', name="administration_polls_edit"),
    url(r'^delete/(?P<poll_id>\d+)/$', 'delete', name="administration_polls_delete"),

    url(r'^view/(?P<poll_id>\d+)/$', 'view', name="administration_polls_view"),
    url(r'^create/choice/(?P<poll_id>\d+)/$', 'create_choice', name="administration_polls_create_choice"),
    url(r'^edit/choice/(?P<choice_id>\d+)/$', 'edit_choice', name="administration_polls_edit_choice"),
    url(r'^delete/choice/(?P<choice_id>\d+)/$', 'delete_choice', name="administration_polls_delete_choice"),

)