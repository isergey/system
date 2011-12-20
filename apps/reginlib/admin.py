# -*- coding: utf-8 -*-
from django.contrib import admin
from reginlib.models import UserLibRegistation, StatusChange, RegistrationManager

class UserLibRegistationAdmin(admin.ModelAdmin):
    list_display = ('user','library', 'create_date')

admin.site.register(UserLibRegistation, UserLibRegistationAdmin)


class StatusChangeAdmin(admin.ModelAdmin):
    list_display = ('registration','status', 'change_date')

admin.site.register(StatusChange, StatusChangeAdmin)


class RegistrationManagerAdmin(admin.ModelAdmin):
    list_display = ('user','library')

admin.site.register(RegistrationManager, RegistrationManagerAdmin)