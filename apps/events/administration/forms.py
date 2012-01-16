# -*- coding: utf-8 -*-
from django import forms
from apps.events.models import Event, EventCategory
import datetime
class EventForm(forms.ModelForm):
#    category = forms.ModelChoiceField(queryset=EventCategory.objects.all())
    start_date = forms.DateTimeField(('%d.%m.%Y %H:%M:%S',), label=u"Дата начала",
                                     widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M:%S',attrs={'class':'text span-18'}),
                                    initial=datetime.date.today
                                      )
    end_date = forms.DateTimeField(('%d.%m.%Y %H:%M:%S',), label=u"Дата окончания",
                                     widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M:%S',attrs={'class':'text span-18'}),
                                    initial=datetime.date.today
                                      )
    class Meta:
        model = Event


    def clean_end_date(self):
        stat_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']

        if end_date < stat_date:
            raise forms.ValidationError(u"Дата окончания мероприятия меньше даты начала")
        return  end_date
