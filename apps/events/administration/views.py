# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required

from apps.events.models import Event
from forms import EventForm
from django.forms.models import model_to_dict

@login_required
@permission_required_or_403('events.add_event')
def index(request):
    events = Event.objects.all().order_by('-id')
    paginator = Paginator(events, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        events_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        events_list = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'events/administration/events_list.html',
                              {'events_list': events_list,
                               'active_module': 'events'})
@login_required
@permission_required_or_403('events.add_event')
def create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_events_index'))
    else:
        form = EventForm()

    return direct_to_template(request, 'events/administration/events_create.html',
                              {'form': form,
                               'active_module': 'events'})

@login_required
@permission_required_or_403('events.change_event')
def edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_events_index'))
    else:

        form = EventForm(model_to_dict(event),instance=event)
    return direct_to_template(request, 'events/administration/events_edit.html',
                              {'form': form,
                               'event':event,
                               'active_module': 'events'})

@login_required
@permission_required_or_403('events.delete_event')
def delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return HttpResponseRedirect(reverse('administration_events_index'))
