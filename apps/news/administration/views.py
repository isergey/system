# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from guardian.decorators import permission_required_or_403

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from apps.news.models import News
from forms import NewsForm
from django.forms.models import model_to_dict

@permission_required_or_403('news.add_news')
def index(request, type='public'):
    if type == 'public':
        news = News.objects.filter(type=0).order_by('-pub_date')
    elif type == 'professional':
        news = News.objects.filter(type=1).order_by('-pub_date')
    else:
        news = News.objects.all().order_by('-pub_date')
    paginator = Paginator(news, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        news_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        news_list = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'news/administration/news_list.html',
                              {'news_list': news_list,
                               'type':type,
                               'active_module': 'news'})

@permission_required_or_403('news.add_news')
def create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_news_index'))
    else:
        form = NewsForm()

    return direct_to_template(request, 'news/administration/news_create.html',
                              {'form': form,
                               'active_module': 'news'})

@permission_required_or_403('news.change_news')
def edit(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_news_index'))
    else:

        form = NewsForm(model_to_dict(news),instance=news)
    return direct_to_template(request, 'news/administration/news_edit.html',
                              {'form': form,
                               'news':news,
                               'active_module': 'news'})

@permission_required_or_403('news.delete_news')
def delete(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.delete()
    return HttpResponseRedirect(reverse('administration_news_index'))
