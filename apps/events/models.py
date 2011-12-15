# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class EventCategory(models.Model):
    name = models.CharField(verbose_name=u'Категория события', max_length=64, unique=True, db_index=True)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"категория мероприятий"
        verbose_name_plural = u"категории мероприятий"



# Create your models here.
class Event(models.Model):

    title = models.CharField(verbose_name=u"Название (макс. 255 символов)",
                             max_length=255, null=False, blank=False, unique=True)
    teaser = models.CharField(verbose_name=u"Краткое описание (макс. 255 символов)",
                             max_length=255, null=False, blank=False)
    description = models.TextField(verbose_name=u"Описание",
                                   null=False, blank=False)
    start_date = models.DateTimeField(verbose_name=u"Дата начала",
                                      null=False, blank=False, db_index=True)
    end_date = models.DateTimeField(verbose_name=u"Дата окончания",
                                    null=False, blank=False, db_index=True)
    address = models.CharField(verbose_name=u"Адрес места проведения (макс. 255 символов)",
            max_length=255, blank=True)
    active = models.BooleanField(verbose_name=u"Активно",
                                 default=True, db_index=True)
    auto_delete = models.BooleanField(verbose_name=u"Автоматически удалять после завершения",
                                      ) #автоматическое удаление
#    tags = TaggableManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u"мероприятие"
        verbose_name_plural = u"мероприятия"
        


class FavoriteEvent(models.Model):
    user = models.ForeignKey(User, verbose_name=u"Пользователь")
    event = models.ForeignKey(Event, verbose_name=u"Мероприятие")

    def __unicode__(self):
        return self.event.title + ': ' + self.user.username

    class Meta:
        verbose_name = u"отмеченное мероприятие"
        verbose_name_plural = u"отмеченные мероприятия"


class EventRemember(models.Model):
    favorite_event = models.ForeignKey(FavoriteEvent, verbose_name=u"Избранное событие")
    remember_date = models.DateField(verbose_name=u"Дата напоминания", blank=True, null=True)
    remember_system = models.IntegerField(verbose_name=u"Система напоминания (0-email, 1-sms)",default=0)

class EventComment(models.Model):
    event = models.ForeignKey(Event, verbose_name=u"Мероприятие")
    user = models.ForeignKey(User, verbose_name=u"Пользователь")
    text = models.CharField(verbose_name=u"Текст комментария (макс. 1024 символа)",
                            max_length=1024, null=False, blank=False)
    post_date = models.DateTimeField(verbose_name=u"Дата отправления",
                                     auto_now_add=True)
    class Meta:
        verbose_name = u"комментарий"
        verbose_name_plural = u"комментарии"