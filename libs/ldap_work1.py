# -*- coding: utf-8 -*-
import ldap
from ldap import modlist

class LdapWorkException(Exception): pass

class LdapWork(object):
    """
    Класс для работы с LDAP базой. 
    Содержит методы для управления организациями и пользователями
    """
    def __init__(self, ldap_server_uri, bind_dn, password, base_dn):
        """
        ldap_server_uri -- адрес LDAP сервера. eg ldap://localhost:389
        bind_dn -- dn для аутентификации. eg 'cn=Manager,dc=example,dc=com'
        password -- пароль
        base_dn -- корень, с которым будем работать
        """
        self.ldap_connection = ldap.initialize(ldap_server_uri)
        self.ldap_connection.simple_bind_s(bind_dn, password)
        self.base_dn = base_dn
        
    def __del__(self):
        self.ldap_connection.unbind_s()
    

    
    def reg_library(self, title, address, phone, site_url, 
                    email, latitude, longitude,
                    country, city, district, code, edd, time, paren_org = ''):
        """
        Метод для регистрации библиотеки
        """
        adding_oblect = {}
        adding_oblect['objectClass'] = ['RUSLANorg', 'organization', 'top']
        adding_oblect['o'] = title
        adding_oblect['displayname'] = title
        adding_oblect['mail'] = email
        
        if address != '': adding_oblect['postaladdress'] = address
        
        if phone != '': adding_oblect['telephonenumber'] = phone
        
        if site_url != '': adding_oblect['httpservice'] = site_url
        
        if latitude != '': adding_oblect['latitude'] = latitude
        
        if longitude != '': adding_oblect['longitude'] = longitude
        
        if country != '': adding_oblect['c'] = country
        
        if city != '': adding_oblect['l'] = city
        
        if district != '': adding_oblect['district'] = district
        
        if code != '': adding_oblect['code'] = code
        
        if edd != '': adding_oblect['eddservice'] = edd
        
        if edd != '': adding_oblect['plans'] = time
        
        if paren_org == '':
            dn_org = 'o=%s,%s' % (title, self.base_dn)
        else:
            dn_org = dn_org = 'o=%s,o=%s,%s' % (title, paren_org, self.base_dn)

        ldif = modlist.addModlist(adding_oblect)
        self.ldap_connection.add_s(dn_org,ldif)
        
        
                    
                    
