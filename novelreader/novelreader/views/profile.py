#!/usr/bin/evn python

import logging
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import error, debug, info, warning
from .base import BaseViewMixin
from ..models import UserFavorite

__author__ = 'samuel'

log = logging.getLogger(__name__)


class ProfileView(TemplateView, BaseViewMixin, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        warning(request, '暂时不支持修改个人资料')
        return super(ProfileView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        error(request, "暂时不支持修改个人资料")
        return super(ProfileView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['tab'] = self.request.GET.get('t')
        context['user'] = self.request.user
        context['favorites'] = UserFavorite.objects.filter(user=self.request.user)

        return context
