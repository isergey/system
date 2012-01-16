#encoding: utf-8

from django.contrib.auth.decorators import login_required
from django. shortcuts import render, HttpResponse, Http404, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from libs import pyaz
from libs import pymarc

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

cache = {}
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
            record = pymarc.Record(data=zrecord, to_unicode=True, encoding='utf-8')
            #record.add_field(pymarc.Field(tag='993', indicators=(' ', ' '), subfields=('a', record.as_md5(),)))
            #record = highlighting(fuzzy_terms, record)
            #print record
            search_results.append(
                    {
                    'number': number,
                    'record': record.as_dict(),
                    'zrecord': zrecord
                }
            )
        cache['zrecords'] = search_results
        return (search_results, zrecords)

def index(request):
    term = request.GET.get('term', None)
    if term:
        try:
            search_results = do_search(request)
        except pyaz.ZConnectionExceptiony:
            return HttpResponse(u'Невозможно установть соединение с библиографической базой. Попробуйте позднее.')
        print search_results
        return render(request, 'searcher/searcher.html', {
            'search_results': search_results[0],
            'pages_list':search_results[1]
            })
    return render(request, 'searcher/searcher.html')

def detail(request):
    number = request.GET.get('number', None)
    zrecords = cache['zrecords']
    if number and zrecords:
        number = int(number)
        for zrecord in zrecords:
            print zrecord['number']
            if int(number) == zrecord['number']:
                return render(request, 'searcher/detail.html', {
                    'record':zrecord['record']
                })