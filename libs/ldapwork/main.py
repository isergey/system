# -*- coding: utf-8 -*-
"""
LDAP = {
    'server_uri': 'ldap://ldap.arbicon.ru:389',
    'bind_dn': 'cn=Manager,dc=Arbicon,dc=ru',
    'bind_password': 'Ass-12rack',
    'base_dn': 'dc=ksob,dc=ru'
}


from ldap_work import LdapWork, LdapConnection, LdapUser

ldap_connection = LdapConnection(LDAP)
lw = LdapWork(ldap_connection)

for user in lw.get_users_by_attr(node='.'):
    print user,'\n'

user = LdapUser(username='2username',
                        password='password',
                        email='email',
                        name='name',
                        phone='phone',
                        member_of=['member_of','eeee'],
                        )

result = lw.user_registration(user, 'o=Польз"ователи КСОБ')

if result == False:
    print 'Уже существует'
"""