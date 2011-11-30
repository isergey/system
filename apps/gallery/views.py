# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from guardian.decorators import permission_required_or_403

from forms import UploadFileForm, CreateCollectionForm, EditImageForm
from models import Collection, CollectionImage

import uuid
import Image
import os

def index(request):
    collections = Collection.objects.all()

    return direct_to_template(request, 'gallery/collections_list.html',
                              {'collections': collections,
                               'active': 'gallery'})

#@permission_required_or_403('gallery.view_collection')
def view_collection(request, slug='', collection_id=''):
    if collection_id:
        collection = get_object_or_404(Collection, id=collection_id)
    if slug:
        collection = get_object_or_404(Collection, latin_title=slug)
    images = CollectionImage.objects.filter(collection=collection)
    images_dir = settings.GALLERY['public_path']+str(collection.id)+'/'
    thumbinails_dir =  images_dir + 'thumbinails/'
    return direct_to_template(request, 'gallery/collections_view.html',
                              {'collection': collection,
                               'images':images,
                               'images_dir':images_dir,
                               'thumbinails_dir':thumbinails_dir,
                               'active': 'gallery'
                               })

#@csrf_exempt
#@login_required
def create_collection(request):
    if request.method == 'POST':
        form = CreateCollectionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gallery_index'))
    else:
        form = CreateCollectionForm()
    return direct_to_template(request, 'gallery/create_collection.html',
                              {'form': form,
                               'active': 'gallery'})




#@csrf_exempt
#@login_required
#@transaction.commit_manually
def delete_collection(request, collection_id):
    import shutil   
    collection = get_object_or_404(Collection, id=collection_id)
    CollectionImage.objects.filter(collection=collection).delete()
    collection.delete()
    collection_path = settings.GALLERY['images_dir'] + str(collection_id)
    shutil.rmtree(collection_path)
    transaction.commit()
    return HttpResponseRedirect(reverse('gallery_index'))



#@csrf_exempt
#@login_required
#@transaction.commit_manually
def delete_image(request, collection_id, image_id):

    collection = get_object_or_404(Collection, id=collection_id)
    image = get_object_or_404(CollectionImage, id=image_id)
    image_file_name = image.file_name
    image.delete()
    
    collection_path = settings.GALLERY['images_dir'] + str(collection_id)
    try:
        image_path = collection_path + '/' + image_file_name
        os.remove(image_path)
        thumbinail_path = collection_path + '/thumbinails/' + image_file_name
        os.remove(thumbinail_path)
    except Exception as e:
        transaction.rollback()
        return HttpResponse(str(e))
    transaction.commit()
    return HttpResponseRedirect(reverse('gallery_index'))



#@csrf_exempt
#@login_required
def edit_image(request, collection_id, image_id):
    collection = get_object_or_404(Collection, id=collection_id)
    image = get_object_or_404(CollectionImage, id=image_id)
    if request.method == 'POST':
        form = EditImageForm(request.POST)
        if form.is_valid():
            image.title = form.cleaned_data['title']
            image.comments = form.cleaned_data['comments']
            image.save()
            return HttpResponseRedirect(reverse('gallery_view', args=[collection_id]))
    else:
        init = {'title':image.title, 'comments': image.comments}
        form = UploadFileForm(initial=init)
    return direct_to_template(request, 'gallery/image_edit.html',
                              {'form': form,
                               'active': 'gallery'})

#@csrf_exempt #отключаем защиту csrf
#@login_required
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
            return HttpResponseRedirect(reverse('gallery_view', args=[collection_id]))
    else:
        form = UploadFileForm()
    return direct_to_template(request, 'gallery/image_upload.html',
                              {'form': form,
                               'collection': collection,
                               'active': 'gallery'})


def handle_uploaded_file(f, collection_id):
    collection_path = settings.GALLERY['images_dir'] + str(collection_id) + '/'
    thumbinail_path = collection_path + 'thumbinails/'
    image_file_name = str(uuid.uuid4()) +'.jpg'
    
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
