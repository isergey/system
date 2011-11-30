from django.views.generic.simple import direct_to_template
#from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect


def index(request):
    return direct_to_template(request, 'site_index/index.html')

