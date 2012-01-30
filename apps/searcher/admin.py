# -*- coding: utf-8 -*-
from django.contrib import admin
from models import ZCatalog


class ZCatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')

admin.site.register(ZCatalog, ZCatalogAdmin)


