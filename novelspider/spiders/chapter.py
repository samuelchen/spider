# -*- coding: utf-8 -*-

import scrapy
import logging
from ..db import Database, select, and_, not_
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
LIMIT_NOVELS = settings['LIMIT_NOVELS']
log = logging.getLogger(__name__)


class ChapterSpider(scrapy.Spider):
    name = 'chapter'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/html/8/8955/']

    chapter_counters = {}

    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.start_urls = []
        self.limit = LIMIT_NOVELS

        return super(ChapterSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        tn = self.db.DB_table_novel
        # noinspection PyComparisonWithNone
        stmt = select([tn.c.id, tn.c.name, tn.c.url_index, tn.c.chapter_table]
                    ).order_by(tn.c.recommends.desc()
                    ).where(and_(tn.c.done==False, not_(tn.c.url_index==None)))
        if self.limit > 0:
            stmt = stmt.limit(self.limit)
        rs = self.db.engine.execute(stmt)
        # loop all novels index pages
        for r in rs:
            table = r['chapter_table']
            t = self.db.get_chapter_table(table)
            t.create(self.db.engine, checkfirst=True)

            self.chapter_counters[r['id']] = {'count': 0, 'saved': 0, 'done': False}
            log.info('Parsing chapters for novel %(name)s(id=%(id)s) %(url_index)s' % r)
            yield scrapy.Request(r['url_index'], meta={'table': table, 'novel_id': r['id']})

    def parse(self, response):

        # if 'Bandwidth exceeded' in response.body:
        #     raise scrapy.exceptions.CloseSpider('bandwidth_exceeded')

        # parse index page of a novel
        novel_url = response.url
        if novel_url.endswith('index.html'):
            novel_url = novel_url[:novel_url.rindex('/')] + '/'

        meta = response.meta
        table = meta['table']
        novel_id = meta['novel_id']
        idx = 1
        finished_chapters = set()
        finished_sections = set()

        # finished chapters
        t = self.db.get_chapter_table(table)
        stmt = select([t.c.id, t.c.name, t.c.is_section, t.c.url]).where(t.c.done==True)
        rs = self.db.engine.execute(stmt)
        self.chapter_counters[novel_id]['saved'] = rs.rowcount
        log.info('Will skip %s chapters which were saved.' % rs.rowcount)

        # cache finished urls
        for r in rs:
            if r[t.c.is_section]:
                finished_sections.add(r[t.c.name])
            else:
                finished_chapters.add(r[t.c.url])

        # loop all chapter links in current page
        for x in response.css('div.centent > *'):
            # section title has no li
            is_section = x.css('li:first-child').extract_first() is None
            if is_section:
                name = x.css('div::text').extract_first()
                if name:
                    self.chapter_counters[novel_id]['count'] += 1
                    if name not in finished_sections:
                        yield {
                            "table": table,
                            "novel_id": novel_id,

                            "idx": idx,
                            "name": name,
                            "url": None,
                            "content": None
                        }
                    else:
                        log.info('Skipped saved section %s' % name)
                    idx += 1

            else:
                # chapter
                for y in x.css('li'):
                    url = y.css('a::attr("href")').extract_first()
                    name = y.css('a::text').extract_first()
                    if url and name:
                        self.chapter_counters[novel_id]['count'] += 1
                        if url not in finished_chapters:
                            item = {
                                "table": table,
                                "novel_id": novel_id,

                                "idx": idx,
                                "name": name.strip(),
                                "url": url.strip(),
                            }
                            yield scrapy.Request(novel_url + url, callback=self.parse_content, meta={"item": item})
                        else:
                            log.info('Skipped saved chapter %s' % name)
                        idx += 1

        self.chapter_counters[novel_id]['done'] = True

    def parse_content(self, response):
        item = response.meta['item']

        txt = response.text
        i = txt.find('<br')
        txt = txt[i:]
        j = txt.find('<!-- 翻页上AD开始 -->')
        txt = txt[:j]
        item['content'] = txt
        return item

