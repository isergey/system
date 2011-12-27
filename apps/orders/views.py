# -*- coding: utf-8 -*-
import time
from lxml import etree
import xml.etree.cElementTree as ET
import datetime
import re

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from libs.ill import ILLRequest
from libs.order_manager.manager import OrderManager


from libs.ldapwork.ldap_work import LdapWork, LdapWorkException, LdapConnection
import zgate.zworker as  zworker
from zgate.models import ZCatalog
from participants.models import Library
from templatetags.order_tags import org_by_id

from models import UserOrderTimes


def set_cookies_to_response(cookies, response):
    for key in cookies:
        response.set_cookie(key, cookies[key])
    return response

def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        json = simplejson.dumps({'status': 'error', 'error': u'Необходимо войти в систему'}, ensure_ascii=False)
        return HttpResponse(json, mimetype='application/json')

    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap


def json_error(error):
    return simplejson.dumps({'status': 'error',
                             'error': error},
        ensure_ascii=False)


order_statuses_titles = {
    'new': u'принят на обработку',
    'recall': u'отказ',
    'conditional': u'в обработке',
    'shipped': u'доставлен',
    'pending': u'в ожидании', #Доставлен
    'notsupplied': u'выполнение невозможно',
    }

apdy_type_titles = {
    'ILLRequest': u'Заказ',
    'ILLAnswer': u'Ответ',
    'Shipped': u'Доставлен',
    'Recall': u'Задолженность',
    }

apdu_reason_will_supply = {
    '1': u'Получены условия',
    '2': u'Необходимо повторить запрос позднее',
    '3': u'Отказ',
    '4': u'Получена информация о местонахождении документа',
    '5': u'Заказ будет выполнен позднее',
    '6': u'Запрос поставлен в очередь',
    '7': u'Получена информация о стоимости выполнения заказа',
    }
apdu_unfilled_results = {
    '1': u'Документ выдан',
    '2': u'Документ в обработке',
    '3': u'Документ утерян и/или списан',
    '4': u'Документ не выдается',
    '5': u'Документа нет в фонде',
    '6': u'Документ заказан, но еще не получен ',
    '7': u'Том / выпуск еще не приобретен',
    '8': u'Документ в переплете',
    '9': u'Отсутствуют необходимые части / страницы документа',
    '10': u'Нет на месте',
    '11': u'Документ временно не выдается',
    '12': u'Документ в плохом состоянии',
    '13': u'Недостаточно средств для выполнения заказа',
    #'14':u'',
    #'15':u'Документ в плохом состоянии',    
}

#Вид и статусы заказов, в зависимоти от которых можно удалять заказ
can_delete_statuses = {
    '1': ['shipped', 'received', 'notsupplied','checkedin'], #document
    '2': ['shipped', 'received', 'notsupplied', 'checkedin'], #copy
    '5': ['shipped','notsupplied', 'checkedin'] #reserve
}



xslt_root = etree.parse(settings.ORDERS['xsl_templates']['marc'])
transform = etree.XSLT(xslt_root)

def check_for_can_delete(transaction):
    """
    return True or False
    """
    for apdu in transaction.illapdus:
        if isinstance(apdu.delivery_status, ILLRequest):
            if apdu.delivery_status.ill_service_type in can_delete_statuses and\
               transaction.status in can_delete_statuses[apdu.delivery_status.ill_service_type]:
                return True
    return False

@login_required
def index(request):
    def format_time(datestr='', timestr=''):


        if datestr:
            datestr = time.strptime(datestr, "%Y%m%d")
            datestr = time.strftime("%d.%m.%Y", datestr)
        if timestr:
            timestr = time.strptime(timestr, "%H%M%S")
            timestr = time.strftime("%H:%M:%S", timestr)
        return datestr + ' ' + timestr
    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])
    transactions = order_manager.get_orders(request.user.username)
    orgs = {}
    #for org_id in transactions_by_org:
    orders = []
    for transaction in transactions:
        #print ET.tostring(transaction.illapdus[0].delivery_status.supplemental_item_description, encoding="UTF-8")
        try:
            doc = etree.XML(ET.tostring(transaction.illapdus[0].delivery_status.supplemental_item_description,
                encoding="UTF-8"))
            result_tree = transform(doc)
            res = str(result_tree)
        except Exception, e:
            raise e
        res = res.replace('– –', '—')
        res = res.replace('\n', '</br>')
        order = {}

        if transaction.status in order_statuses_titles:
            order['status'] = order_statuses_titles[transaction.status]
        else:
            order['status'] = transaction.status
        order['type'] = ''
        order['copy_info'] = ''
        order['apdus'] = []

        for apdu in transaction.illapdus:
            apdu_map = {}

            apdu_map['type'] = apdu.delivery_status.type
            if apdu.delivery_status.type in apdy_type_titles:
                apdu_map['type_title'] = apdy_type_titles[apdu.delivery_status.type]
            else:
                apdu_map['type_title'] = apdu.delivery_status.type

            apdu_map['datetime'] = format_time(apdu.delivery_status.service_date_time['dtots']['date'],
                apdu.delivery_status.service_date_time['dtots']['time'])

            if isinstance(apdu.delivery_status, ILLRequest):
                order['order_id'] = apdu.delivery_status.transaction_id['tq']
                order['org_info'] = org_by_id(apdu.delivery_status.responder_id['pois']['is'])
                if apdu.delivery_status.third_party_info_type['tpit']['stl']['stlt']['si']:
                    order['org_info'] = org_by_id(apdu.delivery_status.third_party_info_type['tpit']['stl']['stlt']['si'])
                apdu_map['requester_note'] = apdu.delivery_status.requester_note
                order['record'] = res
                order['user_comments'] = apdu.delivery_status.requester_note
                apdu_map['record'] = res
                if apdu.delivery_status.ill_service_type == '1':
                    apdu_map['service_type'] = u'документ'
                    order['type'] = 'doc'

                elif apdu.delivery_status.ill_service_type == '2':
                    apdu_map['service_type'] = u'копия документа'
                    order['type'] = 'copy'
                    order['copy_info'] = apdu.delivery_status.item_id['pagination']

                elif apdu.delivery_status.ill_service_type == '5':
                    apdu_map['service_type'] = u'бронирование документа'
                    order['type'] = 'reserve'

                order['type_title'] = apdu_map['service_type']
                order['can_delete'] = check_for_can_delete(transaction)

            else:
                #print apdu.delivery_status.type
                apdu_map['responder_note'] = apdu.delivery_status.responder_note
                if apdu.delivery_status.type == 'ILLAnswer':
                    apdu_map['reason_will_supply'] = apdu.delivery_status.results_explanation['wsr']['rws']
                    apdu_map['reason_will_supply_title'] = ''
                    if apdu_map['reason_will_supply'] in apdu_reason_will_supply:
                        apdu_map['reason_will_supply_title'] = apdu_reason_will_supply[apdu_map['reason_will_supply']]

                    apdu_map['unfilled_results'] = apdu.delivery_status.results_explanation['ur']['ru']
                    apdu_map['unfilled_results_title'] = ''
                    if apdu_map['unfilled_results'] in apdu_unfilled_results:
                        apdu_map['unfilled_results_title'] = apdu_unfilled_results[apdu_map['unfilled_results']]



            #apdu_map['record'] = res
            order['apdus'].append(apdu_map)

        orders.append(order)
        #if org_id in settings.LIBS:
    #    orgs[org_id] = settings.LIBS[org_id]
    #else:
    #    orgs[org_id] = org_id
    #orders_by_org[org_id] = orders



    response = render(request, 'orders/orders_list.html',
            {'orders': orders,
             'orgs': orgs})

    #response['Pragma'] = 'no-cache''
    #response['Cache-Control'] = 'no-cache must-revalidate proxy-revalidate'
    return response


@login_required
def order(request, order_type='', org_id=''):
    """
        order_type document || copy || reserve
    """
    #zgate_cookie = request.session.get('zgate_cookie', '')
    #zworker = ZWorker(zgate_cookie)
    #zworker.xml_name = catalogs['1']['xml']
    #zworker.xsl_name = catalogs['1']['xsl']
    #zworker.entry_point = reverse("zgate_index", args=['1'])

    #заменяем F на X чтобы cgi вернул XML. О как!

    if 'zstate' in request.GET:
        zgate_url = catalogs[catalog_id]['url']
        zstate = request.GET['zstate'].replace(' ', '+')
        (xml_record, cookies) = zworker.request(zgate_url + '?' + zstate.replace('1+F', '1+X'), cookies=request.COOKIES)
        #xml_record = zworker.make_get_request(request.GET['zstate'].replace(' F ', ' X '))

    try:
        tree = ET.XML(xml_record.encode('UTF-8'))
    except SyntaxError as e:
        # Если zgate вернул html страницу, то печатаем ее как ошибку ыыы


        compiled_regx = re.compile(r".*<body>(?P<section>.*).*</body>", re.IGNORECASE | re.MULTILINE)
        xml_record = xml_record.replace("\n",
            '|||') #временно меняем символы новой строки, чтобы сработала регулярка ыыы
        xml_record = re.match(compiled_regx, xml_record).group('section')
        xml_record = xml_record.replace("|||", '\n')
        response =  render(request, 'orders/orders_done.html',
                {'error': xml_record})
        return set_cookies_to_response(cookies, response)


    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])
    #return HttpResponse(u'Заказ сделан '+ order_type +'<br/>'+ org_id +'<br/>'+xml_record.decode('utf-8'))


    sender_id = 'belav' #id отправителя
    reciver_id = '19017901' #id получателя (огранизации)
    reserve_reciver_id = ''  #id конечного получателя (огранизации) при бронировании
    if order_type == 'reserve':
        reserve_reciver_id = org_id
    try:
        result = order_manager.order_document(
            order_type=order_type,
            sender_id=sender_id,
            reciver_id=reciver_id,
            xml_record=xml_record,
            reserve_reciver_id=reserve_reciver_id,
            comments=u'Сделать как можно скорее!'
        )
    except Exception as e:
        if settings.DEBUG == True:
            raise e
        else:
            raise RuntimeError(u'Ошибка при обработке заказа')
            #result = u'Заказ сделан '+ order_type +'<br/>'+xml_record.decode('utf-8')
    return render(request, 'orders/orders_done.html',
            {'result': result})


def ldap_org_search(district='', code=''):
    try:
        ldap_connection = LdapConnection(settings.LDAP)
        ldap_work = LdapWork(ldap_connection)
    except LdapWorkException as e:
        sys.stderr.write('Error of connection to LDAP server: ' + e.message)
        return None
    ldap_orgs = ldap_work.get_org_by_attr(district=district, code=code)
    return ldap_orgs


def org_by_district(request, catalog_id=''):
    if request.method == 'POST' and 'district' in request.POST:
        district = request.POST['district']

        libraries = Library.objects.filter(district=district).exclude(parent=None)


        orgs = []
        for org in libraries:
            orgs.append({'code': org.code, 'title': org.name})

        json = simplejson.dumps(orgs, ensure_ascii=False)
        return HttpResponse(json)
    else:
        return HttpResponse('Only post requests')


def org_by_code(request):
    if request.method == 'POST' and 'code' in request.POST:


        library = get_object_or_404(Library, code=request.POST['code'])

        org = {
            'code': library.code,
            'title': library.name,
            'postal_address': getattr(library,'postal_address', u'не указан'),
            'phone': getattr(library,'phone', u'не указан'),
            'email': getattr(library,'mail', u'не указан')
        }

        json = simplejson.dumps({'status': 'ok', 'org_info': org}, ensure_ascii=False)
        return HttpResponse(json)

    else:
        return HttpResponse('Only post requests')


@ajax_login_required
def make_order(request):
    if request.method != 'POST':
        return HttpResponse('Only post requests');
    order_type = request.POST.get('type', None)
    order_manager_id = request.POST.get('org_id', None) # организация, которая получит заказ



    order_time = datetime.datetime.now()

    order_copy_limit = 1
    order_document_limit = 2
    order_reserve_limit = 3


    user_order_times = UserOrderTimes.objects.filter(
        user=request.user,
        order_manager_id=order_manager_id,
        order_type=order_type,
        order_time__year=order_time.year,
        order_time__month=order_time.month,
        order_time__day=order_time.day
    ).count()

    if order_type == 'document':
        if user_order_times >= order_document_limit:
            return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'На сегодня Ваш лимит заказов на доставку в эту библиотеку исчерпан'},
                ensure_ascii=False))
    elif order_type == 'copy':
        if user_order_times >= order_copy_limit:
            return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'На сегодня Ваш лимит заказов на копию в эту библиотеку исчерпан'},
                ensure_ascii=False))
    elif order_type == 'reserve':
        if user_order_times >= order_reserve_limit:
            return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'На сегодня Ваш лимит заказов на бронирование в эту библиотеку исчерпан'},
                ensure_ascii=False))

    else:
        return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Неизвестный тип заказа'},
            ensure_ascii=False))



    catalog = get_object_or_404(ZCatalog, latin_title=request.POST['catalog_id'])
    zgate_url = catalog.url

    zstate = 'present+' + request.POST['zsession'] +\
             '+default+' + request.POST['zoffset'] +\
             '+1+X+1.2.840.10003.5.28+' + catalog.default_lang

    (xml_record, cookies) = zworker.request(zgate_url + '?' + zstate, cookies=request.COOKIES)

    #определяем, сколько раз пользователь сдлела заказ за сегодня


    try:
        tree = ET.XML(xml_record)
    except SyntaxError as e:
        return HttpResponse(json_error(u'Заказ не выполнен. Возможно, время сессии истекло'))



    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])

    library = None
    try:
        library = Library.objects.get(code=order_manager_id)
    except Library.DoesNotExist:
        return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Организация не найдена'}))

    def get_first_recivier_code(library):
        ancestors = library.get_ancestors()
        for ancestor in ancestors:
            if ancestor.ill_service and ancestor.ill_service.strip():
                return ancestor.code
        return None

    # если у библиотеки указан ill адрес доставки, то пересылаем заказ ей
    if library.ill_service and library.ill_service.strip():
        manager_id = ''
        reciver_id = library.code

    # иначе ищем родителя, у которого есть адрес доставки
    else:
        manager_id = library.code
        reciver_id = get_first_recivier_code(library)

        if not reciver_id:
            return  HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Организация не может получать заявки'}))


    sender_id = request.user.username #id отправителя
    copy_info =  request.POST.get('copy_info', '')


    try:
        order_manager.order_document(
            order_type=order_type,
            sender_id=sender_id,
            reciver_id=reciver_id,
            manager_id=manager_id,
            xml_record=xml_record,
            comments=request.POST.get('comments', ''),
            copy_info=copy_info
        )
        user_order_times = UserOrderTimes(user=request.user, order_type=order_type, order_manager_id=order_manager_id)
        user_order_times.save()
    except Exception as e:
        if settings.DEBUG == True:
            return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Ошибка при обработке заказа' + str(e)},
                ensure_ascii=False))
        else:
            return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Ошибка при обработке заказа'},
                ensure_ascii=False))
            #result = u'Заказ сделан '+ order_type +'<br/>'+xml_record.decode('utf-8')

    return HttpResponse(simplejson.dumps({'status': 'ok'}, ensure_ascii=False));


@login_required
def delete_order(request, order_id=''):
    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])
    transactions = order_manager.get_order(order_id=order_id.encode('utf-8'), user_id=request.user.username)
    if len(transactions):
        if check_for_can_delete(transactions[0]):
            pass
    order_manager.delete_order(order_id=order_id.encode('utf-8'), user_id=request.user.username)

    return redirect(reverse('orders_index'))

    
