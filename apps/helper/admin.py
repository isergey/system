# -*- coding: utf-8 -*-
from django.contrib import admin
from models import AskLog


class AskLogAdmin(admin.ModelAdmin):
    list_display = ('normalize', 'not_normalize', 'datetime', 'answered')

admin.site.register(AskLog, AskLogAdmin)


