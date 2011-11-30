# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('polls.views',
    url(r'^$', 'index', name="polls_index"),
    url(r'^(?P<poll_id>\d+)/$', 'vote', name="polls_vote"),
    url(r'^(?P<poll_id>\d+)/results/$', 'results', name="polls_results"),
    #url(r'^create/$', 'create', name="news_create"),
    #url(r'^(?P<news_id>\d+)/edit/$','edit', name="news_edit"),
    #url(r'^(?P<news_id>\d+)/delete/$','edit', name="news_delete"),
)

