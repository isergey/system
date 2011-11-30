# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.news.models import News

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')
    list_filter = ['pub_date']
admin.site.register(News,NewsAdmin)
