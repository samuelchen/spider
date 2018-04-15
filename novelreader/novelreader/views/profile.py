#!/usr/bin/evn python

import logging
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import error, debug, info, warning
from .base import BaseViewMixin
from ..models.novelutil import list_user_favorites
from utils import is_valid_username

__author__ = 'samuel'

log = logging.getLogger(__name__)


# @method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        return super(ProfileView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:
            # Use user.first_name as fullname
            fullname = request.POST.get('fullname')
            if fullname and is_valid_username(fullname):
                request.user.first_name = fullname
                request.user.save()
            else:
                error(request, '无效的名字，请重新输入，只支持中文，英文和空格')

        return super(ProfileView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['tab'] = self.request.GET.get('t')
        context['user'] = self.request.user

        if self.request.user.is_authenticated:
            context['favorites'] = list_user_favorites(user_id=self.request.user.id)
        else:
            context['tab'] = 'history'

        return context
