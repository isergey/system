# -*- coding: utf-8 -*-
districts_list = [

    {'code': '1', 'title': u'Адмиралтейский'},
    {'code': '2', 'title': u'Василеостровский'},
    {'code': '3', 'title': u'Выборгский'},
    {'code': '4', 'title': u'Калининский'},
    {'code': '5', 'title': u'Кировский'},
    {'code': '6', 'title': u'Колпинский'},
    {'code': '7', 'title': u'Красногвардейский'},
    {'code': '8', 'title': u'Красносельский'},
    {'code': '9', 'title': u'Кронштадтский'},
    {'code': '10', 'title': u'Курортный'},
    {'code': '11', 'title': u'Московский'},
    {'code': '12', 'title': u'Невский'},
    {'code': '13', 'title': u'Петроградский'},
    {'code': '14', 'title': u'Петродворцовый'},
    {'code': '15', 'title': u'Приморский'},
    {'code': '16', 'title': u'Пушкинский'},
    {'code': '17', 'title': u'Фрунзенский'},
    {'code': '18', 'title': u'Центральный'},
]

def get_districts_choices(with_select_row=False):
    choices = []
    if with_select_row:
        choices.append((0, u'----'))
    for district in districts_list:
        choices.append((district['code'], district['title']))
    return choices

def find_district(code='', title=''):
    if code:
        for district in districts_list:
            if code == district['code']:
                return district
        return None
    if title:
        for district in districts_list:
            if title == district['title']:
                return district
        return None
