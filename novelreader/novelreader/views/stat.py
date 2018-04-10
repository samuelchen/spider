#!/usr/bin/env python
# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views import View
from ..models.novelutil import (
    switch_novel_favorite,
    recommend_novel,
)
import logging

__author__ = 'samuel'
log = logging.getLogger(__name__)


class StatView(View, LoginRequiredMixin):

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        novel_id = request.POST.get('novel_id')

        status = None
        if action == 'favorite':
            rc = switch_novel_favorite(novel_id, self.request.user.id)
            status = 'on' if rc else 'off'
        elif action == 'recommend':
            status = recommend_novel(novel_id, self.request.user.id)
        elif action == 'search-result':
            add
        else:
            pass

        return JsonResponse({"status": status, "message": " "})

