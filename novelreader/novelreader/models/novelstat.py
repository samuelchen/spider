#!/usr/bin/env python
# coding: utf-8

from .novel import UserFavorite
import logging

__author__ = 'Samuel Chen <samuel.net@gmail.com>'
log = logging.getLogger(__name__)


# ===== Stat functions =====

def load_user_novel_list_states(user, novels):
    # favorites = UserFavorite.objects.filter(user=user)
    pass

def load_user_novel_state(user, novel_id):
    state = {}
    if user.is_authenticated:
        state['is_favor'] = len(UserFavorite.objects.filter(user=user, novel_id=novel_id).all()) > 0
    return state