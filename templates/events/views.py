# -*- coding: utf-8 -*-

from models import Event

def index(request):
    events_list = Event.objects.all()
    return direct_to_template(request, 'events/events_list.html',
                              {'events_list': events_list,
                               'active_events':True})

def show(request, event_id):
    events_list = get_object_or_404(Event, id=event_id)
    return direct_to_template(request, 'events/events_show.html',
                              {'event': event,
                               'active_events':True})