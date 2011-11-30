# -*- coding: utf-8 -*-
import subprocess
import os
import re
import libs.humanquery as HQ

class ZWorker(object):
    def __init__(self, zgate_cookie = '', session_time_out = '300', zgate_home_dir = ''):
        """
        Инициализация переменных окружения для вызова cgi приложегния zgate
        """
        os.environ['ZGATE_SESSION_TIMEOUT'] = session_time_out

        if zgate_home_dir:
            os.environ['ZGATE_HOME'] = zgate_home_dir
        else:
            os.environ['ZGATE_HOME'] = os.getcwd() + '/zgate.conf'

        if zgate_cookie:
            os.environ['HTTP_COOKIE'] = zgate_cookie

        os.environ['ZGATE_CHAR_SET'] = "UTF-8"

        self.post_string = ''
        self.current_login = ''
        self.current_password = ''
        self.xml_name = ''
        self.xsl_name = ''
        self.entry_point = '' # url инициализации cgi скрипта


    def get_search_form(self, username='', password=''):
        if username:
            pass
            #s = Session.objects.get(pk=md5_constructor(username).hexdigest())
            #if s:
            #    password = s.password

        self.post_string = 'ACTION=init&LANG=rus&FORM_HOST_PORT=' + self.xml_name + ',' +\
                  self.xsl_name + '&ENTRY_POINT=' + self.entry_point + '&USERID=' +\
                  username + '&PASSWORD=' + password #'burchik' + '&PASSWORD=' + '123456'

        os.environ['CONTENT_LENGTH'] = str(len(self.post_string))
        os.environ['REQUEST_METHOD'] = 'POST'

        result = self.__run_cgi(self.post_string.replace('+', '%2B'))
        #print result
        if len(result) == 0:
            raise RuntimeError('zgate error')
        headers = result.split('\n\n')[0]
        cookie = headers.split('Set-Cookie:')[1]
        try:
            compiled_regx = re.compile(r".*<body>(?P<section>.*).*</body>", re.IGNORECASE | re.MULTILINE)

            result = result.replace("\n", '|||') #временно меняем символы новой строки, чтобы сработала регулярка ыыы
            result = re.match(compiled_regx, result).group('section')
            result = result.replace("|||", '\n')
        except AttributeError:
            raise RuntimeError('wrong zgate response')
        result = self.__change_href(result)
        return {'zgate_cookie': cookie, 'search_form': result}


    def make_get_request(self, get_params = ''):
        """
        Заруск приложения для GET запросов
        """
        results = self.__run_cgi(params=get_params)
        results = results.split('\n\n')[1]
        results = self.__change_href(results)
        return results

    def make_get_request_np(self, get_params = ''):
        """
        Заруск приложения для GET запросов без параметров
        """
        os.environ['CONTENT_LENGTH'] = str(len(get_params))
        os.environ['REQUEST_METHOD'] = 'GET'
        os.environ['QUERY_STRING'] = get_params
        
        results = self.__run_cgi()
        results = results.split('\n\n')[1]
        results = self.__change_href(results)
        return results

    def search(self, post_string):
        """
        Обработка переменных переданных от поисковой формы
        в post_string нужно передать строку вида val=1&val=2 
        """
        self.post_string = post_string
        os.environ['CONTENT_LENGTH'] = str(len(self.post_string))
        os.environ['REQUEST_METHOD'] = 'POST'

        result = self.__run_cgi(self.post_string)

        compiled_regx = re.compile(ur".*<body>(?P<section>.*).*</body>", re.IGNORECASE | re.MULTILINE)
        result = result.replace("\n", '|||') #временно меняем символы новой строки, чтобы сработала регулярка
        result = re.match(compiled_regx, result).group('section')

        result = result.replace("|||", '\n')
        result = self.__change_href(result)
        #print result
        return result


    def __change_href(self, result):
        """
        Подменяет добавляет в ссылки переменнную st
        """
        result = result.replace('href="zgate?form', 'href="' + self.entry_point + '?form')
        result = result.replace('href="zgate?present', 'href="show?st=present')
        result = result.replace('href="zgate?ACTION', 'href="show?ACTION')
        result = result.replace('href="zgate?ACTION=SEARCH', 'href="show?ACTION=SEARCH')
        #result = result.replace('href="zgate?', 'href="/zgate/show?')
        compiled_regx = re.compile(ur'<div class="human_query">(.*])\)?</div>', re.UNICODE)
        arm_querys = re.findall(compiled_regx, result)

        if arm_querys:
            for arm_query in arm_querys:
                #print 'querys ', arm_query
                if result.find(arm_query) != -1:
                    result = result.replace(arm_query, HQ.HumanQuery(arm_query).convert())
        return result

    def __run_cgi(self, input='', params=''):


        process_name = os.getcwd() + '/zgate ' + params
        #print 'process: ', process_name
        #print 'input', input
        #if params:
        #    process_name = [os.getcwd() + '/zgate', params.replace(' ', '+')]

        #print process_name
        """zgate = subprocess.Popen(process_name, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdin, stdout) = (zgate.stdin,zgate.stdout)
        if input:
            stdin.write(input.replace('+', '%2B'))
            stdin.close()
        result = stdout.readlines()
        stdout.close()
        """
        fin, fout = os.popen4(process_name)
        if input:
            fin.write(input.replace('+', '%2B'))
            fin.close()
        result = fout.readlines()
        fout.close()
        #print 'readed'
        headers = []
        no_line_result = []
        i = 0
        """
        В результате могут несколько '\n' подряд
        Вырезаем их, оставляя только первую '\n' после http заголовка 
        """
        for line in result:
            i += 1
            if line != '\n':
                headers.append(line)
            else:
                headers.append(line)
                break

        for line in result[i:]:
            if line != '\n':
                headers.append(line)

        headers.extend(no_line_result)

        #print 'he ', headers
        return ''.join(headers).decode('UTF-8')
