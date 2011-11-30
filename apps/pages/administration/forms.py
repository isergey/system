# -*- coding: utf-8 -*-
from django import forms
from apps.pages.models import Page
from common.access.choices import get_groups_choices
from common.access.shortcuts import  check_perm_for_model

class PageForm(forms.ModelForm):
    view_page_groups = forms.MultipleChoiceField(choices=get_groups_choices(),
                                       label=u"Группы пользователей, имеющие доступ к странице",
                                       widget=forms.CheckboxSelectMultiple)

    def clean_view_page_groups(self):
        groups = self.cleaned_data['view_page_groups']
        if check_perm_for_model('view_page', Page):
            return groups
        
        raise forms.ValidationError(u'Model Page not have "view_page" perm')


    class Meta:
        model = Page
