# encoding: utf-8
from django.conf.urls.defaults import *


urlpatterns = patterns('helper.views',
    url(r'^$', 'index', name="helper_index"),
)



