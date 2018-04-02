#!/usr/bin/env python
# coding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from ..models.novel import UserFavorite
import logging

__author__ = 'samuel'
log = logging.getLogger(__name__)


class StatView(View):

    def post(self, request, *args, **kwargs):
        novel_id = request.POST.get('novel_id')
        novel_name = request.POST.get('novel_name')
        favor, created = UserFavorite.objects.get_or_create(user=request.user, novel_id=novel_id, novel_name=novel_name)

        if created:
            status = "on"
        else:
            favor.delete()
            status = "off"

        return JsonResponse({"status": status, "message": " "})

