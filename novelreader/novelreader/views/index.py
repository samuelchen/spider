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

        update_novels = list_update_novels(add_last_chapter=True)
        context['update_novels_top'] = update_novels[:3]
        context['update_novels'] = update_novels[3:]
        context['recommend_novels'] = list_recommend_novels()
        context['favorite_novels'] = list_favorite_novels()
        context['hot_novels'] = list_hot_novels()
        context['choice_novels'] = list_choice_novels(page_items=6)

        return context
