#encoding: utf-8
from django import forms
from models import UserLibRegistation, StatusChange
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.admin import widgets
from models import Library
from vendors.mptt.fields import TreeNodeChoiceField
from common.forms import CoolModelForm
from participants.districts import get_districts_choices

from participants.models import District

def get_districts_choices(with_empty_row=False):
    districts = District.objects.select_related().all()
    choices = []
    if with_empty_row:
        choices.append((0, u'----'))
    for district in districts:
        choices.append((district.id, district.city.name + u': '+ district.name))
    return choices


class UserLibRegistationForm(CoolModelForm):
    district = forms.ChoiceField(choices=get_districts_choices(True), label=u'Выберите район',
        help_text=u'Нажмите на список, чтобы выбрать район, в котором находится библиотека')
    visit_date = forms.DateField(
        label=u'Дата визита',widget=widgets.AdminDateWidget,
        help_text=u'Укажите дату визита в библиотеку для окончательного оформления регистрации (дд.мм.гггг)'
    )
    class Meta:
        model = UserLibRegistation
        exclude = ('user','status', 'recive_library', 'manage_library')


class ChangeStatusForm(CoolModelForm):
    comments = forms.CharField(widget=forms.Textarea, label=u'Комментарии пользователю')
    class Meta:
        model = StatusChange
        exclude = ('registration','registration_manager', 'status', 'change_date', )