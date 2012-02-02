# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required

from apps.events.models import Event
from forms import EventForm
from django.forms.models import model_to_dict



def inset_one(event):
    """
    insert event to solr index
    """
    si = sunburnt.SolrInterface(settings.SOLR_ADDRESS)
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

    return render(request, 'events/administration/events_list.html',
                              {'events_list': events_list,
                               'active_module': 'events'})
@login_required
@permission_required_or_403('events.add_event')
def create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            inset_one(event)
            return HttpResponseRedirect(reverse('administration_events_index'))
    else:
        form = EventForm()

    return render(request, 'events/administration/events_create.html',
                              {'form': form,
                               'active_module': 'events'})

@login_required
@permission_required_or_403('events.change_event')
def edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            inset_one(event)
            return HttpResponseRedirect(reverse('administration_events_index'))
    else:

        form = EventForm(model_to_dict(event),instance=event)
    return render(request, 'events/administration/events_edit.html',
                              {'form': form,
                               'event':event,
                               'active_module': 'events'})

@login_required
@permission_required_or_403('events.delete_event')
def delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return HttpResponseRedirect(reverse('administration_events_index'))



