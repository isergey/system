# -*- coding: utf-8 -*-
from django.conf import settings
from django import forms
from django.contrib.auth.models import Permission, User
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _
from libs.ldapwork.ldap_work import LdapWork, LdapWorkException, LdapConnection
#from libs.ldapwork.ldap_work import LdapWork, LdapWorkException
from libs.ldapwork.ldapuser import LdapUser
from common.forms import CoolModelForm, CoolForm


class LoginForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs["size"] = 65
        self.fields['password'].widget.attrs["size"] = 65

class RegistrationForm(CoolForm):
    username = forms.CharField(max_length=50, label="Логин", help_text=u"Разрешены буквы латинского алфавита и цифры")
    password = forms.CharField( min_length=6, max_length=50,
                                label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=6, max_length=50,
                                label="Повторите пароль", widget=forms.PasswordInput)
    email = forms.EmailField(label="Электронная почта")
    first_name = forms.CharField(max_length=50, label="Имя")
    tel_number = forms.CharField(max_length=50, label="Контактный телефон", required=False)

    def clean_username(self):
        import re
        format = re.compile(r"^[a-zA-z0-9]+$")
        if re.match(format,self.cleaned_data["username"]) == None:
            raise forms.ValidationError(u"Имя пользователя может содержать только латинские символы")

        username = self.cleaned_data["username"]
        ldap_users = []
        try:
            lc = LdapConnection(settings.LDAP)
            lw = LdapWork(lc)
            ldap_users = lw.get_users_by_attr(username=username)
        except LdapWorkException as e:
            import sys

        if len(ldap_users):
            raise forms.ValidationError(_("A user with that username already exists."))
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError(u'пароли не совпадают')
        return password2

    def clean_tel_number(self):
        import re
        format = re.compile(r"^[0-9\+\(\)]+$")
        tel_number = self.cleaned_data["tel_number"]
        if tel_number and re.match(format, tel_number) == None:
             raise forms.ValidationError(u'Номер телефона может содеражать только цифры и знак "+"')
        return tel_number

class PermissionForm(forms.Form):
    name = forms.CharField(max_length=100, label="Название права")
    codename =  forms.CharField(max_length=100, label="Кодовое название. Может содержать символы 0-9, _ , a-z")
    """def clean_codename(self):
        codename = self.clean_data['codename']
        import re
        if re.match(r'^[0-9a-z_]+$', codename) == None:
            print 'wrong'
            raise ValidationError('code name is wrong')
    """


class EmailForm(forms.Form):
    email = forms.EmailField(label="email")
    def clean_email(self):
        #print self.clean()#self.data['email']
        #print 'ok'
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)[:1]
        if not user:
            raise forms.ValidationError(u'Такой адрес не зарегистрирован в системе')

        if not user[0].is_active:
            raise forms.ValidationError(u'Такой адрес не зарегистрирован в системе')
        
        return email


class ResetPasswordForm(forms.Form):
    password = forms.CharField( min_length=6, max_length=50,
                                label="Пароль (минимум 6 символов)", widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=6, max_length=50,
                                label="Повторите пароль", widget=forms.PasswordInput)


    def clean_password2(self):
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError(u'пароли не совпадают')
        return password2


