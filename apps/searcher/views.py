#encoding: utf-8
from lxml import etree as ET
#import xml.etree.cElementTree as ET


from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django. shortcuts import render, HttpResponse, Http404, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from libs import pyaz
from libs.pymarc2.record import UnimarcRecord, Record
from libs.pymarc2 import marcxml

from participants.models import Library
from models import ZCatalog

#ZBASES = {
#    'ksob': {
#        'server': {
#            'host': u'127.0.0.1',
#            'port': u'27017',
#            #'user': u'erm',
#            #'password': u'123456',
#            'databaseName': u'KSOB',
#            #'databaseName': u'Default',
#            'preferredRecordSyntax': u'rusmarc',
#            'encoding': u'UTF-8'
#        },
#        },
#    }
#form_attr = {
#    'use': [
#            {
#            'id': u'1003',
#            'title': u'Автор',
#            },
#            {
#            'id': u'4',
#            'title': u'Заглавие',
#            },
#            {
#            'id': u'1018',
#            'title': u'Издающая организация',
#            },
#            {
#            'id': u'1080',
#            'title': u'Ключевые слова',
#            },
#            {
#            'id': u'21',
#            'title': u'Тематический поиск',
#            },
#            {
#            'id': u'1',
#            'title': u'Персоналия',
#            },
#            {
#            'id': u'59',
#            'title': u'Место издания',
#            },
#            {
#            'id': u'31',
#            'title': u'Год издания',
#            },
#            {
#            'id': u'5',
#            'title': u'Заглавие серии',
#            },
#            {
#            'id': u'1076',
#            'title': u'Географическая рубрика',
#            },
#    ],
#
#    'rows': [
#            {
#            'use': u'4',
#            'init': u''
#        },
#
#    ],
#
#    }
full_xslt_root = ET.parse(settings.ZGATE['xsl_templates']['full_document'])
full_transform = ET.XSLT(full_xslt_root)



def form_attr_init(request, catalog):
    form_attr = catalog.get_form_config()
    new_form_attr = {
        'use': form_attr['use'],
        'rows': []
    }
    terms = request.GET.getlist('term')
    uses = request.GET.getlist('use')
    operators = request.GET.getlist('operator')

    for i, term in enumerate(terms):
        if not term: continue
        row = {
            'use': uses[i],
            'init': term
        }
        if i > 0:
            row['operator'] = operators[i - 1]

        new_form_attr['rows'].append(row)

    if not new_form_attr['rows']:
        new_form_attr['rows'] = form_attr['rows']
    return new_form_attr

def do_search(request, catalog):
    query_builder = pyaz.RPNQueryBuilder()
    rows = catalog.get_form_config()['rows']
    for row in rows:
        operator = None
        if 'operator' in row:
            operator = row['operator']
            if operator == u'0':
                operator = u'@and'
            elif operator == u'1':
                operator = u'@or'
            elif operator == u'2':
                operator = u'@not'
            else:
                raise ValueError(u'Operator have wrong value')

        query_builder.add_condition(term=row['init'], use=row['use'], truncation=u'1', operator=operator)

    query = query_builder.build()
    print query

    base = catalog.get_server_config()
    zconnection = pyaz.ZConnection(
        base['server']
    )

    zconnection.connect(str(base['server']['host']), int(base['server']['port']))
    zresults = zconnection.search(query)


    #if zresults:
    paginator = Paginator(object_list=zresults, per_page=10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        zrecords_paginator = paginator.page(page)
    except (EmptyPage, InvalidPage):
        zrecords_paginator = paginator.page(paginator.num_pages)
    search_results = []
    offset = page * paginator.per_page - paginator.per_page
    number = offset # порядковый номер записи в результате

    for zrecord in zrecords_paginator.object_list:
        number += 1
        record = UnimarcRecord(raw=zrecord, raw_encoding='utf-8')
        search_results.append({
            'number': number,
            'record': record,
            })

    request.session['zrequest'] = {
        'query': query,
        'base': base,
        }

    return (search_results, zrecords_paginator)


def index(request, catalog_id='', slug=''):
    catalog = None
    if catalog_id:
        catalog = get_object_or_404(ZCatalog, id=catalog_id)
    if slug:
        catalog = get_object_or_404(ZCatalog, latin_title=slug)

    term = request.GET.get('term', None)
    form_attr = form_attr_init(request, catalog)
    rows = catalog.get_form_config()['rows']
    if term:

        try:
            search_results = do_search(request, catalog)
        except pyaz.ZConnectionException as e :
            return HttpResponse(u'Во время выполнения поискового запроса возникла ошибка. Повторите запрос позднее. Причина: ' + e.message)
        return render(request, 'searcher/searcher.html', {
            'search_results': search_results[0],
            'pages_list': search_results[1],
            'form_attr': form_attr,
            'catalog': catalog
        })
    return render(request, 'searcher/searcher.html', {
        'form_attr': form_attr,
        'catalog': catalog
    })


def get_title(self):
    title = []
    try:
        for subfield in self._fields['461'][0]['1']:
            if subfield.field.tag == '200':
                title.append(subfield.field['a'][0].data)
                title.append(u': ' + subfield.field['e'][0].data)
    except KeyError:
        pass

    try:
        if title:
            title.append(u', ' + self._fields['200'][0]['a'][0].data)
        else:
            title.append(self._fields['200'][0]['a'][0].data)
            title.append(u', ' + self._fields['200'][0]['e'][0].data)
    except KeyError:
        pass

    return u''.join(title)

UnimarcRecord.get_title = get_title

def detail(request, catalog_id='', slug=''):
    catalog = None
    if catalog_id:
        catalog = get_object_or_404(ZCatalog, id=catalog_id)
    if slug:
        catalog = get_object_or_404(ZCatalog, latin_title=slug)

    number = request.GET.get('number', None)
    #zrecords = cache['zrecords']
    base = base = catalog.get_server_config()
    query = request.session['zrequest']['query']
    zconnection = pyaz.ZConnection(
        base['server']
    )
    try:
        zconnection.connect(str(base['server']['host']), int(base['server']['port']))
    except pyaz.ZConnectionException as e :
        return HttpResponse(u'Во время выполнения поискового запроса возникла ошибка. Повторите запрос позднее. Причина: ' + e.message)

    zconnection.connect(str(base['server']['host']), int(base['server']['port']))
    zresults = zconnection.search(query)
    zrecord = zresults[(int(number) - 1)]
    zrecord = UnimarcRecord(raw=zrecord)
    xml_record = marcxml.record_to_rustam_xml(zrecord)
    result_tree = full_transform(xml_record)
    full_document = unicode(result_tree)

    try:
        owners = get_document_owners(xml_record)
        record_id = get_record_id(xml_record)
        save_document = True
    except SyntaxError as e:
        pass #не будем добавлять держателей

    zrecord.get_title()
    return render(request, 'searcher/detail.html', {
        'record': full_document,
        'owners': owners,
        'record_id': record_id,
        'save_document': save_document,
        })


"""
xml_record ETreeElement
return list of owners
"""

def get_document_owners(xml_record):
    def get_subfields(field_code, subfield_code):
        org_ids = []
        fields = xml_record.findall('field')

        for field in fields:
            if field.attrib['id'] == field_code:
                subfileds = field.findall('subfield')

                for subfiled in subfileds:
                    if subfiled.attrib['id'] == subfield_code:
                        if subfiled.text:
                            org_ids.append(subfiled.text) # сиглы организаций (code)
                            break
        return org_ids

    #сперва ищем держателей в 850 поле
    owners = get_subfields('850', 'a')
    if not owners:
        owners = get_subfields('899', 'a')
        #если нет то в 899

    owners_dicts = []

    if owners:
        libraries = Library.objects.filter(code__in=owners)
        for org in libraries:
            owners_dicts.append({
                'code': org.code,
                'name': org.name
            })
    return owners_dicts

"""
xml_record ETreeElement
return record id string or None if record not have id
"""

def get_record_id(xml_record):
    fields = xml_record.findall('field')
    for field in fields:
        if field.attrib['id'] == '001':
            if field.text:
                return field.text
    return None