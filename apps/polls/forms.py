# -*- coding: utf-8 -*-
from django import forms

from models import Poll

#def get_poll_choices():
#    poll
#    return month


class CalendarFilterForm(forms.Form):
    month = forms.ChoiceField(choices=MONTH_CHOICES,
                              label=u"Месяц",
                              initial=get_current_month_choice(),
                              widget=forms.Select(attrs={'onchange':'this.form.submit();'}))
    year = forms.ChoiceField(choices=get_years_choice(),
                             label=u"Год",
                             initial=get_current_year_choice(),
                             widget=forms.Select(attrs={'onchange':'this.form.submit();'}))
    #Возвращаем список из предыдущего текущего и следующего года

