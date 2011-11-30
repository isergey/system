# -*- coding: utf-8 -*-
from django import forms
from apps.news.models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
