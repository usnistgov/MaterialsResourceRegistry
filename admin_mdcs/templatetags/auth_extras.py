from django import template
from django.contrib.auth.models import Group
from django.db.models import Q
import mgi.rights as RIGHTS

register = template.Library()

#Allow us to access to dictionary data, within a view, with the [] accessor
@register.filter(name='has_perm')
def has_perm(user, permission):
    try:
        permission_split = permission.split('.')
        permission_name = getattr(RIGHTS, permission_split[1])
        if user.is_anonymous():
            #We can give directly the permission name
            access = Group.objects.filter(Q(name=RIGHTS.anonymous_group) & Q(permissions__codename=permission_name))
        else:
            #We need to prefix with the app name
            access = user.has_perm(permission)
    except:
        #If something went wrong, we ask for an empty permission to give the access if it's a superUser
        access = user.has_perm("")

    return access
