# -*- coding: utf-8 -*-
import simplejson
from django.db import models

DEFAULT_LANG_CHICES = (
    ('rus', u'Русский'),
    ('eng', u'English'),
    )

default_server_config =  u"""
{
  "server": {
        "host": "127.0.0.1",
        "port": "210",
        "user": "erm",
        "password": "123456",
        "database_name": "Default",
        "preferredRecordSyntax": "rusmarc",
        "encoding": "UTF-8"
  }
}
"""

default_form_config = u"""
{
  "use": [
        {
          "id": "1003",
          "title": "Автор"
        },
        {
          "id": "4",
          "title": "Заглавие"
        },
        {
          "id": "1018",
          "title": "Издающая организация"
        },
        {
          "id": "1080",
          "title": "Ключевые слова"
        },
        {
          "id": "21",
          "title": "Тематический поиск"
        },
        {
          "id": "1",
          "title": "Персоналия"
        },
        {
          "id": "59",
          "title": "Место издания"
        },
        {
          "id": "31",
          "title": "Год издания"
        },
        {
          "id": "5",
          "title": "Заглавие серии"
        },
        {
          "id": "1076",
          "title": "Географическая рубрика"
        }
  ],
  "rows": [
    {
      "use": "4",
      "init": " "
    }
  ]
}
"""
class ConfigException(Exception): pass

def clean_server_config(config):
    if 'server' not in config:
        raise ConfigException(u'No "server" section in config')

    if 'port' not in config['server']:
            raise ConfigException(u'No "port" in server section in config')

    if 'databaseName' not in config['server']:
        raise ConfigException(u'No "databaseName" in server section in config')

    if 'preferredRecordSyntax' not in config['server']:
        raise Exception(u'No "preferredRecordSyntax" in server section in config')

    if 'encoding' not in config['server']:
        raise ConfigException(u'No "encoding" in server section in config')


def clean_form_config(config):
    if 'use' not in config:
        raise ConfigException(u'No "use" section in config')

    if not isinstance(config['use'], list):
        raise ConfigException(u'"use" section should contain an array')

    for i, item in enumerate(config['use']):
        if not isinstance(item, dict):
            raise ConfigException(u'"use" array should contain a dict ' + unicode(i) + ' item')
        if 'id' not in item:
            raise ConfigException(u'not id in "use" array dict item ' + unicode(i) + ' item')

        if not isinstance(item['id'], unicode):
            raise ConfigException(u'"id" in "use" array dict item should contain a string ' + unicode(i) + ' item')

        if not isinstance(item['title'], unicode):
            raise ConfigException(u'"title" in "use" array dict item should contain a string ' + unicode(i) + ' item')

    if 'rows' not in config:
        raise ConfigException(u'No "rows" section in config')

    if not isinstance(config['rows'], list):
        raise ConfigException(u'"rows" section should contain an array')

    for i, item in enumerate(config['rows']):
        if not isinstance(item, dict):
            raise ConfigException(u'"rows" array should contain a dict ' +  unicode(i) + ' item')
        if 'use' not in item:
            raise ConfigException(u'not "use" in "rows" array dict item '  + unicode(i) + ' item')

        if not isinstance(item['use'], unicode):
            raise ConfigException(u'"use" in "use" array dict item should contain a string ' + unicode(i) + ' item')

        if 'init' in item and not isinstance(item['init'], unicode):
            raise ConfigException(u'"init" in "use" array dict item should contain a string ' + unicode(i) + ' item')

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

    server_config = models.TextField(
        verbose_name=u"Настройка z", default=default_server_config,
        null=False, blank=False
    )

    form_config = models.TextField(
        verbose_name=u"Настройка поисковой формы",
        null=False, blank=False, default=default_form_config
    )

    can_search = models.BooleanField(
        verbose_name=u"Возможность поиска", blank=False, default=True,
        help_text=u'Доступ к каталогу для поиска'
    )


    def __unicode__(self):
        return self.title


    def get_server_config(self):
        return simplejson.loads(self.server_config)

    def get_form_config(self):
        return simplejson.loads(self.form_config)


    class Meta:
        verbose_name = u"Z Каталог"
        verbose_name_plural = u"Z Каталоги"
        permissions = (
            ('view_zcatalog', u'Доступ к каталогу'),
            )


    def clean(self):
        from django.core.exceptions import ValidationError
        # Don't allow draft entries to have a pub_date.
        try:
            server_config = simplejson.loads(self.server_config)
        except Exception as e:
            raise ValidationError(u'Wrong server config json format: ' + e.message)
        try:
            clean_server_config(server_config)
        except ConfigException as e:
            raise  ValidationError(u'Wrong server config format: ' + e.message)

        try:
            form_config = simplejson.loads(self.form_config)
        except Exception as e:
            raise ValidationError(u'Wrong form config json format: ' + e.message)

        try:
            clean_form_config(form_config)
        except ConfigException as e:
            raise  ValidationError(u'Wrong form config format: ' + e.message)