# -*- coding: utf-8 -*-
from django.db import models
from django.utils.text import capfirst

class Page(models.Model):
    title = models.CharField(verbose_name=u"Название страницы",
                             max_length=255, null=False, blank=False)
    latin_title = models.SlugField(unique=True, verbose_name=u"Название страницы (латинскими буквами)")
    content = models.TextField(verbose_name=u"Содержимое страницы",
                               null=False, blank=False)
    create_date = models.DateTimeField(verbose_name=u"Дата создания",
                                    auto_now_add=True)
    def __unicode__(self):
        return self.title

    def unique_error_message(self, model_class, unique_check):
        opts = model_class._meta
        model_name = capfirst(opts.verbose_name)

        # A unique field
        if len(unique_check) == 1:
            field_name = unique_check[0]
            field_label = capfirst(opts.get_field(field_name).verbose_name)
            # Insert the error into the error dict, very sneaky
            if field_name == 'latin_title':
                return u"Такое название уже существует"
            return _(u"%(model_name)s with this %(field_label)s already exists.") %  {
                'model_name': unicode(model_name),
                'field_label': unicode(field_label)
            }
        # unique_together
        else:
            field_labels = map(lambda f: capfirst(opts.get_field(f).verbose_name), unique_check)
            field_labels = get_text_list(field_labels, _('and'))
            return _(u"%(model_name)s with this %(field_label)s already exists.") %  {
                'model_name': unicode(model_name),
                'field_label': unicode(field_labels)
            }

    class Meta:
        verbose_name = u"страница"
        verbose_name_plural = u"страницы"
        permissions = (
            ('view_page', u'Просмотр страницы'),
        )