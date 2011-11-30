# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('gallery.views',
    url(r'^$', 'index', name="gallery_index"),
    # страница загрузки изображения, указываем id коллекции
    url(r'^(?P<collection_id>\d+)/$', 'view_collection', name="gallery_view"),
    url(r'^s/(?P<slug>[-_\w]+)/$', 'view_collection', name="gallery_view_slug"),
)

