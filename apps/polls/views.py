# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic.simple import direct_to_template
from models import Poll, Choice, PolledUser


def index(request):
    polls = Poll.objects.filter(published=True).order_by('-id')[:100]
    paginator = Paginator(polls, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        polls_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        polls_list = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'polls/polls_list.html',
                              {'polls_list': polls_list,
                               'module': 'polls'})


def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, published=True)

    if not poll.is_active():
        return HttpResponseRedirect(reverse('polls_results', args=(poll.id,)))

    poller_id = None
    if request.user.is_authenticated():
        poller_id = request.user.username
    elif request.session.session_key:
        poller_id = request.session.session_key

    votes_in_poll = PolledUser.objects.filter(poller_id=poller_id,poll=poll).count()
    if votes_in_poll:
        return results(request, poll_id, poll)


    if request.method == 'POST' and 'answer' in request.POST:
        if poll.poll_type == 'radio':
            #Голосуем за первый попавшийся id 
            choices = Choice.objects.filter(poll=poll, pk__in=request.POST.getlist('answer'))[:1]
        elif poll.poll_type == 'checkboxes':
            choices = Choice.objects.filter(poll=poll, pk__in=request.POST.getlist('answer'))
        else:
            raise ValueError(u'Type of poll must be "radio" or "checkboxes"')

        for choice in choices:
            choice.votes += 1
            choice.save()

        polled_user = PolledUser(poller_id=poller_id, poll=poll)
        polled_user.save()


        return results(request, poll_id, poll)

    choices = Choice.objects.filter(poll=poll).order_by('-sort')

    return direct_to_template(request, 'polls/polls_show.html',
                              {'poll': poll,
                               'choices': choices,
                               'module': 'polls'})


# Внимание! Может вызываться из show
def results(request, poll_id, poll=None):

    if not poll:
        poll = get_object_or_404(Poll, id=poll_id, published=True)

    choices = Choice.objects.filter(poll=poll).order_by('-sort')[:100]

    choices_dicts = []
    # суммарное число ответов
    summ_number_of_answers = 0

    # сортируем ответы по количеству голосов, начиная от большего к меньшему
    # и извлекаем максимальное значение
    max_choice_answers = 0
    if len(choices):
        max_choice_answers = sorted(choices, key=lambda x: x.votes, reverse=True)[0].votes
        if max_choice_answers == 0: max_choice_answers = 1
    
    for choice in choices:
        choices_dicts.append({
            'choice': choice,
            # Процент от макимального значения
            'percent_from_max': int(choice.votes * 100 / max_choice_answers * 0.85),
            })
        summ_number_of_answers += choice.votes

    if summ_number_of_answers == 0:
        summ_number_of_answers = 1;
    for choices_dict in choices_dicts:
        # Процент от суммарного значения голосов
        choices_dict['percent_from_sum_votes'] = '%0.2f' %\
                                                 (choices_dict['choice'].votes * 100.0 / summ_number_of_answers)

    show_results = False
    message = u"Спасибо за ответ. Ваше мнение очень важно для нас!"
    if request.method == 'GET':
        if poll.show_results_after_end_poll:
            message = u"Результаты будут доступны после завершения опроса."
        else:
            message = u"Результаты опроса не доступны."
    elif request.method == 'POST':
        if poll.show_results_after_end_poll:
            message = u"Спасибо за ответ! Результаты будут доступны после завершения опроса!"

    # если голосование активно и разрешено показывать результаты
    if poll.is_active() and poll.show_results_on_vote:
        show_results = True

    # если голосование НЕ активно и разрешено показывать результаты
    # после завершения голосования
    elif not poll.is_active() and poll.show_results_after_end_poll:
        show_results = True

    if request.is_ajax():
        return direct_to_template(request, 'polls/polls_ajax_results.html',
                                  {'poll': poll,
                                   'choices_dicts': choices_dicts,
                                   'show_results': show_results,
                                   'message': message})


    return direct_to_template(request, 'polls/polls_results.html',
                              {'poll': poll,
                               'choices_dicts': choices_dicts,
                               'show_results': show_results,
                               'message': message,
                               'module': 'polls'})
