# -*- coding: utf-8 -*-
from django.db import models

class Feedback(models.Model):

    name = models.CharField(verbose_name=u"Имя",
                             max_length=256, null=False, blank=False)

    email = models.EmailField(verbose_name=u"Email",
                             max_length=512, null=False, blank=False, help_text=u'Не будет выводиться')

    message = models.TextField(verbose_name=u"Текст отзыва",
                             max_length=5120, null=False, blank=False)

    published = models.BooleanField(verbose_name=u"Опубликовано",
                                    null=False, blank=False, default=False)
    
    add_date = models.DateTimeField(verbose_name=u"Дата добавления",
                                    auto_now_add=True)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"отзыв"
        verbose_name_plural = u"отзывы"