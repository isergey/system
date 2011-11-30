# -*- coding: utf-8 -*-
from django import template
register = template.Library()
from participants.models import Library, LibrarySystem
from django.core.cache import cache

@register.simple_tag
def org_by_id(org_id):

    org_info = cache.get(str(org_id), None)
    if org_info:
        return org_info


    org_info = {'code':'', 'name':'', 'type':''}

    try:
        library = Library.objects.get(code=org_id)
        org_info['code'] = library.code
        org_info['name'] = library.name
        org_info['type'] = 'library'
    except Library.DoesNotExist:
        try:
            library_system = LibrarySystem.objects.get(code=org_id)
            org_info['code'] = library_system.code
            org_info['name'] = library_system.name
            org_info['type'] = 'library_system'
        except Library.DoesNotExist:
            return u'Организация с кодом %s не найдена' % unicode(org_id)
    cache.set(str(org_id), org_info)
    return org_info