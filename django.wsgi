import os
import sys
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
path = PROJECT_PATH + '../'
if path not in sys.path:
    sys.path.append(path)


