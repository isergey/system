# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from guardian.decorators import permission_required_or_403
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from apps.guestbook.models import Feedback
from forms import FeedbackForm
from django.forms.models import model_to_dict


@permission_required_or_403('guestbook.add_feedback')
def index(request):
    feedbacks = Feedback.objects.all().order_by('-add_date')
    paginator = Paginator(feedbacks, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        feedbacks_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        feedbacks_list = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'guestbook/administration/messages_list.html',
                              {'feedbacks_list': feedbacks_list,
                               'active_module': 'guestbook'})


@permission_required_or_403('guestbook.change_feedback')
def edit(request, message_id):
    feedback = get_object_or_404(Feedback, id=message_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_guestbook_index'))
    else:
        form = FeedbackForm(model_to_dict(feedback),instance=feedback)
    return direct_to_template(request, 'guestbook/administration/edit_message.html',
                              {'form': form,
                               'feedback':feedback,
                               'active_module': 'guestbook'})

@permission_required_or_403('guestbook.delete_feedback')
def delete(request, message_id):
    feedback = get_object_or_404(Feedback, id=message_id)
    feedback.delete()
    return HttpResponseRedirect(reverse('administration_guestbook_index'))

