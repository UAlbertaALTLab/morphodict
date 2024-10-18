from django import template

register = template.Library()


@register.filter
def blank_if_zero(n):
    """Return str(n) unless n is zero, in which case return ""."""
    if n == 0:
        return ""
    return str(n)


@register.filter
def add_percent_sign(n):
    """Add a % sign to the end of x, unless x is empty"""
    if not isinstance(n, str):
        n = str(n)
    if len(n) > 0:
        return n + "%"
    return n
