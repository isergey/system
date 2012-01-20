#encoding: utf-8
from lxml import etree as ET
#import xml.etree.cElementTree as ET

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django. shortcuts import render, HttpResponse, Http404, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from libs import pyaz
from libs.pymarc2.record import UnimarcRecord, Record
from libs.pymarc2 import marcxml

from participants.models import Library
ZBASES = {
    'ksob': {
        'server': {
            'host': u'127.0.0.1',
            'port': u'27017',
            #'user': u'erm',
            #'password': u'123456',
            'databaseName': u'KSOB',
            'preferredRecordSyntax': u'rusmarc',
            'encoding': u'UTF-8'
        },
    },
 }

full_xslt_root = ET.parse(settings.ZGATE['xsl_templates']['full_document'])
full_transform = ET.XSLT(full_xslt_root)


def do_search(request):
    USE_ATTRIBUTES = {
        'anywhere': u'1035',
        'author': u'1003',
        'title': u'4',
        'subject': u'21',
        }

    search_results = []

    term = request.GET.get('term', None)
    use = request.GET.get('use', None)

    if use and use in  USE_ATTRIBUTES:
        use = USE_ATTRIBUTES[use]
    else:
        use = None

    term_count = 0
    zrecords = None

    query_builder = pyaz.RPNQueryBuilder()
    query_builder.add_condition(term=term, use=use, truncation=u'1')

    query = query_builder.build()

    zresults = None

    base = ZBASES['ksob']
    zconnection = pyaz.ZConnection(
        base['server']
    )
    zconnection.connect(str(base['server']['host']), int(base['server']['port']))

    zresults = zconnection.search(query)
    #except Exception:
    #    pass

    if zresults:
        paginator = Paginator(object_list=zresults, per_page=10)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            zrecords = paginator.page(page)
        except (EmptyPage, InvalidPage):
            zrecords = paginator.page(paginator.num_pages)
        search_results = []
        offset = page * paginator.per_page - paginator.per_page
        number = offset # порядковый номер записи в результате

        for zrecord in zrecords.object_list:
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

        #cache['zrecords'] = search_results
        return (search_results, zrecords)

def index(request):
    term = request.GET.get('term', None)
    if term:
        try:
            search_results = do_search(request)
        except pyaz.ZConnectionException:
            return HttpResponse(u'Невозможно установть соединение с библиографической базой. Попробуйте позднее.')
        return render(request, 'searcher/searcher.html', {
            'search_results': search_results[0],
            'pages_list':search_results[1]
            })
    return render(request, 'searcher/searcher.html')

def detail(request):
    number = request.GET.get('number', None)
    #zrecords = cache['zrecords']
    base = request.session['zrequest']['base']
    query = request.session['zrequest']['query']
    zconnection = pyaz.ZConnection(
        base['server']
    )

    zconnection.connect(str(base['server']['host']), int(base['server']['port']))
    zresults = zconnection.search(query)
    zrecord = zresults[(int(number)-1)]
    zrecord = UnimarcRecord(raw=zrecord, raw_encoding='utf-8')
    xml_record = marcxml.record_to_rustam_xml(zrecord)
    result_tree = full_transform(xml_record)
    full_document = unicode(result_tree)

    try:
        owners = get_document_owners(xml_record)
        record_id = get_record_id(xml_record)
        save_document = True
    except SyntaxError as e:
        pass #не будем добавлять держателей


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
    owners =  get_subfields('850', 'a')
    if not owners:
        owners =  get_subfields('899', 'a')
        #если нет то в 899

    owners_dicts = []

    if owners:
        libraries = Library.objects.filter(code__in=owners)
        for org in libraries:
            owners_dicts.append({
                'code':org.code,
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