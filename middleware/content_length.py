class ContentLength(object):
    def process_response(self, request, response):
        if not response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))
        return response