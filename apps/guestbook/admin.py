# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.guestbook.models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'published','add_date')
    list_filter = ['add_date']
admin.site.register(Feedback,FeedbackAdmin)
