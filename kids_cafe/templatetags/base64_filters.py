# kids_cafe/templatetags/base64_filters.py
from django import template
import base64 as b64_lib

register = template.Library()

@register.filter
def b64encode(buffer):
    if buffer:
        return b64_lib.b64encode(buffer.getvalue()).decode()
    return ''