#!/usr/bin/env python
# coding: utf-8

from functools import wraps
from time import time
import re

__author__ = 'Samuel Chen <samuel.net@gmail.com>'
__date__ = '4/6/2018 1:24 AM'


def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result
    return wrap


regx_name = re.compile(r"^[\u4e00-\u9fa5a-zA-Z][\u4e00-\u9fa5a-zA-Z ]+$", re.IGNORECASE)
def is_valid_username(name):
    return regx_name.match(name) is not None

__all__ = [
    'timeit',
    'is_valid_username',
]
