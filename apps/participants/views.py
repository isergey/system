# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render,get_object_or_404, get_list_or_404 ,Http404
import simplejson
from libs.ldapwork.ldap_work import  LdapWork
from districts import districts_list, find_district
from models import LibrarySystem, Library, District

def make_library_dict(library):
    return {
        'code': library.code,
        'title': library.name,
        'address':  getattr(library,'postal_address',u"не указан"),
        'phone': getattr(library,'phone',u"не указан"),
        'plans': getattr(library,'plans',u"не указано"),
        'http_service': getattr(library,'http_service',u"не указан"),
        'latitude': library.latitude,
        'longitude': library.longitude,
    }


def index(request):
    library_systems = LibrarySystem.objects.all()
    for org in library_systems:
        print org.code, org.name

    return render(request, 'participants/cbs_list.html',
                              {'orgs':library_systems})

def cbs_list(request, code):

    library_system = get_object_or_404(LibrarySystem, code=code)
    libraries = Library.objects.filter(library_system=library_system)
    orgs = []

    for org in libraries:
        orgs.append(make_library_dict(org))

    js_orgs =  simplejson.dumps(orgs, encoding='utf-8',ensure_ascii=False)
    return render(request, 'participants/participants_list_by_cbs.html',
                              {'cbs_name':library_system.name,
                               'cbs_code': id,
                                'ldap_orgs':orgs,
                               'js_orgs':js_orgs})

def detail_by_cbs(request, code):
    library = get_object_or_404(Library,code=code)

    orgs = []

    orgs.append(make_library_dict(library))

    js_orgs =  simplejson.dumps(orgs, encoding='utf-8',ensure_ascii=False)
    return render(request, 'participants/participants_detail_by_cbs.html',
                              {'cbs_name':library.library_system.name,
                               'cbs_code': library.library_system.code,
                                'library':library,
                               'js_orgs':js_orgs})



def detail_by_district(request, code):
    library = get_object_or_404(Library,code=code)

    orgs = [make_library_dict(library)]

    js_orgs =  simplejson.dumps(orgs, encoding='utf-8',ensure_ascii=False)
    return render(request, 'participants/participants_detail_by_district.html', {
        'library': library,
        'js_orgs':js_orgs
    })

def districts(request):

    #ldap_work = LdapWork(settings.LDAP)


    return render(request, 'participants/districts_list.html',
                              {'districts':districts_list})

def by_district(request, id):
    district = get_object_or_404(District,id=id)
    libraries = Library.objects.filter(district=district)
    orgs = []
    for org in libraries:
        orgs.append(make_library_dict(org))


    js_orgs =  simplejson.dumps(orgs, encoding='utf-8',ensure_ascii=False)
    return render(request, 'participants/participants_list_by_districts.html',
                              {'ldap_orgs':libraries,
                               'district':district,
                               'js_orgs':js_orgs})
