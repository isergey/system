# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.events.models import Event, FavoriteEvent, EventComment, EventCategory

class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(EventCategory, EventCategoryAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'active')

admin.site.register(Event, EventAdmin)

class FavoriteEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event')
admin.site.register(FavoriteEvent,FavoriteEventAdmin)

class EventCommentAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'text', 'post_date')
    list_filter = ['event','user','post_date']
admin.site.register(EventComment,EventCommentAdmin)