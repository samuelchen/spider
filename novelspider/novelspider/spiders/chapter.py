# -*- coding: utf-8 -*-

import scrapy
import logging
from ..db import Database, select, and_, not_, mark_done
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
LIMIT_NOVELS = settings['LIMIT_NOVELS']
SPIDER_ID = settings['SPIDER_ID']
log = logging.getLogger(__name__)


class ChapterSpider(scrapy.Spider):
    name = 'chapter'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/html/8/8955/']

    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.start_urls = []
        self.limit = LIMIT_NOVELS

        # chapter counters for novel {novel_id: {'count': 0, 'saved': 0, 'done': False} }
        # "count": used to calculate total chapters count
        # "saved": used to calculate saved chapters count
        # "done": is a flag to control weather total chapters count ("count") is finished counting.
        self.chapter_counters = {}

        super(ChapterSpider, self).__init__(*args, **kwargs)

    def start_requests(self):

        # novels to be downloaded
        tn = self.db.DB_table_novel
        tl = self.db.DB_table_novel_lock
        # noinspection PyComparisonWithNone
        stmt1 = select([tl.c.novel_id]).where(tl.c.locker!=SPIDER_ID)
        stmt = select([tn.c.id, tn.c.name, tn.c.url_index, tn.c.chapter_table]
                    ).where(and_(tn.c.done==False, not_(tn.c.url_index==None), not_(tn.c.id.in_(stmt1)))
                    ).order_by(tn.c.recommends.desc())
        if self.limit > 0:
            stmt = stmt.limit(self.limit)
        rs = self.db.engine.execute(stmt)

        # lock novels
        novels = []
        for r in rs:
            rc = self.db.lock_novel(novel_id=r['id'], locker=SPIDER_ID, name=r['name'])
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
        idx = 10

        # finished chapters including chapter, section and conflicts
        finished_sections, finished_chapters = self.cache_finished_chapters(table)
        # keep count of saved chapters. calculate from this number.
        self.chapter_counters[novel_id]['saved'] = len(finished_chapters) + len(finished_sections)
        log.info('Will skip %s chapters which were saved.' % self.chapter_counters[novel_id]['saved'])

        # loop all chapter links in current page
        for x in response.css('div.centent > *'):
            # section title has no li
            is_section = x.css('li:first-child').extract_first() is None
            if is_section:
                name = x.css('div::text').extract_first()
                name = name.strip() if name else name
                if name:
                    self.chapter_counters[novel_id]['count'] += 1       # total count + 1
                    if name not in finished_sections:
                        log.info('Requesting section %s(id=%s) of %s' % (name, idx, table))
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
                    idx += 10

            else:
                # chapter
                for y in x.css('li'):
                    url = y.css('a::attr("href")').extract_first()
                    name = y.css('a::text').extract_first()
                    url = url.strip() if url else url
                    name = name.strip() if name else name
                    if url and name and url != '#' and not url.startswith('javascript:'):
                        name = name.strip()
                        url = url.strip()
                        self.chapter_counters[novel_id]['count'] += 1           # total count + 1
                        if url not in finished_chapters:
                            log.info('Requesting chapter %s(id=%s, %s) of %s' % (name, idx, url, table))
                            item = {
                                "table": table,
                                "novel_id": novel_id,

                                "idx": idx,
                                "name": name,
                                "url": url,
                            }
                            yield scrapy.Request(novel_url + url, callback=self.parse_content, meta={"item": item})
                        else:
                            log.info('Skipped saved chapter %s' % name)
                        idx += 10

        self.chapter_counters[novel_id]['done'] = True
        log.info('Chapters counts: total=%(count)s, saved=%(saved)s (including conflicts)' % self.chapter_counters[novel_id])
        # it maybe all saved but not marked done. So mark it done here because it will not yield to pipeline.
        if self.chapter_counters[novel_id]['saved'] >= self.chapter_counters[novel_id]['count']:
            # TODO: possible finished but chapters counting not done ?
            # mark this novel done
            tn = self.db.DB_table_novel
            mark_done(self.db.engine, tn, tn.c.id, [novel_id, ])
            log.info('Novel %s is finished downloading.' % table)
            self.db.unlock_novel(novel_id=novel_id, locker=SPIDER_ID)

    def parse_content(self, response):
        item = response.meta['item']

        txt = response.text
        i = txt.find('<br')
        # txt = txt[i:]
        j = txt.find('<!-- 翻页上AD开始 -->', i)
        # txt = txt[:j]
        k = txt.rfind('</div>', i, j)
        txt = txt[i:k if k > 0 else j]

        # TODO: remove source site name/link lines
        item['content'] = txt
        return item

    def log_novels(self, novels):
        import os

        base_dir = settings['BASE_DIR']
        fname = os.path.join(base_dir, 'log', 'chapter_novels.log')
        with open(fname, 'w') as f:
            f.write('novel')
            for r in novels:
                f.write('+')
                f.write('%s_%s' % (r['id'], r['name']))
            f.write('.log')

    def cache_finished_chapters(self, table):
        finished_chapters = set()
        finished_sections = set()

        # finished chapters
        t = self.db.get_chapter_table(table)
        stmt = select([t.c.id, t.c.name, t.c.is_section, t.c.url])
        rs = self.db.engine.execute(stmt)

        # cache finished urls
        for r in rs:
            if r[t.c.is_section]:
                finished_sections.add(r[t.c.name])
            else:
                finished_chapters.add(r[t.c.url])

        # conflict chapters
        if self.db.exist_table(table + '_conflict'):
            t = self.db.get_chapter_conflict_table(table)
            stmt = select([t.c.id, t.c.name, t.c.is_section, t.c.url])
            rs = self.db.engine.execute(stmt)

            # cache conflict urls
            for r in rs:
                if r[t.c.is_section]:
                    if r[t.c.name] in finished_sections:
                        # do not miss duplicated section, otherwise, will miss a saved count.
                        finished_sections.add('%s_%s' % (r[t.c.name], r[t.c.id]))
                    else:
                        finished_sections.add(r[t.c.name])
                else:
                    finished_chapters.add(r[t.c.url])

        return finished_sections, finished_chapters
