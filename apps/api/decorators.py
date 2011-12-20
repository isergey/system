# encoding: utf-8
from exceptions import ApiException
from common import response

def api(func):
    """
    декоратор для перехвата исключений, унаследованных от ApiException
    """
    def wrapper(*args, **kwargs):
        try:
            data = func(*args, **kwargs)

            return response({
                'status':'ok',
                'response': data
            })

        except ApiException as e:
            return response({
                'status':'error',
                'error': e.message
            })

    return wrapper
