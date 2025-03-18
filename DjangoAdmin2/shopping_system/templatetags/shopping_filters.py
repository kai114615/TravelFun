from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def multiply(value, arg):
    """將兩個數值相乘"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 