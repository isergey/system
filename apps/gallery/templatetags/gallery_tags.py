# -*- coding: utf-8 -*-
import random
from django.conf import settings
from django import template
from apps.gallery.models import  Collection, CollectionImage
register = template.Library()

@register.inclusion_tag('gallery/tags/tag_index_gallery.html')
def index_gallery():
    try:
        collection = Collection.objects.get(latin_title='index')
    except Collection.DoesNotExist:
        return {}

    images = CollectionImage.objects.filter(collection=collection)
    images_dir = settings.GALLERY['public_path']+str(collection.id)+'/'
    thumbinails_dir =  images_dir + 'thumbinails/'
    return {'collection': collection,
            'images': images,
            'images_dir': images_dir,
            'thumbinails_dir': thumbinails_dir,
    }

@register.inclusion_tag('gallery/tags/gallery_preview.html')
def gallery_preview(collection):
    try:
        collection = Collection.objects.get(id=collection)
    except Collection.DoesNotExist:
        return {}
    images = CollectionImage.objects.filter(collection=collection)
    items = range(len(images))
    random.shuffle(items)
    previews = []
    for item in items[:5]:
        previews.append(images[item])

    images_dir = settings.GALLERY['public_path']+str(collection.id)+'/'
    thumbinails_dir =  images_dir + 'thumbinails/'
    return {'collection': collection,
            'images': previews,
            'images_dir': images_dir,
            'thumbinails_dir': thumbinails_dir,
            }