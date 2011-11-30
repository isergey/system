from django import template
from django.template import resolve_variable
from django.contrib.auth.models import Group

register = template.Library()

@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to a specific
    group. Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}

    """
    try:
        tag, group = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires 1 argument.")
    nodelist = parser.parse(('endifusergroup',))
    parser.delete_first_token()
    return GroupCheckNode(group, nodelist)

@register.filter
def is_in(obj, val):
    return val in obj

@register.filter
def in_groups(user, groups):
    groups = groups.lower()
    groups = groups.split(', ')
    user_groups = user.groups.all()
    user_groups_lower = []
    for user_group in user_groups:
        user_groups_lower.append(user_group.name.lower())

    for user_group in user_groups_lower:
        if user_group in groups: return True
    return False


@register.filter
def get_user_groups(user):
    user_groups = user.groups.all()
    user_groups_lower = []
    for user_group in user_groups:
        user_groups_lower.append(user_group.name.lower())
    return ','.join(user_groups_lower)


class GroupCheckNode(template.Node):
    def __init__(self, group, nodelist):
        self.group = group
        self.nodelist = nodelist
    def render(self, context):
        user = resolve_variable('user', context)
        if not user.is_authenticated:
            return ''
        try:
            group = Group.objects.get(name=self.group)
        except Group.DoesNotExist:
            return ''
        if group in user.groups.all():
            return self.nodelist.render(context)
        return ''


