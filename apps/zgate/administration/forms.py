# -*- coding: utf-8 -*-
from django import forms
from apps.zgate.models import ZCatalog

from common.access.choices import get_groups_choices
from common.access.shortcuts import  check_perm_for_model

class ZCatalogForm(forms.ModelForm):

    view_catalog_groups = forms.MultipleChoiceField(choices=get_groups_choices(),
                                       label=u"Группы пользователей, имеющие доступ к каталогу",
                                       widget=forms.CheckboxSelectMultiple)

    def clean_view_page_groups(self):
        groups = self.cleaned_data['view_catalog_groups']
        if check_perm_for_model('view_zcatalog', ZCatalog):
            return groups

        raise forms.ValidationError(u'Model ZCatalog not have "view_zcatalog" perm')
    class Meta:
        model = ZCatalog

        
    def __init__(self, *args, **kwargs):
        super(ZCatalogForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget = forms.TextInput(attrs={'class':'text span-18'})
        self.fields['description'].widget = forms.Textarea(attrs={'class':'text span-18'})
        self.fields['help'].widget = forms.Textarea(attrs={'class':'text span-18'})
        self.fields['url'].widget = forms.TextInput(attrs={'class':'text span-18'})
        self.fields['xml'].widget = forms.TextInput(attrs={'class':'text span-18'})
        self.fields['xsl'].widget = forms.TextInput(attrs={'class':'text span-18'})

