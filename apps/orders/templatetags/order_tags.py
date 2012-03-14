# -*- coding: utf-8 -*-
import hashlib
from django import template
register = template.Library()
from participants.models import Library
from django.core.cache import cache

@register.simple_tag
def org_by_id(org_id):
    hash_id = hashlib.md5(org_id.encode('utf-8')).hexdigest()
    org_info = cache.get(hash_id, None)
    if org_info:
        return org_info


    org_info = {
        'code':'',
        'name':'',
        'type':''
    }

    try:
        library = Library.objects.get(code=org_id)
        org_info['code'] = library.code
        org_info['name'] = library.name
        if library.is_root_node():
            org_info['type'] = 'library_system'
        else:
            org_info['type'] = 'library'
    except Library.DoesNotExist:
        org_info = {
            'code':org_id,
            'name':org_id,
            'type':None
        }
    cache.set(hash_id, org_info)
    return org_info