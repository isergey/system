# encoding: utf-8

from django.contrib import admin

from models import LibrarySystem, Library, UserLibrarySystem, UserLibrary, Country, City, District


class LibrarySystemAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(LibrarySystem, LibrarySystemAdmin)

class LibraryAdmin(admin.ModelAdmin):
    list_display = ["name",'library_system']

admin.site.register(Library, LibraryAdmin)

class UserLibrarySystemAdmin(admin.ModelAdmin):
    list_display = ["user" ]

admin.site.register(UserLibrarySystem,UserLibrarySystemAdmin)



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