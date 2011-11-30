# -*- coding: utf-8 -*-
from django import template
from apps.events.models import Event
register = template.Library()

@register.inclusion_tag('events/events_calendar1.html')
def event_calendar(y=0, m=0):

    from datetime import date
    import calendar
    today = date.today()
    year = today.year
    month = today.month
    if y: year = y
    if m: month = m
    weeks = calendar.monthcalendar(year, month)

    events = Event.objects.filter(start_date__year=year, start_date__month=month)
    print events
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
            for event in events:
                if event.start_date.day == day:
                    day_events['events'].append({'id': event.id,
                                                 'title': event.title,
                                                 'desc':event.description })
            week_events.append(day_events)
        calendar_of_events.append(week_events)
    return {'calendar': calendar_of_events }