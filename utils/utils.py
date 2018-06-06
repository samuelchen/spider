#!/usr/bin/env python
# coding: utf-8

from functools import wraps
from time import time
import re
from django.conf import settings
import os
import zipstream


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


# ---- clean content -----
keywords_to_clean = ['飘天\s*(文学)*', '书海阁', '17k']        # names
idx_separator = len(keywords_to_clean)              # index to separate names & domains
keywords_to_clean.extend(['piaotian.com', 'qidian.com', '17k.com'])     # domains
my_domain = settings.WEBSITE.get('domain')
my_site_name = settings.WEBSITE.get('name')

regx_keywords = [r'%s' % k.replace('.', r'\.') for k in keywords_to_clean]
regx_keywords = [re.compile(k, re.IGNORECASE | re.MULTILINE) for k in regx_keywords]

regx_blank = re.compile(r'(&nbsp;)+', re.IGNORECASE | re.MULTILINE)
regx_br = re.compile(r'<br\s*/?>', re.IGNORECASE | re.MULTILINE)
regx_newline = re.compile(r'[\r|\n]+', re.IGNORECASE | re.MULTILINE)

sql_keys = ['%%%s%%' % k for k in keywords_to_clean]


def clean_content(value, *args, **kwargs):

    value = regx_blank.sub('　　', value)      # Chinese blank
    value = regx_br.sub('\r\n', value)
    value = regx_newline.sub('\r\n\r\n', value)

    i = 0
    for regx in regx_keywords:
        if i >= idx_separator:
            value = regx.sub(my_domain, value)
        else:
            value = regx.sub(my_site_name, value)
        i += 1
    return value


class ZipUtilities:
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def toZip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.addFolderToZip(file, name)

    def addFolderToZip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(name, os.path.basename(full_path)))
            elif os.path.isdir(full_path):
                self.addFolderToZip(full_path, os.path.join(name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()


__all__ = [
    'timeit',
    'is_valid_username',
    'clean_content',
    'ZipUtilities',
]
