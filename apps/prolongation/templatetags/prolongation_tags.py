# encoding: utf-8 -*-
from prolongation.models import ProlongationManager

from django import template
from django.contrib.auth.models import User
register = template.Library()

@register.filter
def is_prolongation_manager(user):
    if isinstance(user, User) and user.is_authenticated():
        count = ProlongationManager.objects.filter(user=user).count()
        if count:
            return True
    return False
