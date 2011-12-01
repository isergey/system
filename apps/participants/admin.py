# encoding: utf-8

from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from models import Library, UserLibrary, Country, City, District


admin.site.register(Library, MPTTModelAdmin)

class UserLibraryAdmin(admin.ModelAdmin):
    list_display = ["user" ]

admin.site.register(UserLibrary, UserLibraryAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ["name" ]

admin.site.register(Country, CountryAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(City, CityAdmin)

class DistrictAdmin(admin.ModelAdmin):
    list_display = ["name" ]

admin.site.register(District, DistrictAdmin)