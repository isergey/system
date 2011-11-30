# -*- coding: utf-8 -*-
from django import forms
from apps.guestbook.models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
