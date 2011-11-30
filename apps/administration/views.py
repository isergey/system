
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required

@permission_required_or_403('administration.can_access')
def index(request):
    return direct_to_template(request, 'administration_base.html',
                              {'pages_list': '1',
                               'active_pages':True})

