# -*- coding: utf-8 -*-

import os
import scrapy
import logging
from ..db import Database, select, and_, not_, mark_done
from .chapter import ChapterSpider
# from scrapy.utils.project import get_project_settings
#
# settings = get_project_settings()
# LIMIT_NOVELS = settings['LIMIT_NOVELS']
# SPIDER_ID = settings['SPIDER_ID']
log = logging.getLogger(__name__)


class SingleSpider(ChapterSpider):
    name = 'single'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/html/8/8955/']

    def __init__(self, *args, **kwargs):
        super(SingleSpider, self).__init__(*args, **kwargs)

        self.novel_name = kwargs.get('n')
        self.db = Database()
        self.start_urls = []
        # # self.limit = LIMIT_NOVELS
        # self.limit = self.settings.get('LIMIT_NOVELS', 1)
        # self.SPIDER_ID = self.settings.get('SPIDER_ID')

        # chapter counters for novel {novel_id: {'count': 0, 'saved': 0, 'done': False} }
        # "count": used to calculate total chapters count
        # "saved": used to calculate saved chapters count
        # "done": is a flag to control weather total chapters count ("count") is finished counting.
        self.chapter_counters = {}


    @property
    def LIMIT_NOVELS(self):
        return 1

    def start_requests(self):

        print(self.name, self.novel_name)

        if not self.novel_name:
            log.error('Novel name must be specified ("-a n=novel_name") for "single novel" spider.')
            return

        # novels to be downloaded
        tn = self.db.DB_table_novel
        tl = self.db.DB_table_novel_lock
        # noinspection PyComparisonWithNone
        stmt1 = select([tl.c.novel_id]).where(tl.c.locker!=self.SPIDER_ID)
        stmt = select([tn.c.id, tn.c.name, tn.c.url_index, tn.c.chapter_table]
                    ).where(and_(tn.c.done==False, tn.c.name==self.novel_name, not_(tn.c.id.in_(stmt1))))
        rs = self.db.engine.execute(stmt)

        # lock novels
        novels = []
        for r in rs:
            rc = self.db.lock_novel(novel_id=r['id'], locker=self.SPIDER_ID, name=r['name'])
            if rc >= 0:
                # only add unlocked or locked-by-self novels
                novels.append(r)

        # loop all locked novels' index page
        for r in novels:
            table = r['chapter_table']
            t = self.db.get_chapter_table(table)
            t.create(self.db.engine, checkfirst=True)

            self.chapter_counters[r['id']] = {'count': 0, 'saved': 0, 'done': False}
            log.info('Parsing chapters for novel %(name)s(id=%(id)s) %(url_index)s' % r)

            yield scrapy.Request(r['url_index'], meta={'table': table, 'novel_id': r['id']})

        self.log_novels(novels)

