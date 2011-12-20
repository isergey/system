# -*- coding: utf-8 -*-
from django.conf import settings
import datetime
import uuid

from django.utils import simplejson

from django.conf import settings
from django.views.generic.simple import direct_to_template

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import login as auth_login
from django.contrib.sites.models import Site, RequestSite
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, Http404
from django.db import transaction

from libs.ldapwork.ldap_work import LdapWork
import re

from apps.ldaccounts.forms import PermissionForm, RegistrationForm, ResetPasswordForm
#from apps.mailer import send_mail

from models import RegConfirm, PasswordRemember
from forms import EmailForm

from django.core.mail import send_mail
#@login_required
def index(request):
    """
    username = request.user.is_anonymous()
    #groups = Group.objects.all()
    ct,t = ContentType.objects.get_or_create(model = '', app_label = 'gallery',
	    defaults = {'name': 'новое'})

    per, created = Permission.objects.get_or_create(codename = 'can_index_gallery',
	    content_type__pk = ct.id,
	    defaults = {'name': 'Can Index Pizza', 'content_type': ct})

    request.user.user_permissions.add(per)
    groups = request.user.groups.all()
    #perm.save()
    """
    return direct_to_template(request, 'ldaccounts/ldaccounts_base.html',{
        'username': username,
        'groups': groups
    })


def get_users(request, year=None, month=None, day=None):
    dap_work = LdapWork(settings.LDAP)

    if year and month and day:
        users = User.objects.filter(date_joined__year=year, date_joined__month=month, date_joined__day=day ).order_by('-date_joined')
    if year and month and  not day:
        users = User.objects.filter(date_joined__year=year, date_joined__month=month).order_by('-date_joined')
    if year and not month and  not day:
        users = User.objects.filter(date_joined__year=year).order_by('-date_joined')
    if not year and not month and  not day:
        users = User.objects.all().order_by('-date_joined')

    user_maps = []
    for user in users:
        user_map = {}
        ldap_user = dap_work.get_users_by_attr(username=user.username)
        if ldap_user:
            user_map['description'] = ldap_user[0].description
            user_map['false'] = True
        else:
            user_map['new'] = True

        user_map['username'] = user.username
        user_map['date_joined'] = user.date_joined

        user_maps.append(user_map)
    return direct_to_template(request, 'ldaccounts/users.html', {
        'users': user_maps
    })
    

@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    #Displays the login form and handles the login action

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":

        form = authentication_form(data = request.REQUEST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                #записываем в сессию открытый пароль, чтобы передать его в zgate
                request.session['opassword'] = form.cleaned_data['password']
            if 'pw' in request.GET and request.GET['pw'] == '1':
                    return direct_to_template(request, 'registration/personal_cabinet_wiget.html')

            for group in request.user.groups.all():
                if group.name == 'PROFESSIONAL':
                    return HttpResponseRedirect('/professional')
    
            return HttpResponseRedirect(redirect_to)
        elif request.is_ajax():
            return HttpResponse("wrong")
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)


        
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))



def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                is_active=False,
            )
            user.set_password(form.cleaned_data['password'])
            from django.utils.hashcompat import md5_constructor
            user.save()
            hash = md5_constructor(str(user.id) + form.cleaned_data['username']).hexdigest()
            confirm = RegConfirm(hash=hash, user_id=user.id)
            confirm.save()
            message = u'Поздравляем! Вы зарегистрировались на ' + 'ksob.spb.ru'\
                + u". Пожалуйста, пройдите по адресу " + "http://" + 'ksob.spb.ru' + "/accounts/confirm/" + hash\
                + u" для активации учетной записи"

            send_mail(u'Активация аккаунта ' + 'ksob.spb.ru', message, 'ksob@ksob.spb.ru',
                    [form.cleaned_data['email']])

            return direct_to_template(request, 'registration/registration_done.html', {'form': form })
    else:
        form = RegistrationForm() # An unbound form
    return direct_to_template(request, 'registration/registration.html', {'form': form })

def test_mail(request):
    send_mail('Subject here', 'Here is the message.', 'superzi@ya.ru',
    ['sergey@unilib.neva.ru'], fail_silently=True)
    return HttpResponse(u'отправлено1')

def confirm_registration(request, hash):
    try:
        confirm = RegConfirm.objects.get(hash=hash)
    except RegConfirm.DoesNotExist:
        return HttpResponse(u'Код подтверждения не верен')
    try:
        user = User.objects.get(id=confirm.user_id)
    except User.DoesNotExist:
        return HttpResponse(u'Код подтверждения не верен')

    if user.is_active == False:
        #тут надо создать пользователя в лдапе
        user.is_active = True
        group = Group.objects.get(name='users')
        user.groups.add(group)
        user.save()
        confirm.delete()
    return direct_to_template(request,  'registration/registration_confirm.html')


@transaction.commit_on_success
def remember_password(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            hash = uuid.uuid4().hex
            password_remember = PasswordRemember(hash=hash, email=form.cleaned_data['email'])
            password_remember.save()
            message = u'Вы запросили восстановление пароля на сайте %s. Для продолжения перейдите по ссылке %s' % \
                (settings.SITE_URL ,settings.SITE_URL + "/accounts/reset/" + hash)

            send_mail(u'Восстановление пароля ' + settings.SITE_URL, message, 'ksob@ksob.spb.ru',
                      [form.cleaned_data['email']])
            return HttpResponse(u'Ссылка на страницу восстановления пароля была отправлена на адрес, указанный в форме.')

    else:
        form = EmailForm()

    return direct_to_template(request, 'registration/email_form.html', {'form': form})

@transaction.commit_on_success
def reset_password(request, hash):
    password_remember = get_object_or_404(PasswordRemember, hash=hash, activated=False)
    users_list = User.objects.filter(email=password_remember.email)[:1]
    if users_list:
        user = users_list[0]
    else:
        raise Http404()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            password_remember.activated = True
            password_remember.save()
            return HttpResponse(u'Пароль изменен. Можете <a href="/accounts/login/">войти</a> на портал, используя новый пароль.')

    else:
        form = ResetPasswordForm()

    print user.username
    return direct_to_template(request, 'registration/reset_password_form.html', {'form': form, 'username':user.username})


from api.common import response
from api.decorators import api
from api.exceptions import ApiException, WrongArguments

@api
def api_get_user(request):
    username = request.GET.get('username', None)
    if username == None:
        raise WrongArguments

    if username:
        try:
            user = User.objects.get(username=username)
            result = {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
        except User.DoesNotExist:
            result = {}
    return result


