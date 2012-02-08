# encoding: utf-8
import sunburnt
import simplejson as json
from django.shortcuts import render, HttpResponse


def index(request):
    answer = {'answer':u'Какая-то борода...'}
    if request.method == 'POST':
        si = sunburnt.SolrInterface('http://127.0.0.1:8983/solr/')

        query = None
        terms = request.POST.get('ask', None)

        if terms:
            terms = terms.split()
            query = si.Q()

        for term in terms:
            query = (query | si.Q(text_ru=term))

        results = None
        if query:
            results = si.query(query).execute()

        if results:
            answer = {'answer': results[0]['answer_t']}
        else:
            answer = {'answer': u'Возможно вы найдете ответ, нажав <a href="http://www.google.ru/search?q='+ request.POST.get('ask', u'ксоб') +u'+site:http%3A%2F%2Fksob.spb.ru" target="_blank">сюда</a>:-) Скоро я сам найду ответ!'}

    answer = json.dumps(answer, ensure_ascii=False)
    return HttpResponse(answer)
