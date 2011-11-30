# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403



import uuid
import Image
import os
import binascii
import shutil

@login_required
def index(request):
    return HttpResponse(u'Ok')


