# -*- coding: utf-8 -*-
from django import template
register = template.Library()
from participants.models import Library
from django.core.cache import cache

@register.simple_tag
def org_by_id(org_id):

    org_info = cache.get(str(org_id), None)
    if org_info:
        return org_info


    org_info = {'code':'', 'name':'', 'type':''}
    print org_id, '19217020'

    try:
        library = Library.objects.get(code=org_id)
        print library
        org_info['code'] = library.code
        org_info['name'] = library.name
        if library.is_root_node():
            org_info['type'] = 'library_system'
        else:
            org_info['type'] = 'library'
    except Library.DoesNotExist:
        org_info = {'code':org_id, 'name':org_id, 'type':None}
    cache.set(str(org_id), org_info)
    return org_info