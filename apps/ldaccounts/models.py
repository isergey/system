# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class RegConfirm(models.Model):
    hash = models.CharField(max_length=32, db_index=True, null=False, blank=False)
    user = models.ForeignKey(User)

class PasswordRemember(models.Model):
    hash = models.CharField(max_length=32, db_index=True)
    email = models.EmailField(max_length=64)
    activated = models.BooleanField(default=False, db_index=True)
