#from django.conf import settings
#from django.db.models.signals import post_syncdb
#from django.contrib.auth.models import Group
#def sync_groups(*args, **kw):
#    if kw['sender'].__name__ != 'django.contrib.auth.models': return
#
#    for ldap_group in settings.LDAP_USERS_GROUPS:
#        p, created = Group.objects.get_or_create(name=ldap_group)
#        if created:
#            print 'group ',  ldap_group, 'has created'
#
#
#post_syncdb.connect(sync_groups)

