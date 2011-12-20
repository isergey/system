#encoding: utf-8
from django import forms
from models import UserLibRegistation, StatusChange
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.admin import widgets


class SexyModelForm(forms.ModelForm):
    #error_css_class = 'class-error'
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
#        for field in self.fields:
#            self.fields[field].widget.attrs['class'] = 'some-class other-class'
    def as_div(self):
        "Returns this form rendered as HTML <div>s."
        return self._html_output(
            normal_row = u'<div%(html_class_attr)s>%(label)s %(field)s %(errors)s %(help_text)s </div>',
            error_row = u'<div class="error">%s</div>',
            row_ender = '</div>',
            help_text_html = u'<span class="help-block">%s</span>',
            errors_on_separate_row = False)


class UserLibRegistationForm(SexyModelForm):
    visit_date = forms.DateField(
        label=u'Дата визита',widget=widgets.AdminDateWidget,
        help_text=u'Укажите дату визита в библиотеку для окончательного оформления регистрации (дд.мм.гггг)'
    )
    class Meta:
        model = UserLibRegistation
        exclude = ('user','status')


class ChangeStatusForm(SexyModelForm):
    comments = forms.CharField(widget=forms.Textarea, label=u'Комментарии пользователю')
    class Meta:
        model = StatusChange
        exclude = ('registration','registration_manager', 'status', 'change_date', )