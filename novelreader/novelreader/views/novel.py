#!/usr/bin/evn python

import logging
from django.http import Http404
from django.views.generic import TemplateView
from ..models.novelutil import (
    get_novel_info, get_latest_chapters, get_all_chapters,
    list_hot_novels, list_recommend_novels, list_favorite_novels
)
from .base import BaseViewMixin

__author__ = 'samuel'

log = logging.getLogger(__name__)


class NovelView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(NovelView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NovelView, self).get_context_data(**kwargs)
        nid = kwargs.get('nid', None)
        if nid is None:
            raise Http404('Novel does not exist.')

        novel = get_novel_info(nid, add_last_chapter=True, with_actions_user_id=self.request.user.id)
        if not novel:
            raise Http404('Novel (id=%s) is not found' % nid)

        context['novel'] = novel
        context['latest_chapters'] = get_latest_chapters(nid)
        context['chapters'] = get_all_chapters(nid)


        context['top_a'] = {
            "title": "热门小说", "subtitle": "", "keyword": "hot", "icon": "fa fa-fire",
            "novels": list_hot_novels(page_items=5)
        }

        context['tops_b'] = [
            {"title": "推荐榜", "subtitle": "", "keyword": "recommend",
             "novels": list_recommend_novels(page_items=6), "icon": "fa fa-thumbs-up"},
            {"title": "收藏榜", "subtitle": "",  "keyword": "favorite",
             "novels": list_favorite_novels(page_items=6), "icon": "fa fa-star"},
        ]

        return context
