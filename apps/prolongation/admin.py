# -*- coding: utf-8 -*-
from django.contrib import admin
from prolongation.models import UserProlongation, StatusChange, ProlongationManager

class UserProlongationAdmin(admin.ModelAdmin):
    list_display = ('user','recive_library', 'manage_library', 'create_date')

admin.site.register(UserProlongation, UserProlongationAdmin)


#class StatusChangeAdmin(admin.ModelAdmin):
#    list_display = ('prolongation','status', 'change_date')

#admin.site.register(StatusChange, StatusChangeAdmin)


class ProlongationManagerAdmin(admin.ModelAdmin):
    list_display = ('user','library')

admin.site.register(ProlongationManager, ProlongationManagerAdmin)