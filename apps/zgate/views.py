# -*- coding: utf-8 -*-
from django.utils.http import urlquote
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from guardian.core import ObjectPermissionChecker
import simplejson
from lxml import etree
import xml.etree.cElementTree as ET
import time
from participants.models import Library, LibrarySystem
#catalogs = settings.ZGATE['catalogs']

from models import ZCatalog, SavedRequest, SavedDocument
import zworker
from libs import humanquery
def json_error(error):
    return simplejson.dumps({'status': 'error',
                             'error': error},
        ensure_ascii=False)

full_xslt_root = etree.parse(settings.ZGATE['xsl_templates']['full_document'])
full_transform = etree.XSLT(full_xslt_root)

short_xslt_root = etree.parse(settings.ZGATE['xsl_templates']['short_document'])
short_transform = etree.XSLT(short_xslt_root)

def set_cookies_to_response(cookies, response):
    for key in cookies:
        response.set_cookie(key, cookies[key])
    return response

def render_search_result(request, catalog, zresult=''):
    cookies = {}
    if zresult == '':
        url = catalog.url
        new_get = []
        for key in request.GET:
            if key == 'zstate': continue
            new_get.append(urlquote(key) + '=' + urlquote(request.GET[key]))

        new_get = '&'.join(new_get)

        if request.GET['zstate'] == 'action':
            url = url + '?' + new_get
        else:
            url = url + '?' + request.GET['zstate'].replace(' ', '+')

        (zresult, cookies) = zworker.request(url)
    try:
        zresults_body_element = zworker.get_body_element(zresult)

        zresults_body_element = zworker.change_links_href(zresults_body_element)
    except Exception:
        return HttpResponse(u'Некорректный url')
    result = zworker.make_html_body_content(zresults_body_element)

    response = render(request, 'zgate/search_results.html',
            {'catalog_title': catalog.title,
             'search_results': result})

    return  set_cookies_to_response(cookies, response)


def render_form(request, zresult, catalog):
    zworker.entry_point = reverse("zgate_index", args=[catalog.id])
    page_body = zworker.get_body_element(zresult)
    page_body = zworker.change_links_href(page_body)
    page_body = zworker.change_form_action(page_body)
    page_body = zworker.make_html_body_content(page_body)

    return render(request, 'zgate/search_form.html',
            {'catalog_title': catalog.title,
             'search_form': page_body,
             'catalog': catalog})


def help(request, catalog_id='', slug=''):
    if catalog_id:
        catalog = get_object_or_404(ZCatalog, id=catalog_id)
    if slug:
        catalog = get_object_or_404(ZCatalog, latin_title=slug)

    return render(request, 'zgate/help.html',
            {'catalog': catalog})


def render_detail(request, catalog):
    zvars = request.GET['zstate'].split(' ')
    zstate = request.GET['zstate'].replace(' ', '+')
    zgate_url = catalog.url

    (zresult, cookies) = zworker.request(zgate_url + '?' + zstate, cookies=request.COOKIES)
    zresults_body_element = zworker.get_body_element(zresult)
    zresults_body_element = zworker.change_links_href(zresults_body_element)

    #забираем xml представление записи
    (xml_record, cookies) = zworker.request(zgate_url + '?' + zstate.replace('1+F', '1+X'), cookies=request.COOKIES)
    s = time.time();
    owners = []
    record_id = '0'
    st = request.GET['zstate']
    zsession = zvars[1]
    zoffset = zvars[3]
    save_document = False
    try:
        xml_record = ET.XML(xml_record)
        #print 'ET :', time.time() - s
        owners = get_document_owners(xml_record)
        record_id = get_record_id(xml_record)
        save_document = True
    except SyntaxError as e:
        pass #не будем добавлять держателей


    result = zworker.make_html_body_content(zresults_body_element)
    response =  render(request, 'zgate/search_results.html',
            {'catalog_title': catalog.title,
             'search_results': result,
             'owners': owners,
             'record_id': record_id,
             'zsession': zsession,
             'zoffset': zoffset,
             'catalog': catalog,
             'save_document': save_document,
             })
    return set_cookies_to_response(cookies, response)

@login_required
def save_requests(request, catalog):
    query = ''
    human_query = ''
    zurls = ''
    if 'TERM' in request.GET and request.GET['TERM']:
        query = request.GET['TERM']
        try:
            human_query = humanquery.HumanQuery(query).convert()
        except Exception as e:
            if settings.DEBUG:
                raise  e

    else:
        return HttpResponse(u'Неверные параметры запроса. Не указаны поисковые параметры.')

    if 'DB' in request.GET and request.GET['DB']:
        zurls = request.GET['DB']
    else:
        return HttpResponse(u'Неверные параметры запроса, Не указаны параметры баз данных.')

    saved_request = SavedRequest(zcatalog=catalog, user=request.user, zurls=zurls, query=query, human_query=human_query)
    saved_request.save()
    return render(request, 'zgate/save_request.html',
            {'saved_request': saved_request,
             'module':'zgate'})

def save_document(request):
    if request.method != 'POST':
        return HttpResponse('Only post requests');


    expiry_date = None
    if request.user.is_authenticated():
        owner_id = request.user.username
    elif request.session.session_key:
        owner_id = request.session.session_key
        expiry_date = request.session.get_expiry_date()
    else:
        return HttpResponse(json_error(u'Документ не может быть сохранен, возможно в Вашем браузере отключены cookies.'))

    catalog = get_object_or_404(ZCatalog, latin_title=request.POST['catalog_id'])
    zgate_url = catalog.url

    zstate = 'present+' + request.POST['zsession'] +\
             '+default+' + request.POST['zoffset'] +\
             '+1+X+1.2.840.10003.5.28+'+catalog.default_lang

    (xml_record, cookies) = zworker.request(zgate_url + '?' + zstate)

    try:
        tree = ET.XML(xml_record)
    except SyntaxError as e:
        return HttpResponse(json_error(u'Заказ не выполнен. Возможно, время сессии истекло'))

    comments = None
    if 'comments' in request.POST and request.POST['comments']:
        comments = request.POST['comments']

    try:
        doc = etree.XML(xml_record)
        result_tree = full_transform(doc)
        full_document = unicode(result_tree)

        result_tree = short_transform(doc)
        short_document = unicode(result_tree)
    except Exception, e:
        raise e

    saved_document = SavedDocument(
        zcatalog=catalog,
        owner_id=owner_id,
        document=xml_record,
        comments=comments,
        expiry_date=expiry_date,
        full_document=full_document,
        short_document=short_document
    )

    saved_document.save()

    response =  HttpResponse(simplejson.dumps({'status': 'ok'}, ensure_ascii=False));
    return response



def index(request, catalog_id='', slug=''):
    if catalog_id:
        catalog = get_object_or_404(ZCatalog, id=catalog_id)
    if slug:
        catalog = get_object_or_404(ZCatalog, latin_title=slug)


    checker = ObjectPermissionChecker(request.user)
    if not checker.has_perm('view_zcatalog', catalog):
        return HttpResponse(u'Доступ запрещен')

    if not catalog.can_search:
        return HttpResponse(u"Каталог не доступен для поиска.")

    zgate_url = catalog.url
    if request.method == 'POST' and 'SESSION_ID' in request.POST:
        (result, cookies) = zworker.request(zgate_url, data=request.POST, cookies=request.COOKIES)
        response =  render_search_result(request, catalog, zresult=result, )
        return set_cookies_to_response(cookies,response)

    else:
        if 'zstate' in request.GET: #а тут пользователь уже начал щелкать по ссылкам

            if 'ACTION' in request.GET and request.GET['ACTION'] == 'pq':
                return save_requests(request, catalog)

            url = zgate_url + '?' + request.GET['zstate'].replace(' ', '+')

            vars = request.GET['zstate'].split(' ')
            cookies = {}
            if vars[0] == 'form':
                (zresult, cookies) = zworker.request(url, cookies=request.COOKIES)
                response = render_form(request, zresult=zresult, catalog=catalog)
                return set_cookies_to_response(cookies,response)

            elif vars[0] == 'present':
                if vars[4] == '1' and vars[5] == 'F':
                    response = render_detail(request, catalog)
                    return set_cookies_to_response(cookies,response)

                response = render_search_result(request, catalog)
                return set_cookies_to_response(cookies,response)
            else:
                response = render_search_result(request, catalog)
                return set_cookies_to_response(cookies,response)
        else: #значит только инициализация формы
        #            if not catalog.can_search:
        #                return Htt

            (zgate_form, cookies) = zworker.get_zgate_form(
                zgate_url=zgate_url,
                xml=catalog.xml,
                xsl=catalog.xsl,
                cookies=request.COOKIES
            )

            response = render_form(request, zgate_form, catalog)
            return set_cookies_to_response(cookies, response)



def saved_document_list(request):
    owner_id = ''
    if request.user.is_authenticated():
        owner_id = request.user.username
    elif request.session.session_key:
        owner_id = request.session.session_key

    saved_documents = SavedDocument.objects.filter(owner_id=owner_id).order_by('-add_date')

    format = 'full'
    if 'format' in request.GET and request.GET['format'] == 'short':
        format = 'short'

    return render(request, 'zgate/saved_documents_list.html',
            {'saved_documents': saved_documents,
             'format': format,
             'module':'zgate'})



def load_documents(request):
    response = HttpResponse(mimetype='application/txt')
    response['Content-Disposition'] = 'attachment; filename=documents.txt'
    if request.method == 'POST':
        owner_id = ''
        if request.user.is_authenticated():
            owner_id = request.user.username
        elif request.session.session_key:
            owner_id = session_key

        documents = []

        if 'download' in request.POST and isinstance(request.POST.getlist('download'), list) and len(request.POST.getlist('download')):
            save_requests = SavedDocument.objects.filter(pk__in=request.POST.getlist('download'), owner_id=owner_id)

            for save_request in save_requests:
                documents.append(save_request.short_document)

            response.write('\r\n'.join(documents))
        else:
            save_requests = SavedDocument.objects.filter(owner_id=owner_id)
            for save_request in save_requests:
                documents.append(save_request.short_document)

            response.write('\r\n'.join(documents))
    return response


def delete_saved_document(request, document_id=''):
    owner_id = ''
    if request.user.is_authenticated():
        owner_id = request.user.username
    elif request.session.session_key:
        owner_id = session_key

    saved_document = get_object_or_404(SavedDocument,id=document_id, owner_id=owner_id)
    saved_document.delete()
    return redirect(reverse('zgate_saved_document_list'))


@login_required
def saved_requests_list(request):

    saved_requests = SavedRequest.objects.filter(user=request.user).order_by('-add_date').select_related()
    paginator = Paginator(saved_requests, 20)
    try:

        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        saved_requests_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        saved_requests_list = paginator.page(paginator.num_pages)

    return render(request, 'zgate/saved_requests_list.html',
            {'saved_requests_list': saved_requests_list,
             'module':'zgate'})



@login_required
def make_saved_request(request, request_id=''):
    saved_request = get_object_or_404(SavedRequest,id=request_id, user = request.user)


    (zgate_form, cookies) = zworker.get_zgate_form(
        zgate_url=saved_request.zcatalog.url,
        xml=saved_request.zcatalog.xml,
        xsl=saved_request.zcatalog.xsl,
        cookies=request.COOKIES
        #        username=username,
        #        password=password
    )
    session_id = zworker.get_zgate_session_id(zgate_form)
    get_params = []
    get_params.append(urlquote('zstate') + '=' + urlquote('action'))
    get_params.append(urlquote('ACTION') + '=' + urlquote('SEARCH'))
    get_params.append(urlquote('SESSION_ID') + '=' + urlquote(session_id))
    get_params.append(urlquote('LANG') + '=' + urlquote(saved_request.zcatalog.default_lang))
    get_params.append(urlquote('DBNAME') + '=' + urlquote(saved_request.zurls))
    get_params.append(urlquote('TERM_1') + '=' + urlquote(saved_request.query))
    get_params.append(urlquote('ESNAME') + '=' + urlquote('B'))
    get_params.append(urlquote('MAXRECORDS') + '=' + urlquote('20'))
    get_params.append(urlquote('CHAR_SET') + '=' + urlquote('UTF-8'))
    get_params.append(urlquote('RECSYNTAX') + '=' + urlquote('1.2.840.10003.5.28'))

    link = reverse('zgate_index', args=(saved_request.zcatalog.id,)) + '?' + '&'.join(get_params)

    response = redirect(link)
    return set_cookies_to_response(cookies, response)

@login_required
def delete_saved_request(request, request_id=''):
    saved_request = get_object_or_404(SavedRequest,id=request_id, user = request.user)
    saved_request.delete()
    return redirect(reverse('zgate_saved_requests'))
"""
xml_record ETreeElement
return list of owners
"""

def get_document_owners(xml_record):

    def get_subfields(field_code, subfield_code):
        subfields = []
        fields = xml_record.findall('field')
        for field in fields:
            if field.attrib['id'] == field_code:
                subfileds = field.findall('subfield')
                for subfiled in subfileds:
                    if subfiled.attrib['id'] == subfield_code:
                        if subfiled.text:
                            subfields.append(subfiled.text) # сиглы организаций (code)
                            break
        return subfields

    #сперва ищем держателей в 850 поле
    owners =  get_subfields('850', 'a')
    if not owners:
        owners =  get_subfields('899', 'a')
        #если нет то в 899

    owners_dicts = []
    if owners:
        library_systems = LibrarySystem.objects.filter(code__in=owners)
        for org in library_systems:
            owners_dicts.append({
                'code':org.code,
                'name': org.name
            })
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
