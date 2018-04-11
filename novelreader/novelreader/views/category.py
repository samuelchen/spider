#!/usr/bin/evn python

import logging
from django.http import Http404
from django.views.generic import TemplateView
from ..models.novelutil import (
    list_novels_by_category,
    list_hot_novels_by_category,
    list_recommend_novels_by_category,
    list_favorite_novels_by_category,
)
from .base import BaseViewMixin

__author__ = 'samuel'
categories = '玄幻魔法 武侠修真 都市言情 历史军事 网游竞技 科幻小说 恐怖灵异 同人漫画 其他类型 全本'.split(' ')
log = logging.getLogger(__name__)
PAGE_ITEMS = 30


class CategoryView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(CategoryView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)

        category = kwargs.get('category')
        page = int(self.request.GET.get('p', 0))
        context['category'] = category
        context['p'] = page

        if category in categories:
            novels = list_novels_by_category(category, page=page, page_items=PAGE_ITEMS, add_last_chapter=True)
            context['novels_top'] = novels[0:4]
            context['novels'] = novels[4:]
        else:
            raise Http404('未找到此类型小说')

        self.gen_pager_context(context, context['novels'], page_items=PAGE_ITEMS)

        context['top_a'] = {
            "title": "热门小说", "subtitle": category, "icon": "fa fa-fire",
            "novels": list_hot_novels_by_category(category, page_items=13)
        }

        context['tops_b'] = [
            {"title": "推荐榜", "subtitle": category, "icon": "fa fa-thumbs-up",
             "novels": list_recommend_novels_by_category(category, page_items=13)},
            {"title": "收藏榜", "subtitle": category, "icon": "fa fa-star",
             "novels": list_favorite_novels_by_category(category, page_items=13)},
        ]
        return context
