from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
import logging

__author__ = 'samuel'
USER_MODEL = get_user_model()
log = logging.getLogger(__name__)


class UserFavorite(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(USER_MODEL)
    novel_id = models.IntegerField()
    novel_name = models.CharField(max_length=100)

    class Meta:
        index_together = [
            ('user', 'novel_id'),
        ]
        unique_together = [
            ("user", "novel_id"),
        ]


# class UserHistory(models.Model):
#     pass


# class NovelStatics(models.Model):
#     id = models.IntegerField(primary_key=True, auto_created=True)
#     novel_id = models.IntegerField(unique=True, db_index=True)
#     novel_name = models.CharField(max_length=100)
#     novel_author = models.CharField(max_length=50)
#
#     searches = models.IntegerField(default=0)
#     searches_year = models.IntegerField(default=0)
#     searches_month = models.IntegerField(default=0)
#     searches_week = models.IntegerField(default=0)
#
#     views = models.IntegerField(default=0, help_text='How many times novel are read.')
#     views_year = models.IntegerField(default=0)
#     views_month = models.IntegerField(default=0)
#     views_week = models.IntegerField(default=0)
#     # chapter_views = models.IntegerField(default=0, help_text='How many chapters are read.')
#
#     recommends = models.IntegerField(default=0)
#     recommends_year = models.IntegerField(default=0)
#     recommends_month = models.IntegerField(default=0)
#     recommends_week = models.IntegerField(default=0)
#
#     favorites = models.IntegerField(default=0)
#     favorites_year = models.IntegerField(default=0)
#     favorites_month = models.IntegerField(default=0)
#     favorites_week = models.IntegerField(default=0)
#
#     featured = models.BooleanField(default=False, help_text='site featured')
#     selected = models.BooleanField(default=False, help_text='editor choice')
#
#     picked = models.IntegerField(default=0, help_text='Weight of picked. Auto filled by AI. 1-10')
#
#     timestamp = models.DateTimeField(auto_now=True)