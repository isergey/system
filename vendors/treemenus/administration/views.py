# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage



from treemenus.models import Menu, MenuItem
from treemenus.administration.forms import MenuForm, MenuItemForm
def index(request):
    menus = Menu.objects.all().order_by('-id')
    paginator = Paginator(menus, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        menus_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        menus_list = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'treemenus/administration/menus_list.html',
                              {'menus_list': menus_list,
                               'active_module': 'menus'})

def create(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_menus_index'))
    else:
        form = MenuForm()

    return direct_to_template(request, 'treemenus/administration/menu_create.html',
                              {'form': form,
                               'active_module': 'menus'})

def create_item(request, menu_id):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_menus_index'))
    else:
        form = MenuForm()

    return direct_to_template(request, 'treemenus/administration/menu_create.html',
                              {'form': form,
                               'active_module': 'menus'})


def edit(request, id):
    zcatalog = get_object_or_404(ZCatalog, id=id)
    if request.method == 'POST':
        form = ZCatalogForm(request.POST, instance=zcatalog)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_zgate_index'))
    else:

        form = ZCatalogForm(model_to_dict(zcatalog),instance=zcatalog)
    return direct_to_template(request, 'zgate/administration/zcatalog_edit.html',
                              {'form': form,
                               'zcatalog':zcatalog,
                               'active_module': 'zgate'})

def delete(request, id):
    menu = get_object_or_404(Menu, id=id)
    menu.delete()
    return HttpResponseRedirect(reverse('administration_menus_index'))