# -*- coding: utf-8 -*-
from django.db import models
NEWS_TYPE_CHOICES = (
    (0, u'Общедоступная'),
    (1, u'Профессиональная'),
)
class News(models.Model):
    title = models.CharField(verbose_name=u"Заголовок новости",
                             max_length=128, null=False, blank=False)

    teaser = models.CharField(verbose_name=u"Тизер новости",
                             max_length=256, null=False, blank=False)

    content = models.TextField(verbose_name=u"Текст новости",
                               null=False, blank=False)

    type = models.IntegerField(choices=NEWS_TYPE_CHOICES,
                               verbose_name=u"Тип новости", default=0)

    published = models.BooleanField(verbose_name=u"Опубликована",
                                    default=True)

    pub_date = models.DateTimeField(verbose_name=u"Дата публикации",
                                    auto_now_add=True)

    def __unicode__(self):
        return self.title

    def type_title(self):
        for choice in NEWS_TYPE_CHOICES:
            if self.type == choice[0]:
                return choice[1]
        return self.type
    
    class Meta:
        verbose_name = u"новость"
        verbose_name_plural = u"новости"
