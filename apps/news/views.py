from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from models import News


def index(request):
    news = News.objects.filter(published=True, type=0).order_by('-pub_date')
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
        
    return direct_to_template(request, 'news/news_list.html',
                              {'news_list': news_list,
                               'active_news':True})

def show(request, news_id):
    news = get_object_or_404(News, id=news_id, published=True, type=0)
    return direct_to_template(request, 'news/news_show.html',
                              {'news': news,
                               'active_news':True})