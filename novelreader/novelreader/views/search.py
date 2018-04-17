#!/usr/bin/env python
# coding: utf-8
import logging
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import error, debug, info, warning
from .base import BaseViewMixin
from ..models.novelutil import (
    search_novels,
    add_search_stat
)

__author__ = 'samuel'
log = logging.getLogger(__name__)
PAGE_ITEMS = 20


class SearchView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(SearchView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(SearchView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        term = self._get_request_field('q')
        qtype = self._get_request_field('qtype')
        context['q'] = term or ''
        context['qtype'] = qtype or ''
        if term:
            # add a search statics
            context['sid'] = add_search_stat(qterm=term, qtype=qtype, uid=self.request.user.id) or ''

            novels = search_novels(term, qtype, page_items=PAGE_ITEMS, add_last_chapter=True)
            context['novels'] = novels
            if len(novels) <= 0:
                if qtype == 'name':
                    error(self.request, '没找到该名字的书. 如果是作者名，请尝试点击作者 <i class="fa fa-user"></i> 按钮搜索。')
                elif qtype == 'author':
                    error(self.request, '没找到该名字的作者. 如果是书名，请尝试点击书名 <i class="fa fa-book"></i> 按钮搜索。')
                else:
                    error(self.request, '没找到该名字或者作者的书. 请尝试减少查询字数重新搜索。')

            self.gen_pager_context(context, novels, page_items=PAGE_ITEMS)
        return context

    def _get_request_field(self, name, default=None):
        return self.request.POST.get(name, self.request.GET.get(name, default))