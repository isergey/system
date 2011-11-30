# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.zgate.models import ZCatalog
from guardian.admin import GuardedModelAdmin

class ZCatalogAdmin(GuardedModelAdmin):
    list_display = ('title', 'description', 'url', 'xml', 'xsl')

admin.site.register(ZCatalog, ZCatalogAdmin)
