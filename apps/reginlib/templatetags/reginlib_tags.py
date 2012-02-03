# encoding: utf-8 -*-
from reginlib.models import RegistrationManager

from django import template

register = template.Library()

@register.filter
def is_reg_manager(user):
    count = RegistrationManager.objects.filter(user=user).count()
    if count:
        return True
    return False
