from django import template

register = template.Library()

#Allow us to access to dictionary data, within a view, with the [] accessor
@register.filter(name='access')
def access(value, arg):
    return value[arg]
