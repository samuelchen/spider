#!/usr/bin/evn python

import logging
from django.http import Http404
from django.views.generic import TemplateView
from ..models.novelutil import (
    list_novels_by_category,
    list_hot_novels_by_category,
    list_recommend_novels_by_category,
    list_favorite_novels_by_category,

    list_favorite_novels,
    list_hot_novels,
    list_recommend_novels,
    list_update_novels,
)
from .base import BaseViewMixin

__author__ = 'samuel'
tops = {
    "update": "最近更新",
    "hot": "热门小说",
    "recommend": "总推荐榜",
    "favorite": "总收藏榜"
}
log = logging.getLogger(__name__)
PAGE_ITEMS = 30


class TopView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(TopView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopView, self).get_context_data(**kwargs)

        keyword = kwargs.get('top')
        page = int(self.request.GET.get('p', 0))
        context['top'] = keyword
        context['p'] = page
        context['title'] = tops.get(keyword)

        novels = []
        if keyword == 'update':
            novels = list_update_novels(page=page, page_items=PAGE_ITEMS, add_last_chapter=True)
        elif keyword == 'hot':
            novels = list_hot_novels(page=page, page_items=PAGE_ITEMS, add_last_chapter=True)
        elif keyword == 'recommend':
            novels = list_recommend_novels(page=page, page_items=PAGE_ITEMS, add_last_chapter=True)
        elif keyword == 'favorite':
            novels = list_favorite_novels(page=page, page_items=PAGE_ITEMS, add_last_chapter=True)
        else:
            raise Http404('未找到此类型小说')

        context['novels_top'] = novels[0:4]
        context['novels'] = novels[4:]
        self.gen_pager_context(context, novels, page_items=PAGE_ITEMS)

        return context
