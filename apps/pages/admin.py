# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.pages.models import Page
from guardian.admin import GuardedModelAdmin

class PageAdmin(GuardedModelAdmin):
    list_display = ('title',)
admin.site.register(Page,PageAdmin)

  