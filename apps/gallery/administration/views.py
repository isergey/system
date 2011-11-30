# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403

from apps.gallery.models import Collection, CollectionImage
from apps.gallery.administration.forms import CreateCollectionForm, UploadFileForm, EditImageForm

import uuid
import Image
import os
import binascii
import shutil

@login_required
@permission_required_or_403('events.add_collection')
def index(request):
    collections = Collection.objects.all().order_by('-add_date_time')
    paginator = Paginator(collections, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        collections_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        collections_list = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'gallery/administration/list.html',
                              {'collections_list': collections_list,
                               'active_module': 'gallery'})

#@permission_required_or_403('gallery.create_collection')
@login_required
@permission_required_or_403('events.add_collection')
def create_collection(request):
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_gallery_index'))
    else:
        form = CreateCollectionForm()
    return direct_to_template(request, 'gallery/administration/create.html',
                              {'form': form,
                               'active_module': 'gallery'})


#@permission_required_or_403('gallery.view_collection')
@login_required
@permission_required_or_403('events.add_collection')
def view_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    images = CollectionImage.objects.filter(collection=collection).order_by('-add_date_time')
    images_dir = settings.GALLERY['public_path']+str(collection_id)+'/'
    thumbinails_dir =  images_dir + 'thumbinails/'
    return direct_to_template(request, 'gallery/administration/view.html',
                              {'collection': collection,
                               'images':images,
                               'images_dir':images_dir,
                               'thumbinails_dir':thumbinails_dir,
                               'active_module': 'gallery'
                               })

#@permission_required_or_403('gallery.edit_collection')
@login_required
@permission_required_or_403('events.add_collection')
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_gallery_index'))
    else:

        form = CreateCollectionForm(model_to_dict(collection),instance=collection)
    return direct_to_template(request, 'gallery/administration/edit.html',
                              {'form': form,
                               'collection':collection,
                               'active_module': 'gallery'})

#@permission_required_or_403('gallery.upload_image')
@login_required
@permission_required_or_403('events.add_collectionimage')
def upload(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            image_file_name = handle_uploaded_file(request.FILES['file'], collection_id)
            if image_file_name:
                image = CollectionImage(collection=collection,
                              title=form.cleaned_data['title'],
                              comments=form.cleaned_data['comments'])
                image.file_name = image_file_name
                image.save()
            return HttpResponseRedirect(reverse('administration_gallery_view', args=[collection_id]))
    else:
        form = UploadFileForm()
    return direct_to_template(request, 'gallery/administration/upload.html',
                              {'form': form,
                               'collection': collection,
                               'active_module': 'gallery'})




#@permission_required_or_403('gallery.edit_image')
@login_required
@permission_required_or_403('events.change_collectionimage')
def edit_image(request, image_id):
    image = get_object_or_404(CollectionImage, id=image_id)
    if request.method == 'POST':
        form = EditImageForm(request.POST)
        if form.is_valid():
            image.title = form.cleaned_data['title']
            image.comments = form.cleaned_data['comments']
            image.save()
            return HttpResponseRedirect(reverse('administration_gallery_view', args=[image.collection.id]))
    else:
        form = UploadFileForm(model_to_dict(image))
    return direct_to_template(request, 'gallery/administration/edit_image.html',
                              {'form': form,
                               'image': image,
                               'active_module': 'gallery'})





#@transaction.commit_manually
@permission_required_or_403('gallery.delete_collectionimage')
def delete_image(request, image_id):
    image = get_object_or_404(CollectionImage, id=image_id)
    image_file_name = image.file_name
    collection_id = image.collection.id

    collection_path = settings.GALLERY['images_dir'] + str(collection_id)
    try:
        image_path = collection_path + '/' + image_file_name
        os.remove(image_path)
        thumbinail_path = collection_path + '/thumbinails/' + image_file_name
        os.remove(thumbinail_path)
    except Exception as e:
        if e.errno != 2: # 2 - файл не найден
            transaction.rollback()
            return HttpResponse(str(e))

    image.delete()
    #transaction.commit()
    return HttpResponseRedirect(reverse('administration_gallery_view', args=[collection_id]))



@permission_required_or_403('gallery.delete_collection')
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    collection_path = settings.GALLERY['images_dir'] + str(collection_id)
    try:
        shutil.rmtree(collection_path)
    except OSError as e:
        if e.errno == 2: # Не существует каталога с изображениями
            pass
        else:
            raise e
    CollectionImage.objects.filter(collection=collection).delete()
    collection.delete()

    return HttpResponseRedirect(reverse('administration_gallery_index'))





def handle_uploaded_file(f, collection_id):
    collection_path = settings.GALLERY['images_dir'] + str(collection_id) + '/'
    thumbinail_path = collection_path + 'thumbinails/'
    image_file_name = str(binascii.crc32(str(uuid.uuid4()))&0xffffffff) +'.jpg'

    if not os.path.exists(collection_path):
        os.makedirs(collection_path)
    destination = open(collection_path + image_file_name, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

    final_hight = 768

    try:
        im = Image.open(collection_path + image_file_name)
        im = im.convert('RGB')
        image_ratio = float(im.size[0]) / im.size[1]
        final_width = int((image_ratio * final_hight))
        im.thumbnail((final_width, final_hight), Image.ANTIALIAS)
        im.save(collection_path + image_file_name, "JPEG", quality = 95)
    except IOError as e:
        print 'lol', e
        return None

    final_hight = 60
    try:
        im = Image.open(collection_path + image_file_name)
        im = im.convert('RGB')
        image_ratio = float(im.size[0]) / im.size[1]
        final_width = int((image_ratio * final_hight))
        im.thumbnail((final_width, final_hight), Image.ANTIALIAS)
        if not os.path.exists(thumbinail_path):
            os.makedirs(thumbinail_path)
        im.save(thumbinail_path + image_file_name, "JPEG", quality = 95)
    except IOError as e:
        print 'lol', e
        return None
    return image_file_name

