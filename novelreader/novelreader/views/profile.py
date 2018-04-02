#!/usr/bin/evn python

import logging
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models.novelutil import (
    get_novel_info, get_latest_chapters, get_all_chapters,
    list_hot_novels, list_recommend_novels, get_chapter
)
from .base import BaseViewMixin

__author__ = 'samuel'

log = logging.getLogger(__name__)


class ProfileView(TemplateView, BaseViewMixin, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        return super(ProfileView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
