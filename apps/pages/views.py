# -*- coding: utf-8 -*-
from django.http import    HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt

from guardian.core import ObjectPermissionChecker
from models import Page


def index(request):
    pages_list = Page.objects.all()
    return direct_to_template(request, 'pages/pages_list.html',
                              {'pages_list': pages_list,
                               'active_pages':True})


def show(request, page_id='',slug=''):
    if page_id:
        page = get_object_or_404(Page, id=page_id)
    if slug:
        page = get_object_or_404(Page, latin_title=slug)

    checker = ObjectPermissionChecker(request.user)

    if not checker.has_perm('pages.view_page', page):
        return HttpResponseForbidden()

    return direct_to_template(request, 'pages/page_show.html',
                              {'page': page,
                               'active_page_id':page_id})


def show_main(request):
    return show(request,slug='index')
