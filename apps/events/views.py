# -*- coding: utf-8 -*-
from libs import sunburnt
import datetime

from django.utils.html import escape, mark_safe, strip_tags, clean_html
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import  render, HttpResponse
from models import Event, EventComment, FavoriteEvent, EventRemember
from forms import CommentEventForm, AddToFavoriteForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage


from common.functions import replace_illegal


def index(request):

    paginator = Paginator(Event.objects.all().order_by('-start_date'), 20)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        object_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        object_list = paginator.page(paginator.num_pages)

    return render(request, 'events/events_list.html', {
        'events_list': object_list.object_list,
        'object_list': object_list,
        'active_events': True
    })


def filer_by_date(request, day='', month='', year=''):
    events_list = Event.objects.filter(start_date__year=year, start_date__month=month, start_date__day=day)
    return render(request, 'events/events_list.html',
            {'events_list': events_list,
             'active_events': True})


def show(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = CommentEventForm()
    comments = EventComment.objects.filter(event=event)
    return render(request, 'events/events_show.html', {
        'event': event,
        'form': form,
        'comments': comments,
        'active_events': True
    })


class PageStub:
    def __init__(self, num_items):
        self.num_items = num_items
    def __len__(self):
        return self.num_items

    def __getslice__(self,start, end):
        return xrange(start, end)




def search(request):
    attr = request.GET.get('attr', None)
    term = request.GET.get('term', None)
    if not attr and not term:
        return HttpResponse(u'Введите поисковое выражение')

    print settings.SOLR_ADDRESS

    si = sunburnt.SolrInterface(settings.SOLR_ADDRESS)
    events_list = []
    if attr:
        kwargs={attr:term}

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        limit = 10
        offset = (page-1) * limit
        results = si.query(**kwargs).paginate(start=offset, rows=limit).execute()
        paginator = Paginator(PageStub(results.result.numFound), limit)

        object_list = None
        try:
            object_list = paginator.page(page)
        except (EmptyPage, InvalidPage):
            object_list = paginator.page(paginator.num_pages)


        ids = []
        for result in results:
            ids.append(result['id'])
        events_list = Event.objects.filter(id__in=ids)
    return render(request, 'events/events_list.html', {
        'events_list': events_list,
        'active_events': True,
        'object_list': object_list
    })



def calendar(request):
    from datetime import date
    import calendar

    today = date.today()
    weeks = calendar.monthcalendar(today.year, today.month)
    calendar_of_events = []
    for week in weeks:
        week_events = []
        for day in week:
            day_events = {
                'day': 0,
                'today': False,
                'events': [],
                }
            day_events['day'] = day
            if day == today.day: day_events['today'] = True
            if day == 15:
                day_events['events'].append({'title': u'Название события1', 'desc': u'Описание'})
                day_events['events'].append({'title': u'Название события2', 'desc': u'Описание'})

            week_events.append(day_events)
        calendar_of_events.append(week_events)
    return render(request, 'events/events_calendar.html', {
        'calendar': calendar_of_events
    }
    )


@login_required
def favorits(request):
    user = request.user
    fav_events = FavoriteEvent.objects.filter(user=user)

    return render(request, 'events/events_favorits.html',
            {'fav_events': fav_events,
             'active_events': True})


@login_required
def add_to_favorits(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = AddToFavoriteForm(request.POST)
        if form.is_valid():
            user = request.user
            try:
                favorite_event = FavoriteEvent.objects.get(user=user, event=event)
            except FavoriteEvent.DoesNotExist:
                favorite_event = FavoriteEvent(user=user, event=event)
                favorite_event.save()
            for rem_day in form.cleaned_data['days_for_remember']:
                rem_day = int(rem_day)
                if rem_day < 1: continue
                differense = datetime.timedelta(days=rem_day)
                remember_date = event.start_date - differense
                event_remember = EventRemember(favorite_event=favorite_event, remember_date=remember_date)
                event_remember.save()
            return HttpResponseRedirect(reverse('events_favorits'))
    else:
        form = AddToFavoriteForm()

    return render(request, 'events/events_add_to_favorits_form.html',
            {'event': event,
             'form': form,
             'active_events': True})


@login_required
def favorits_detail(request, event_id):
    favorite_event = get_object_or_404(FavoriteEvent, id=event_id)
    remembers = EventRemember.objects.filter(favorite_event=favorite_event)

    return render(request, 'events/events_favorite_detail.html',
            {'favorite_event': favorite_event,
             'remembers': remembers,
             'active_events': True})


@login_required
def comment_event(request, event_id):
    if request.method == 'POST':
        form = CommentEventForm(request.POST)
        if form.is_valid():
            event = get_object_or_404(Event, id=event_id)
            user = request.user
            comment = EventComment(event=event, user=user, text=form.cleaned_data['text'])
            comment.save()
        else:
            print form.errors
    return HttpResponseRedirect(reverse('events_show', args=[event_id]))



def insert(request):
    """
    insert to solr index all events
    """
    si = sunburnt.SolrInterface(settings.SOLR_ADDRESS)
    events_list = Event.objects.all()

    for event in events_list:
        doc = {
            'id': unicode(event.id),
            'event_name_t':  replace_illegal(event.title),
            'event_name_t_ru':  replace_illegal(event.title),
            'address_t': replace_illegal(event.address),
            'address_t_ru': replace_illegal(event.address),
            'any_t_ru': replace_illegal(' '.join((event.title, event.address)))
        }
        si.add(doc)
    si.commit()
    return HttpResponse(u'Ok')