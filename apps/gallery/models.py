# -*- coding: utf-8 -*-
from django.db import models

class Collection(models.Model):
    title = models.CharField(verbose_name=u"Название альбома",
                             max_length=255, null=False, blank=False)
    latin_title = models.SlugField(unique=True, verbose_name=u"Название альбомы (латинскими буквами)")
    description = models.TextField(verbose_name=u"Описание альбома",
                               null=False, blank=False)
    add_date_time = models.DateTimeField(verbose_name=u"Дата добавления",
                                         auto_now_add=True, null=False, blank=False)
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = u"альбом"
        verbose_name_plural = u"альбомы"

        permissions = (
            ('create_collection', u'Создание альбома'),
            ('view_collection', u'Просмотр альбома'),
            ('delete_collection', u'Удаление альбома'),
            ('edit_collection', u'Редактирование альбома'),
        )

class CollectionImage(models.Model):
    collection = models.ForeignKey(Collection)
    title = models.CharField(verbose_name=u"Название изображения",
                             max_length=255, blank=True)
    comments = models.TextField(verbose_name=u"Комментарии к изображению",
                               max_length=255,blank=True)
    file_name = models.CharField(max_length=64, blank=False)
    add_date_time = models.DateTimeField(verbose_name=u"Дата добавления",
                                         auto_now_add=True, null=False, blank=False)


    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u"изображение"
        verbose_name_plural = u"изображения"

        permissions = (
            ('upload_image', u'Загрузка изображения'),
            ('view_image', u'Просмотр изображения'),
            ('delete_image', u'Удаление изображения'),
            ('edit_image', u'Редактирование изображения'),
        )

