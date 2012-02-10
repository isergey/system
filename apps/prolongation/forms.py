#encoding: utf-8
from django import forms
from models import UserProlongation, StatusChange
from django.contrib.admin import widgets

from vendors.mptt.fields import TreeNodeChoiceField
from common.forms import CoolModelForm


from participants.models import District

def get_districts_choices(with_empty_row=False):
    districts = District.objects.select_related().all()
    choices = []
    if with_empty_row:
        choices.append((0, u'----'))
    for district in districts:
        choices.append((district.id, district.city.name + u': '+ district.name))
    return choices


class UserProlongationForm(CoolModelForm):
    district = forms.ChoiceField(choices=get_districts_choices(True), label=u'Выберите район',
        help_text=u'Нажмите на список, чтобы выбрать район, в котором находится библиотека')
    date_of_return = forms.DateField(
        label=u'Срок возврата (дд.мм.гггг)',widget=widgets.AdminDateWidget,
        help_text=u'Укажите дату, когда документ должен быть возвращен в библиотеку '
    )
    new_date_of_return = forms.DateField(
        label=u'Срок продления (дд.мм.гггг)',widget=widgets.AdminDateWidget,
        help_text=u'Укажите дату, до которой хотите продлить срок возврата. Не более, чем 30 дней со дня старого срока возврата'
    )
    class Meta:
        model = UserProlongation
        exclude = ('user','status', 'recive_library', 'manage_library')


class ChangeStatusForm(CoolModelForm):
    comments = forms.CharField(widget=forms.Textarea, label=u'Комментарии пользователю', max_length=1024)
    class Meta:
        model = StatusChange
        exclude = ('prolongation','prolongation_manager', 'status', 'change_date', )