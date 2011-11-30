# -*- coding: utf-8 -*-
from django.conf import settings
from django import forms
import os
class UploadFileForm(forms.Form):
    file  = forms.FileField(label=u"файл")
    path = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_path(self):
        path = self.cleaned_data['path'].strip('/')
        if path == u'': return '/'
        if '..' in path or '/.' in path:
            raise forms.ValidationError(u"Wrong path")

        path = '/%s' % path
        return path