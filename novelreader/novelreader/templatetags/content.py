#!/usr/bin/env python
# coding: utf-8

from django import template
from django.template.defaultfilters import (
    stringfilter,
    striptags
)
from django.conf import settings
import re

__author__ = 'samuel'
register = template.Library()


keywords_to_clean = ['飘天\s*(文学)*', '书海阁', '17k']        # names
idx_separator = len(keywords_to_clean)              # index to separate names & domains
keywords_to_clean.extend(['piaotian.com', 'qidian.com', '17k.com'])     # domains
my_domain = settings.WEBSITE.get('domain')
my_site_name = settings.WEBSITE.get('name')

# vars
regx_keywords = [r'%s' % k.replace('.', r'\.') for k in keywords_to_clean]
regx_keywords = [re.compile(k, re.IGNORECASE | re.MULTILINE) for k in regx_keywords]

regx_blank = re.compile(r'&nbsp;', re.IGNORECASE | re.MULTILINE)
regx_br = re.compile(r'<br\s*/?>', re.IGNORECASE | re.MULTILINE)

sql_keys = ['%%%s%%' % k for k in keywords_to_clean]


@register.filter(name='clean', is_safe=True)
@stringfilter
def clean(value, *args):

    value = regx_blank.sub('　', value)      # Chinese blank
    # value = regx_br.sub('', value)

    i = 0
    for regx in regx_keywords:
        if i >= idx_separator:
            value = regx.sub(my_domain, value)
        else:
            value = regx.sub(my_site_name, value)
        i += 1
    return value