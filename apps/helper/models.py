# -*- coding: utf-8 -*-
import datetime

from django.db import models



class AskLog(models.Model):

    normalize = models.CharField(max_length=256, verbose_name=u'Нормализованный вопрос', db_index=True)
    not_normalize = models.CharField(max_length=256, verbose_name=u'Ненормализованный вопрос', db_index=True)
    answered = models.BooleanField(verbose_name=u"Ответ был найден?",default=False, db_index=True)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=True, db_index=True)

    class Meta:
        verbose_name = u"Вопрос помощнику"
        verbose_name_plural = u"Вопросы помощнику"