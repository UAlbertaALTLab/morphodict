from django import template

register = template.Library()


@register.filter
def blank_if_zero(n):
    if n == 0:
        return ""
    return str(n)
