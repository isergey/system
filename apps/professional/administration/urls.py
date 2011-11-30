# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.professional.administration.views',
    url(r'^$', 'index', name="administration_professional_index"),
    url(r'^edit/$', 'edit', name="administration_professional_edit"),
)