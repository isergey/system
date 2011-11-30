# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session

from django.utils.hashcompat import md5_constructor #md5_constructor(salt + raw_password).hexdigest()
from django.contrib.auth.models import User, Group, check_password
import ldap
import sys

from libs.ldapwork.ldap_work import LdapWork, LdapWorkException, LdapConnection
from libs.ldapwork.ldapuser import LdapUser

class LdapBackend:
    def authenticate(self, username=None, password=None, session=None):
        if len(password) == 0:
            return None
        result = self.get_or_create_user(username, password)
        return result


    def get_or_create_user(self, username, password):
        """
            Функция принимает имя пользователя и пароль. Если на LDAP сервере существует
        подходящий пользователь - проверяется его наличие в локальной базе, если в 
        базе его не оказалось, то пользователь создается в локальной базе(синхронизация 
        с LDAP пользователем) и возвращается как User, попутно присваивая ему группу 
        для доступа к функциям сайта.
            Если пользователя не существует в LDAP, но существует в локальной базе,
        проверяем его на принадлежность к супер админу, если супер админ, то логиними
        если не супер админ - удаляем.
        """

        #Устанавливаем соединение с LDAP базой



        try:
            ldap_connection = LdapConnection(settings.LDAP)
            ldap_work = LdapWork(ldap_connection)
        except LdapWorkException as e:
            sys.stderr.write('Error of connection to LDAP server: ' + e.message)
            if settings.LDAP_USERS_SYNC:
                return None
        except Exception:
            sys.stderr.write('Error of connection to LDAP server: ' + e.message)
            if settings.LDAP_USERS_SYNC:
                return None

            #Филтр запроса на получение объета пользователя
            #filter = '(&(uid=%s)(objectClass=RUSLANperson)(userPassword=%s))' % (username, password)
            #аттрибуты, которые будут извлечены для обработки
            #attrs = ['uid','sn','memberOf','userPassword','mail','telephoneNumber']

            #ldap_results = ldap_connection.search_s( settings.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, filter, attrs )
        ldap_users = ldap_work.get_users_by_attr(username=username, password=password)

        #если пользователь не существет в LDAP
        #проверяем, существует ли он в локальной базе
        #если да, то в случае, если пользователь не админ, удаляем его
        if len(ldap_users) == 0: #пользователь не найден
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
            else:
                if user.is_superuser == False and settings.LDAP_USERS_SYNC == False:
                    user.delete()
                    return None


                #Если пользователь прошел проверку в LDAP, пытаемся найти его в локальной базе
                #В случае его отсутвия создадим его
        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
        #извлекаем информацию о пользователе
            ldap_user = ldap_users[0]
#            orgs =  ldap_user.dn[1:-2]
#
#            for org in orgs:
#                print 'orororor',org
#
#            ldap_groups = []
#            print 'orgs',orgs
#            for org in orgs:
#                print 'org',org
#                ldap_orgs = ldap_work.get_org_by_attr(display_name=org)
#                if ldap_orgs:
#                    ldap_groups += ldap_orgs.member_of
                    
#            print ldap_groups
            #print ldap_user.string_dn
            
            print 'member_of', ldap_user.member_of
            
            #если пользователь из ветки 'Пользователи КСОБ или он не состоит в группах,
            #то ему присваевается группа users
            user = User(username=ldap_user.uid, email=ldap_user.email)
            user.is_superuser = False
            user.set_password(password)
            if 'Пользователи КСОБ' in ldap_user.dn or len(ldap_user.member_of) == 0:
                try:
                    group = Group.objects.get(name='users')
                except Group.DoesNotExist:
                    group = Group(name='users')
                    group.save()
                if group:
                    user.is_staff = False
                    user.save()
                    user.groups.add(group)
                    return user

            else: #тогда пользователь библиотеки
                if len(ldap_user.member_of):
                    groups = []
                    for group_name in ldap_user.member_of:

                        try:
                            group = Group.objects.get(name=group_name)
                            groups.append(group)
                        except Group.DoesNotExist:
                            group = Group(name=group_name)
                            group.save()
                            groups.append(group)
                    user.is_staff = True
                    user.save()
                    for group in groups:
                        user.groups.add(group)
                    user.save()
                    return user
                raise Exception("Can't create group")

            return None
            #метод стандартный для бэкенда

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _get_ldap_attribute_first(self, attr_map, key):
        """
        Функция получает на вход карту вида
        attr_map = {
            'key':['value1','valueN']
        }
        и возвращает первый элемент из списка key
        Если ключ или значение не найдено, возвращается None
        """
        if attr_map.has_key(key):
            if len(attr_map[key]) > 0: return attr_map[key][0]
            else: return None
        else: return None
