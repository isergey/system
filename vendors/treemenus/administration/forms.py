# -*- coding: utf-8 -*-
from django import forms
from treemenus.models import Menu, MenuItem
import datetime
class MenuForm(forms.ModelForm):

    class Meta:
        model = Menu


class MenuItemForm(forms.ModelForm):

    class Meta:
        model = MenuItem

