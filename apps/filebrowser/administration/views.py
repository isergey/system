# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils.http import urlquote
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403

from forms import UploadFileForm

import os
import datetime
import shutil

mtypes = {
    'gif': 'image',
    'jpg': 'image',
    'png': 'image',
    'pdf': 'pdf',
    'doc': 'doc',
    'xls': 'xsl',
    }


def chek_or_create_dir(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path, 0755)
        except Exception as e:
            return False

    return True


def get_mtype(file_name):
    file_name_ext = file_name.split('.')

    if len(file_name_ext) > 1 and file_name_ext[1] in mtypes:
        return mtypes[file_name_ext[1]]

    return 'file'


def get_file_map(path, show_path_url, show_path):
    file_name = os.path.basename(path)
    item_map = {}

    item_map['type'] = 'file'
    item_map['mtype'] = get_mtype(file_name)
    item_map['name'] = file_name

    file_stat = os.stat(path)
    size = file_stat.st_size / 1024
    if size < 1:
        item_map['size'] = {
            'bytes': file_stat.st_size,
            'title': u'bytes'
        }
    else:
        item_map['size'] = {
            'bytes': size,
            'title': u'Kbytes'
        }

    item_map['create_time'] = datetime.datetime.fromtimestamp(file_stat.st_ctime)
    item_map['url'] = show_path_url + '/' + file_name
    item_map['work_url'] = show_path + '/' + file_name
    return item_map


def get_dir_map(path, show_path):
    dir_name = os.path.basename(path)
    item_map = {}

    item_map['type'] = 'dir'
    item_map['mtype'] = 'dir'
    item_map['name'] = dir_name

    dir_stat = os.stat(path)

    item_map['size'] = {
        'bytes': 0,
        'title': u'bytes'
    }

    item_map['create_time'] = datetime.datetime.fromtimestamp(dir_stat.st_ctime)
    item_map['url'] = show_path + '/' + dir_name
    return item_map


def handle_uploaded_file(f, path):
    destination = open(path + '/' + f.name, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return f.name


@login_required
def index(request):
    base_uplod_path = settings.FILEBROWSER['upload_dir']

    show_path = '' # root of upload path
    show_path_url = settings.FILEBROWSER['upload_dir_url']

    if 'path' in request.GET:
        path = request.GET['path'].strip('/')
        if '..' in path or '/.' in path:
            raise Http404(u"Path not founded")

        show_path = '/%s' % path

    show_path_url += show_path

    if not chek_or_create_dir(base_uplod_path):
        return HttpResponse(u"Catalog '%s' can't be created" % show_path)

    if not os.path.isdir(base_uplod_path + show_path):
        raise Http404(u"Path not founded")

    dir_items = os.listdir(base_uplod_path + show_path)

    dir_map = []
    for dir_item in dir_items:
        path_to_dir_item = base_uplod_path + show_path + '/' + dir_item

        if os.path.isfile(path_to_dir_item):
            dir_map.append(get_file_map(path_to_dir_item, show_path_url, show_path))

        elif os.path.isdir(path_to_dir_item):
            dir_map.append(get_dir_map(path_to_dir_item, show_path))

        # не выводим элемент
        else: continue

    breadcrumbs = []
    path_dirs = show_path.strip('/').split('/')
    breadcrumbs.append({
        'title': '/',
        'url': '/',
        })
    for i, path_dir in enumerate(path_dirs):
        breadcrumbs.append({
            'title': path_dir,
            'url': '/' + '/'.join(path_dirs[:i + 1]),
            })

    upload_form = UploadFileForm(initial={'path': show_path})

    dir_map = sorted(dir_map, key=lambda x: x['create_time'], cmp=lambda x, y: cmp(x, y), reverse=True)
    dir_map = sorted(dir_map, key=lambda x: x['type'], cmp=lambda x, y: cmp(x.lower(), y.lower()))

    return direct_to_template(request, 'filebrowser/administration/list.html', {
        'dir_map': dir_map,
        'breadcrumbs': breadcrumbs,
        'upload_form': upload_form,
        'active_module': 'filebrowser'
    })


@login_required
def delete(request):
    base_uplod_path = settings.FILEBROWSER['upload_dir']

    show_path = '' # root of upload path
    show_path_url = settings.FILEBROWSER['upload_dir_url']

    current_dir = '/'
    if 'path' in request.GET:
        path = request.GET['path'].strip('/')
        if '..' in path or '/.' in path:
            raise Http404(u"Path not founded")

        delete_path = '/%s' % path
        current_dir = os.path.split(delete_path)[0]

        delete_path = base_uplod_path + delete_path

        if os.path.isfile(delete_path):
            os.remove(delete_path)
        if os.path.isdir(delete_path):
            shutil.rmtree(delete_path)

    return HttpResponseRedirect(reverse('administration_filebrowser_index') + '?path=' + current_dir)


@login_required
def upload(request):
    path = '/'
    base_uplod_path = settings.FILEBROWSER['upload_dir']
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            path = form.cleaned_data['path']
            upload_path = base_uplod_path + path
            if not os.path.isdir(upload_path):
                raise Http404(u"Path not founded")

            handle_uploaded_file(f=request.FILES['file'], path=upload_path)

    return HttpResponseRedirect(reverse('administration_filebrowser_index') + '?path=' + path)