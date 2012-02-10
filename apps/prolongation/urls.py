# encoding: utf-8
from django.conf.urls.defaults import *


urlpatterns = patterns('prolongation.views',
    url(r'^$', 'index', name="prolongation_index"),
    url(r'^form/$', 'prolongation', name="prolongation_prolongation"),
    url(r'^detail/(?P<id>\d+)/$', 'prolongation_user_detail', name="prolongation_prolongation_user_detail"),
    url(r'^admin/checkout/$', 'checkout', name="prolongation_checkout"),
    url(r'^admin/checkout/inlib/(?P<id>\d+)/$', 'checkout_by_library', name="prolongation_checkout_by_library"),
    url(r'^admin/checkout/detail/(?P<id>\d+)/$', 'prolongation_detail', name="prolongation_prolongation_detail"),
    url(r'^admin/take_to_process/(?P<id>\d+)/$', 'take_to_process', name="prolongation_take_to_process"),
    url(r'^admin/complete/(?P<id>\d+)/$', 'complete', name="prolongation_complete"),
    url(r'^admin/reject/(?P<id>\d+)/$', 'reject', name="prolongation_reject"),
)



