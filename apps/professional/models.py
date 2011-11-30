# -*- coding: utf-8 -*-
from django.db import models

class Professional(models.Model):
    
    content = models.TextField(verbose_name=u"Текст профессиональной страницы",
                               null=False, blank=False)

    def __unicode__(self):
        return self.content
    
    def delete(self):
        pass
    
    class Meta:
        verbose_name = u"профессиональная страница"
        permissions = (
            ('can_access', u'Имеет доступ'),
            ('cant_access', u'Не имеет доступ'), #
            ('can_edit_content', u'Редактирование профессиональной старницы'),
        )