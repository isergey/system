# encoding: utf-8
from django.conf.urls.defaults import *


urlpatterns = patterns('searcher.views',
    url(r'^$', 'index', name="searcher_index"),
    url(r'^detail$', 'detail', name="searcher_detail"),
#    url(r'^detail/(?P<id>\d+)/$', 'registration_user_detail', name="reginlib_registration_user_detail"),
#    url(r'^admin/checkout/$', 'checkout', name="reginlib_checkout"),
#    url(r'^admin/checkout/(?P<id>\d+)/$', 'checkout_by_library', name="reginlib_checkout_by_library"),
#    url(r'^admin/detail/(?P<id>\d+)/$', 'registration_detail', name="reginlib_registration_detail"),
#    url(r'^admin/take_to_process/(?P<id>\d+)/$', 'take_to_process', name="reginlib_take_to_process"),
#    url(r'^admin/complete/(?P<id>\d+)/$', 'complete', name="reginlib_complete"),
#    url(r'^admin/reject/(?P<id>\d+)/$', 'reject', name="reginlib_reject"),
)



