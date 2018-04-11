#!/usr/bin/env python
# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views import View
from ..models.novelutil import (
    switch_novel_favorite,
    recommend_novel,
    update_search_hit,
    add_search_stat,
    add_novel_view_count,
)
import logging

__author__ = 'samuel'
log = logging.getLogger(__name__)


class StatView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        novel_id = request.POST.get('novel_id')

        status = None
        if action == 'favorite':
            rc = switch_novel_favorite(novel_id, self.request.user.id)
            status = 'on' if rc else 'off'
        elif action == 'recommend':
            status = recommend_novel(novel_id, self.request.user.id)
        elif action == 'search-hit':
            sid = request.POST.get('sid')
            if sid:
                status = update_search_hit(sid=sid, nid=novel_id)
            else:
                qterm = request.POST.get('qterm')
                qtype = request.POST.get('qtype')
                status = add_search_stat(qterm=qterm, qtype=qtype, nid=novel_id, uid=self.request.user.id)
        elif action == 'novel-view':
            status = add_novel_view_count(novel_id=novel_id)
        else:
            pass

        return JsonResponse({"status": status, "message": " "})

