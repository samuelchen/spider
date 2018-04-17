#!/usr/bin/env python
# coding: utf-8

from django import template
from django.template.defaultfilters import (
    stringfilter,
)
from utils import clean_content

__author__ = 'samuel'
register = template.Library()



@register.filter(name='clean', is_safe=True)
@stringfilter
def clean(value, *args):

    return clean_content(value, *args)