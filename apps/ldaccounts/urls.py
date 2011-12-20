# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ldaccounts.views',
    url(r'^$', 'index', name="ldaccounts_index"),
    url(r'^users/$', 'get_users', name="ldaccounts_users"),
    url(r'^users/(?P<year>\d+)/$', 'get_users', name="ldaccounts_users"),
    url(r'^users/(?P<year>\d+)/(?P<month>\d+)/$', 'get_users', name="ldaccounts_users"),
    url(r'^users/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'get_users', name="ldaccounts_users"),

    url(r'^registration/$', 'registration', name="ldaccounts_registration"),
    url(r'^mail/$', 'test_mail', name="ldaccounts_mail"),
    url(r'^confirm/(?P<hash>[a-h0-9]{1,32})/$', 'confirm_registration', name="ldaccounts_confirm"),
    url(r'^remember/$', 'remember_password', name="ldaccounts_remember_password"),
    url(r'^reset/(?P<hash>[a-h0-9]{1,32})/$', 'reset_password', name="ldaccounts_reset_password"),
    url(r'^api/users/getuser/$', 'api_get_user', name="ldaccounts_api_get_user"),
)

#urlpatterns += (
#    url(r'^api/users/getuser/$', 'api_get_user', name="ldaccounts_api_get_user"),
#)



"""
urlpatterns = patterns('apps.ldaccounts.views',
    url(r'^$', 'index', name="ldaccounts_index"),
    url(r'^users/$', 'get_users', name="ldaccounts_users"),
    
    url(r'^groups/$', 'groups_index', name="ldaccounts_groups_index"),
    url(r'^groups/create/$', 'group_create', name="ldaccounts_groups_create"),
    url(r'^groups/edit/(?P<id>\d+)/$', 'group_edit', name="ldaccounts_groups_edit"),
    url(r'^groups/delete/(?P<id>\d+)/$', 'group_delete', name="ldaccounts_groups_delete"),

    url(r'^permissions/$', 'permissions_index', name="ldaccounts_permissions_index"),
    url(r'^permissions/create/(?P<app_label>[0-9a-z_]+)/$', 'permission_create', name="ldaccounts_permissions_create"),
    url(r'^permissions/edit/(?P<id>\d+)/$', 'permission_edit', name="ldaccounts_permissions_edit"),
    url(r'^permissions/delete/(?P<id>\d+)/$', 'permission_delete', name="ldaccounts_permissions_delete"),

    url(r'^users/$', 'users_index', name="ldaccounts_users_index"),
    url(r'^users/create/$', 'user_create', name="ldaccounts_users_create"),
    url(r'^users/edit/(?P<id>\d+)/$', 'user_edit', name="ldaccounts_users_edit"),
    url(r'^users/delete/(?P<id>\d+)/$', 'user_delete', name="ldaccounts_users_delete"),

    url(r'^registration/$', 'registration', name="ldaccounts_registration"),
    url(r'^mail/$', 'test_mail', name="ldaccounts_mail"),
    url(r'^confirm/(?P<hash>[a-h0-9]{32})/$', 'confirm_registration', name="ldaccounts_confirm"),
    
    url(r'^api/users/getuser/$', 'api_get_user', name="ldaccounts_api_get_user"),
    #(r'^login/$', 'login'),
    #(r'^logout/$', 'logout'),
    
    #(r'^users/$', 'users_list'),
    
    #(r'^groups/$', 'groups'),
    #(r'^groups/add$', 'groups_add'),
    #(r'^groups/remove$', 'groups_remove'),
)
"""
