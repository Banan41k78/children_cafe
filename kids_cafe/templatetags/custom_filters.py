import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

BAD_WORDS = [
   r'ху[ейёяю]',r'хул[ию]',r'пизд',r'пи[зс]д',r'[eё]б',r'ебу',r'бля',r'сук[аи]'
]

PATTERN = re.compile(r'\b(?:' + '|'.join(BAD_WORDS) + r')\w*',re.IGNORECASE | re.UNICODE)

def censor(text):
    return PATTERN.sub('***',text)

def linkify(text):
    url_pattern = re.compile(
        r'(https?://[^\s]+|www\.[^\s]+)'
    )
    def repl(m):
        url = m.group(0)
        if not url.startswith('http'):
            url = 'http://' + url
        return f'<a href="{url}" target="_blank" rel="nofollow">{m.group(0)}</a>'
    return url_pattern.sub(repl, text)

@register.filter
def censor_and_linkify(value):
    if not isinstance(value, str):
        return value
    censored = censor(value)
    linked = linkify(censored)
    return mark_safe(linked)