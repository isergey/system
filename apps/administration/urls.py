# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('administration.views',
    url(r'^$', 'index', name="administration_index"),
    (r'^pages/', include('pages.administration.urls')),
    (r'^news/', include('news.administration.urls')),
    (r'^events/', include('events.administration.urls')),
    (r'^polls/', include('polls.administration.urls')),
    (r'^gallery/', include('gallery.administration.urls')),
    (r'^zgate/', include('zgate.administration.urls')),
    (r'^feedbacks/', include('guestbook.administration.urls')),
    (r'^professional/', include('professional.administration.urls')),
    (r'^filebrowser/', include('filebrowser.administration.urls')),
    #(r'^menus/', include('treemenus.administration.urls')),
)

