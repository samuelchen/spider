#!/usr/bin/evn python

import logging
from django.views.generic import View
from django.shortcuts import render_to_response


__author__ = 'samuel'

log = logging.getLogger(__name__)


class TestView(View):

    def get(self, request, *args, **kwargs):
        name = kwargs.get('name', 'index')

        return render_to_response('novelreader/test/%s.html' % name)

