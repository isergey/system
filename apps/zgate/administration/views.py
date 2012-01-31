# -*- coding: utf-8 -*-
import simplejson
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.urlresolvers import reverse
from guardian.decorators import permission_required_or_403
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from apps.zgate.models import ZCatalog
from forms import ZCatalogForm
from django.forms.models import model_to_dict

from common.access.shortcuts import assign_perm_for_groups_id, get_group_ids_for_object_perm, edit_group_perms_for_object

@permission_required_or_403('zgate.add_zcatalog')
def index(request):
    zcatalogs = ZCatalog.objects.all().order_by('-id')
    paginator = Paginator(zcatalogs, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        zcatalogs_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        zcatalogs_list = paginator.page(paginator.num_pages)

    return render(request, 'zgate/administration/zcatalogs_list.html', {
        'zcatalogs_list': zcatalogs_list,
        'active_module': 'zgate'
    })



@permission_required_or_403('zgate.add_zcatalog')
def create(request):
    if request.method == 'POST':
        form = ZCatalogForm(request.POST)
        if form.is_valid():
            catalog = form.save()
            view_catalog_groups_ids = form.cleaned_data['view_page_groups']
            assign_perm_for_groups_id('view_zcatalog', catalog, view_catalog_groups_ids)

            return HttpResponseRedirect(reverse('administration_zgate_index'))
    else:
        form = ZCatalogForm()

    return render(request, 'zgate/administration/zcatalog_create.html', {
        'form': form,
        'active_module': 'zgate'
    })



@permission_required_or_403('zgate.change_zcatalog')
def edit(request, id):
    zcatalog = get_object_or_404(ZCatalog, id=id)

    old_catalog_groups_ids = get_group_ids_for_object_perm(u'view_zcatalog', zcatalog)

    if request.method == 'POST':
        form = ZCatalogForm(request.POST, instance=zcatalog)
        if form.is_valid():
            catalog = form.save()
            new_catalog_groups_ids = form.cleaned_data['view_catalog_groups']
            edit_group_perms_for_object('view_zcatalog', catalog, old_catalog_groups_ids, new_catalog_groups_ids)
            return HttpResponseRedirect(reverse('administration_zgate_index'))
    else:
        init = model_to_dict(zcatalog)
        init['view_catalog_groups'] = old_catalog_groups_ids

        form = ZCatalogForm(init,instance=zcatalog)
    return render(request, 'zgate/administration/zcatalog_edit.html', {
        'form': form,
        'zcatalog':zcatalog,
        'active_module': 'zgate'
    })




@permission_required_or_403('zgate.delete_zcatalog')
def delete(request, id):
    zcatalog = get_object_or_404(ZCatalog, id=id)
    zcatalog.delete()
    return HttpResponseRedirect(reverse('administration_zgate_index'))


@permission_required_or_403('zgate.change_zcatalog')
def statistics(request, id):
    zcatalog = get_object_or_404(ZCatalog, id=id)
    rows = zcatalog.requests_by_day()
    js_rows =  simplejson.dumps(rows, ensure_ascii=False)
    return render(request, 'zgate/administration/zcatalog_statistics.html', {
        'zcatalog':zcatalog,
        'js_rows':js_rows,
        'active_module': 'zgate'
    })