# -*- coding: utf-8 -*-
from collections import OrderedDict
import scrapy
import logging
from ..db import Database, select, and_, not_

log = logging.getLogger(__name__)


# TODO: TO BE DELETED
class ChapterContentSpider(scrapy.Spider):
    name = 'content'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/html/8/8955/5841516.html']

    def __init__(self, *args, **kwargs):
        self.db = Database()
        # self.start_urls = []
        return super(ChapterContentSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        tn = self.db.DB_table_novel
        stmt = select([tn.c.id, tn.c.name, tn.c.url_index, tn.c.chapter_table]).where(and_(tn.c.done==False, not_(tn.c.url_index==None)))
        rs = self.db.engine.execute(stmt)
        for r in rs:
            t = self.db.get_chapter_table(r['chapter_table'])
            stmt = select([t.c.id, t.c.url]).where(t.c.done==False)
            rs_chapter = self.db.engine.execute(stmt)
            for c in rs_chapter:
                yield scrapy.http.Request(c['url'], dont_filter=True, meta={'id':c['id'], 'table':r['chapter_table']})

    def parse(self, response):
        # print(response.text)
        url = response.url
        meta = response.meta
        chapter_id = meta['id']
        table = meta['table']

        txt = response.text
        i = txt.find('<br')
        txt = txt[i:]
        j = txt.find('<!-- 翻页上AD开始 -->')
        txt = txt[:j]
        # ztxt = zlib.compress(txt)
        yield {
            'table': table,
            'id': chapter_id,
            'url': url,
            'text': txt
        }
