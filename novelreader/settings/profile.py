#!/usr/bin/env python
# coding: utf-8

from ._base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS.extend([
    'silk'
])

MIDDLEWARE.extend([
    'silk.middleware.SilkyMiddleware',
])
SILKY_PYTHON_PROFILER = True
SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
SILKY_MAX_RESPONSE_BODY_SIZE = 0  # If response body>0kb, ignore
SILKY_META = True
SILKY_AUTHENTICATION = True     # User must login
SILKY_AUTHORISATION = True      # User must have permissions
SILKY_INTERCEPT_PERCENT = 50    # log only 50% of requests

SILKY_MAX_RECORDED_REQUESTS = 10000             # garbage collection, keep 10000 records
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10  # 10% requests run garbage collection


SILKY_DYNAMIC_PROFILING = [
    {'module': 'novelreader.models.novelutil', 'function': 'list_novels'},
    {'module': 'novelreader.templatetags.content', 'function': 'clean'},
]