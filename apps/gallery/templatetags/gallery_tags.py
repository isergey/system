# -*- coding: utf-8 -*-
from django.conf import settings
from django import template
from apps.gallery.models import  Collection, CollectionImage
register = template.Library()

@register.inclusion_tag('gallery/tag_index_gallery.html')
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
