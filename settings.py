# -*- coding: utf-8 -*-
# Django settings for libportal project.
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__)) + '/'
sys.path.insert(0, os.path.join(PROJECT_PATH, "vendors"))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))



DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')0ngeeewq_dr=57-x6151x&#0@m#2r9i=)9g9pyjmdk9+8or)_'

DEFAULT_CHARSET = 'utf-8'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                             # Or path to database file if using sqlite3.
        'USER': '',                         # Not used with sqlite3.
        'PASSWORD': '',                       # Not used with sqlite3.
        'HOST': '',                        # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                             # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
            }
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True



# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_ROOT = '/wrk/htdocs/ksob.ruslan.ru/libportal/media'
STATIC_URL = '/media/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )


MEDIA_URL = ''



# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'




TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#        ('django.template.loaders.cached.Loader', (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#        )),
#         'django.template.loaders.eggs.Loader',
)







EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 25
#EMAIL_BACKEND = "libportal.apps.mailer.backend.DbBackend"

AUTHENTICATION_BACKENDS = (
#    'apps.ldaccounts.auth_backend.LdapBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
ANONYMOUS_USER_ID = -1

MIDDLEWARE_CLASSES = (
#    'johnny.middleware.LocalStoreClearMiddleware',
#    'johnny.middleware.QueryCacheMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'middleware.content_length.ContentLength'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    #'/wrk/htdocs/ksob.ruslan.ru/libportal/templates/',
    PROJECT_PATH + 'templates',
)


"""
 Синхронизация локальной базы пользоватлей, с базой LDAP
 Еслм True, то при отсутвии подключения к серверу LDAP, пользователи не смогут авторизовываться и
 регистироваться
"""

#LDAP_USERS_SYNC = True
##пароль на сервер
LDAP = {
    #'server_uri': 'ldap://localhost:389',
    'server_uri': 'ldap://ldap.arbicon.ru:389',
    'bind_dn': 'cn=Manager,dc=Arbicon,dc=ru',
    'bind_password': 'Ass-12rack',
    'base_dn': 'dc=ksob,dc=ru'
}


INSTALLED_APPS = (
    'guardian',
    'treemenus',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    #vendor apps
    'mailer',
    'mptt',
    'taggit',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
    'core',
    'site_index',
    'events',
    'pages',
    'news',
    'polls',
    'zgate',
    'gallery',
    'orders',
    'ldaccounts',
    'participants',
    'guestbook',
    'reginlib',
    'prolongation',
    'helper',
    'api',
    #'searcher',
    'administration',
    #'libportal.apps.professional',
    'captcha',

)
ZGATE = {
    'xsl_templates':{
        'full_document': PROJECT_PATH + 'xslt/full_document.xsl',
        'short_document': PROJECT_PATH + 'xslt/short_document.xsl',
    }
}




from local_settings import *
