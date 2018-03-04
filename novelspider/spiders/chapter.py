# -*- coding: utf-8 -*-
from collections import OrderedDict
import scrapy
import logging
from ..db import Database, mark_done, select, and_, not_
from ..settings import LIMIT_NOVELS

log = logging.getLogger(__name__)


class ChapterSpider(scrapy.Spider):
    name = 'chapter'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/html/8/8955/']

    def __init__(self, *args, **kwargs):
        self.db = Database()
        # self.start_urls = []
        self.limit = LIMIT_NOVELS

        return super(ChapterSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        tn = self.db.DB_table_novel
        stmt = select([tn.c.id, tn.c.url_index, tn.c.chapter_table]
                    ).where(and_(tn.c.done==False, not_(tn.c.url_index==None)))
        if self.limit > 0:
            stmt = stmt.limit(self.limit)
        rs = self.db.engine.execute(stmt)
        for r in rs:
            yield scrapy.http.Request(r['url_index'], dont_filter=True, meta={'table':r['chapter_table']})
            mark_done(self.db.engine, tn, tn.c.id, [r['id'], ])
    def parse(self, response):
        current_url = response.url
        if current_url.endswith('index.html'):
            current_url = current_url[:current_url.rindex('/')] + '/'
        meta = response.meta
        table = meta['table']

        for x in response.css('div.centent > *'):
            is_section = x.css('li:first-child').extract_first() is None
            if is_section:
                name = x.css('div::text').extract_first()
                if name:
                    yield {
                        "table": table,
                        "name": name,
                        "url": None,
                        "content": None
                    }
            else:
                for y in x.css('li'):
                    url = y.css('a::attr("href")').extract_first()
                    name = y.css('a::text').extract_first()
                    if url and name:
                        item = {
                            "table": table,
                            "name": name,
                            "url": current_url + url,
                        }
                    yield scrapy.http.Request(item['url'], meta={"item":item},
                                              callback=self.parse_content)

    def parse_content(self, response):
        item = response.meta['item']

        txt = response.text
        i = txt.find('<br')
        txt = txt[i:]
        j = txt.find('<!-- 翻页上AD开始 -->')
        txt = txt[:j]
        item['content'] = txt
        return item