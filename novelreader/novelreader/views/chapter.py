#!/usr/bin/evn python

import logging
from django.http import Http404
from django.views.generic import TemplateView
from ..models.novelutil import (
    get_novel_info, get_latest_chapters, get_all_chapters,
    list_hot_novels, list_recommend_novels, get_chapter
)
from .base import BaseViewMixin
from ..models.novelstat import load_user_novel_state

__author__ = 'samuel'

log = logging.getLogger(__name__)


class ChapterView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(ChapterView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChapterView, self).get_context_data(**kwargs)
        nid = kwargs.get('nid', None)
        cid = kwargs.get('cid', None)
        if nid is None:
            raise Http404('Novel does not exist.')
        novel = get_novel_info(nid, add_last_chapter=False)
        context['novel'] = novel
        context['chapter'] = get_chapter(cid, chapter_table=novel['chapter_table'], with_next=True, with_prev=True)
        context['state'] = load_user_novel_state(self.request.user, nid)
        return context
