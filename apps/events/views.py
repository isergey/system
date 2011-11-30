# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from models import Event, EventComment, FavoriteEvent, EventRemember
from forms import CommentEventForm, AddToFavoriteForm

import datetime

def index(request):
    events_list = Event.objects.all()
    return direct_to_template(request, 'events/events_list.html',
                              {'events_list': events_list,
                               'active_events':True})


def filer_by_date(request, day='', month='', year=''):
    events_list = Event.objects.filter(start_date__year=year, start_date__month=month, start_date__day=day)
    return direct_to_template(request, 'events/events_list.html',
                              {'events_list': events_list,
                               'active_events':True})


def show(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = CommentEventForm()
    comments = EventComment.objects.filter(event=event)
    return direct_to_template(request, 'events/events_show.html',
                              {'event': event,
                               'form': form,
                               'comments': comments,
                               'active_events':True})


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
                day_events['events'].append({'title':u'Название события1', 'desc':u'Описание'})
                day_events['events'].append({'title':u'Название события2', 'desc':u'Описание'})

            week_events.append(day_events)
        calendar_of_events.append(week_events)
    return direct_to_template(request,'events/events_calendar.html', {
                                'calendar': calendar_of_events
                                }
    )

@login_required
def favorits(request):
    user = request.user
    fav_events = FavoriteEvent.objects.filter(user=user)

    return direct_to_template(request, 'events/events_favorits.html',
                              {'fav_events': fav_events,
                               'active_events':True})

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

    return direct_to_template(request, 'events/events_add_to_favorits_form.html',
                              { 'event': event,
                                'form': form,
                                'active_events':True})

@login_required
def favorits_detail(request, event_id):
    favorite_event = get_object_or_404(FavoriteEvent, id=event_id)
    remembers = EventRemember.objects.filter(favorite_event=favorite_event)

    return direct_to_template(request, 'events/events_favorite_detail.html',
                              {'favorite_event': favorite_event,
                               'remembers': remembers,
                               'active_events':True})



@login_required
def comment_event(request, event_id):
    if request.method == 'POST':
        form = CommentEventForm(request.POST)
        if form.is_valid():
            event = get_object_or_404(Event, id=event_id)
            user = request.user
            comment = EventComment(event=event,user=user,text=form.cleaned_data['text'])
            comment.save()
        else:
            print form.errors
    return HttpResponseRedirect(reverse('events_show', args=[event_id]))
    