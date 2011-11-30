# -*- coding: utf-8 -*-
import html5lib
from html5lib import treebuilders
import lxml
import zworker

class ZGateAPI(object):
    def __init__(self):
        self.session_id = '0'
        pass

    def get_search_form(self, username='', password=''):
        zw = zworker.ZWorker(username=username,password=password)
        zw.get_search_form()


    def seach(self):
        pass
    

        