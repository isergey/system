# encoding: utf-8 -*-
from reginlib.models import RegistrationManager

from django import template
from django.contrib.auth.models import User
register = template.Library()

@register.filter
def is_reg_manager(user):
    if isinstance(user, User) and user.is_authenticated():
        count = RegistrationManager.objects.filter(user=user).count()
        if count:
            return True
    return False
