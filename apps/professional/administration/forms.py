# -*- coding: utf-8 -*-
from django import forms
from apps.professional.models import Professional


class ProfessionalForm(forms.ModelForm):
    class Meta:
        model = Professional
