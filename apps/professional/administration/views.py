# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from guardian.decorators import permission_required_or_403
from django.forms.models import model_to_dict
from apps.professional.models import Professional
from forms import ProfessionalForm

@permission_required_or_403('professional.change_professional')
def index(request):
    try:
        professional = Professional.objects.get(id__gt=0)
    except Professional.DoesNotExist:
        professional = Professional()
        professional.content = u'необходимо отредактировать текст'
        professional.save()
    
    return direct_to_template(request, 'professional/administration/show.html',
                              {'content': professional.content,
                               'active_module': 'professional'})


@permission_required_or_403('professional.change_professional')
def edit(request):
    professional = Professional.objects.get(id__gt=0)
    if request.method == 'POST':
        form = ProfessionalForm(request.POST, instance=professional)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('administration_professional_index'))
    else:
        form = ProfessionalForm(model_to_dict(professional),instance=professional)
    return direct_to_template(request, 'professional/administration/edit.html',
                              {'form': form,
                               'active_module': 'professional'})
