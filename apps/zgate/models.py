# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
DEFAULT_LANG_CHICES = (
    ('rus', u'Русский'),
    ('eng', u'English'),
    )

class ZCatalog(models.Model):
    title = models.CharField(
        verbose_name=u"Название каталога",
        max_length=64, null=False, blank=False
    )
    latin_title = models.SlugField(verbose_name=u"Название каталога (латинскими буквами)",
        unique=True)
    description = models.TextField(
        verbose_name=u"Описание каталога",
        null=False, blank=False
    )
    help = models.TextField(
        verbose_name=u"Справка для каталога",
        null=True, blank=True
    )
    default_lang = models.CharField(
        verbose_name=u"Язык каталога по умолчанию",
        choices=DEFAULT_LANG_CHICES,
        default=('rus', u'Русский'),
        max_length=10
    )

    url = models.URLField(
        verbose_name=u"URL АРМ Читателя",
        null=False, blank=False,
        help_text=u'Например: http://consortium.ruslan.ru/cgi-bin/zgate'
    )

    xml = models.CharField(
        verbose_name=u"Имя XML файла",
        max_length=256, null=False, blank=False,
        help_text=u'Нужно уточнить у администратора'
    )

    xsl = models.CharField(
        verbose_name=u"Имя XSL файла",
        max_length=256, null=False, blank=False,
        help_text=u'Нужно уточнить у администратора'
    )

    can_search = models.BooleanField(
        verbose_name=u"Возможность поиска", blank=False, default=True,
        help_text=u'Доступ к каталогу для поиска'
    )

    can_order_auth_only = models.BooleanField(
        verbose_name=u"Возможность заказа в каталоге только авторизированным пользователям на портале",
        blank=False, default=True,
        help_text=u"Заказ в каталоге возможен только если пользователь авторизирован на портале"
    )

    can_order_copy = models.BooleanField(
        verbose_name=u"Возможность заказа копии документа", blank=False,
    )

    can_order_document = models.BooleanField(
        verbose_name=u"Возможность заказа документа во временное пользование", blank=False,
    )

    can_reserve = models.BooleanField(
        verbose_name=u"Возможность  бронирования документа", blank=False,
    )




    def __unicode__(self):
        return self.title


    class Meta:
        verbose_name = u"Каталог (АРМ читателя)"
        verbose_name_plural = u"Каталоги (АРМ читателя)"
        permissions = (
            ('view_zcatalog', u'Доступ к каталогу'),
            )

class SavedRequest(models.Model):
    zcatalog = models.ForeignKey(ZCatalog)
    user = models.ForeignKey(User)
    zurls = models.CharField(max_length=2048, null=False, blank=False, verbose_name=u"Список баз данных для поиска")
    query = models.CharField(max_length=1024, null=False, blank=False, verbose_name=u"Запрос АРМ Читателя")
    human_query = models.CharField(max_length=1024, blank=True, verbose_name=u"Расшифровка запроса")
    add_date = models.DateTimeField(auto_now_add=True, db_index=True)



class SavedDocument(models.Model):
    zcatalog = models.ForeignKey(ZCatalog)
    owner_id = models.CharField(max_length=32, verbose_name=u"Идентификатор сессии (md5) или имя пользователя", db_index=True)
    document = models.TextField(null=False, blank=False, verbose_name=u"Тело документа (xml rusmarc)")
    comments = models.CharField(max_length=2048, blank=True, verbose_name=u"Комментарий к документу")
    add_date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=u"Дата добваления документа")
    expiry_date = models.DateTimeField(db_index=True, null=True, verbose_name=u"Дата когда документ удалится")
    full_document = models.TextField(null=True, blank=True, verbose_name=u"Полная запись на документ")
    short_document = models.TextField(null=True, blank=True, verbose_name=u"Краткая запись на документ")