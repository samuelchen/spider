#!/usr/bin/evn python

import logging
from django.http import Http404
from django.views.generic import TemplateView
from ..models.novelutil import (
    get_novel_info, get_latest_chapters, get_all_chapters,
    list_hot_novels, list_recommend_novels, get_chapter
)
from .base import BaseViewMixin

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
        novel = get_novel_info(nid, add_last_chapter=False, with_actions_user_id=self.request.user.id)
        context['novel'] = novel
        context['chapter'] = get_chapter(cid, chapter_table=novel['chapter_table'], with_next=True, with_prev=True)

        # TODO: temporally for un-cleaned html tags in content.(NEED REMOVE if cleaned)
        s = context['chapter']['content']
        if s:
            idx = s.rfind('</div>')
            if idx > 0:
                context['chapter']['content'] = s[0:idx]

        return context
