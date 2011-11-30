# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Administration(models.Model):
#    fake = models.CharField(verbose_name=u"fake",
#                             max_length=255, null=False, blank=False, unique=True)
    class Meta:
        verbose_name = u"администрирование"
        permissions = (
            ('can_access', u'Имеет доступ'),
        )