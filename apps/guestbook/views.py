from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from models import Feedback
from forms import FeedbackForm


def index(request):
    feedbacks = Feedback.objects.filter(published=True).order_by('-add_date')
    paginator = Paginator(feedbacks, 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        feedback_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        feedback_list = paginator.page(paginator.num_pages)


    return render(request, 'guestbook/feedback_list.html',
                              {'feedback_list': feedback_list,
                               'module':'guestbook'})

def add_feedback(request, conference_slug=''):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('guestbook_index'))
    else:
        form = FeedbackForm()
    return render(request, 'guestbook/feedback_add.html',
                              {'form': form,
                               'module':'guestbook',})