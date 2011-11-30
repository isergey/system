# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.gallery.administration.views',
    url(r'^$', 'index', name="administration_gallery_index"),
    url(r'^create/$', 'create_collection', name="administration_gallery_create"),
    url(r'^(?P<collection_id>\d+)/$', 'view_collection', name="administration_gallery_view"),
    url(r'^upload/(?P<collection_id>\d+)/$', 'upload', name="administration_gallery_upload"),
    url(r'^(?P<collection_id>\d+)/delete/$', 'delete_collection', name="administration_gallery_delete_collection"),
    url(r'^delete/image/(?P<image_id>\d+)/$', 'delete_image', name="administration_gallery_delete_image"),
    url(r'^edit/image/(?P<image_id>\d+)/$', 'edit_image', name="administration_gallery_edit_image"),
    url(r'^edit/collection/(?P<collection_id>\d+)/$', 'edit_collection', name="administration_gallery_edit_collection"),
)