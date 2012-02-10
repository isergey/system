# encoding: utf-8
import re
import datetime
import sunburnt
import simplejson as json
from django.conf import settings
from django.shortcuts import render, HttpResponse
from models import AskLog

def index(request):
    answer = {'answer':u'Какая-то борода...'}
    if request.method == 'POST':
        SOLR_ADDRESS = settings.HELPER_SOLR_ADDRESS
        try:
            si = sunburnt.SolrInterface(SOLR_ADDRESS)
        except AttributeError:
            answer = json.dumps({'answer':u'Я заболел и не могу сейчас разговаривать :-('}, ensure_ascii=False)
            return HttpResponse(answer)

        query = None
        request_terms = request.POST.get('ask', None)
        terms = []
        if request_terms:
            terms = re.findall(ur'\w+', request_terms,re.UNICODE)

            query = si.Q()


        for term in terms:
            query = (query | si.Q(ask_t_ru=term))

        results = None
        if query:
            results = si.query(query).execute()

        if results:
            AskLog(normalize=request_terms, not_normalize=request_terms, answered=True).save()
            text = results[0]['answer_t']
            if text.strip() == '{% date %}':
                text = u'Текущие дата и время ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            answer = {'answer': text}
        else:
            AskLog(normalize=request_terms, not_normalize=request_terms, answered=False).save()
            answer = {'answer': u'Возможно вы найдете ответ, нажав <a href="http://www.google.ru/search?q='+ request.POST.get('ask', u'ксоб') +u'+site:http%3A%2F%2Fksob.spb.ru" target="_blank">сюда</a>:-) Скоро я сам найду ответ!'}

    answer = json.dumps(answer, ensure_ascii=False)
    return HttpResponse(answer)
