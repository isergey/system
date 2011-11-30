from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from guardian.decorators import permission_required_or_403
from models import Professional
from apps.news.models import News

@permission_required_or_403('professional.can_access')
def index(request):
    professional = get_object_or_404(Professional,id__gt=0)
    news = News.objects.filter(published=True, type=1).order_by('-pub_date')
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
    return direct_to_template(request, 'professional/page_show.html',
                              {'content': professional.content,
                               'news_list': news_list,
                               'module':'professional'})


@permission_required_or_403('professional.can_access')
def show_news(request, news_id):
    news = get_object_or_404(News, id=news_id, published=True, type=1)
    return direct_to_template(request, 'professional/news_show.html',
                              {'news': news,
                               'active_news':True})
