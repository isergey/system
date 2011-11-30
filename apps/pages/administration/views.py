# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from guardian.decorators import permission_required_or_403
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from apps.pages.models import Page
from forms import PageForm
from django.forms.models import model_to_dict
from common.access.shortcuts import assign_perm_for_groups_id, get_group_ids_for_object_perm, edit_group_perms_for_object

@permission_required_or_403('pages.add_page')
def index(request):
    pages = Page.objects.all().order_by('-create_date')
    paginator = Paginator(pages, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        pages_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pages_list = paginator.page(paginator.num_pages)
    return direct_to_template(request, 'pages/administration/pages_list.html',
                              {'pages_list': pages_list,
                               'active_module': 'pages'})


@permission_required_or_403('pages.add_page')
def create(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save()
            #page = get_object_or_404(Page, id=form.pk)

            view_page_groups_ids = form.cleaned_data['view_page_groups']

            assign_perm_for_groups_id('pages.view_page', page, view_page_groups_ids)

            return HttpResponseRedirect(reverse('administration_pages_index'))
    else:
        form = PageForm()

    return direct_to_template(request, 'pages/administration/pages_create.html',
                              {'form': form,
                               'groups'
                               'active_module': 'pages', })


@permission_required_or_403('pages.change_page')
def edit(request, page_id):

    page = get_object_or_404(Page, id=page_id)

    old_page_groups_ids = get_group_ids_for_object_perm(u'view_page', page)

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)

        if form.is_valid():
            page = form.save()
            new_page_groups_ids = form.cleaned_data['view_page_groups']
            edit_group_perms_for_object('view_page', page, old_page_groups_ids, new_page_groups_ids)
            return HttpResponseRedirect(reverse('administration_pages_index'))
    else:
        init = model_to_dict(page)
        init['view_page_groups'] = old_page_groups_ids
        form = PageForm(init, instance=page)
    return direct_to_template(request, 'pages/administration/pages_edit.html',
                              {'form': form,
                               'page': page,
                               'active_module': 'pages'})


@permission_required_or_403('pages.delete_page')
def delete(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    page.delete()
    return HttpResponseRedirect(reverse('administration_pages_index'))
