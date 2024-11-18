from django import template
register = template.Library()

@register.filter
def repeat(value, count):
    return value * count