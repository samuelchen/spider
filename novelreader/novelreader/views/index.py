#!/usr/bin/evn python

import logging
from django.views.generic import TemplateView
from ..models.novelutil import (
    list_update_novels, list_recommend_novels, list_favorite_novels, list_hot_novels,
    list_choice_novels
)
from .base import BaseViewMixin

__author__ = 'samuel'

log = logging.getLogger(__name__)


class IndexView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['choice_novels'] = list_choice_novels(page_items=4, with_actions_user_id=self.request.user.id)

        update_novels = list_update_novels(page_items=20, add_last_chapter=True)
        context['update_novels_top'] = update_novels[:4]
        context['update_novels'] = update_novels[4:]

        context['top_a'] = {
            "title": "热门小说", "subtitle": "", "icon": "fa fa-fire",
            "novels": list_hot_novels(page_items=19)
        }

        context['tops_b'] = [
            {"title": "推荐榜", "subtitle": "", "novels": list_recommend_novels(page_items=22), "icon": "fa fa-thumbs-up"},
            {"title": "收藏榜", "subtitle": "", "novels": list_favorite_novels(page_items=22), "icon": "fa fa-star"},
        ]
        return context
