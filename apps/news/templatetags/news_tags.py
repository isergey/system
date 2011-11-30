# -*- coding: utf-8 -*-
from django import template
from apps.news.models import News
register = template.Library()

@register.inclusion_tag('news/news_feed.html')
def news_feed():
    news_list = News.objects.filter(published=True, type=0).order_by('-pub_date')[:5]
    return {'news_list': news_list}