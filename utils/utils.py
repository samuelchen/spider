#!/usr/bin/env python
# coding: utf-8

from functools import wraps
from time import time

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