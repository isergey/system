# -*- coding: utf-8 -*-
from django import forms
from models import Collection

class UploadFileForm(forms.Form):
    title = forms.CharField(label=u"Название изображения",
                             max_length=512, required=False)

    comments = forms.CharField(label=u"Комментарии к изображению",
                                max_length = 512,
                                widget=forms.Textarea(), required=False)
    file  = forms.FileField()


class EditImageForm(forms.Form):
    title = forms.CharField(label=u"Название изображения",
                             max_length=512)

    comments = forms.CharField(label=u"Комментарии к изображению",
                                max_length = 512,
                                widget=forms.Textarea())
                                
class CreateCollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
