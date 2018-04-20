# -*- coding: utf-8 -*-
from datetime import datetime, timezone, timedelta
import scrapy
import logging
from ..db import Database, select
from scrapy.utils.project import get_project_settings

UTC = timezone.utc
CST = timezone(timedelta(hours=8))

settings = get_project_settings()
LIMIT_INDEX_PAGES = settings['LIMIT_INDEX_PAGES']
log = logging.getLogger(__name__)


class NovelSpider(scrapy.Spider):
    name = 'novel'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/booksort1/0/1.html']

    def __init__(self, *args, **kwargs):
        self.db = Database()
        tn = self.db.DB_table_novel
        tl = self.db.DB_table_novel_lock
        tn.create(self.db.engine, checkfirst=True)
        tl.create(self.db.engine, checkfirst=True)
        self.pages = 0
        self.start_urls = []

        # cache all saved novels
        tn = select([tn.c.name])
        rs = self.db.engine.execute(tn)
        self.saved_novels = {r[tn.c.name] for r in rs}

        super(NovelSpider, self).__init__(*args, **kwargs)

    def start_requests(self):

        t = self.db.DB_table_home

        stmt = select([t.c.url, t.c.update_on])
        rs = self.db.engine.execute(stmt)
        for r in rs:
            yield scrapy.Request(r[t.c.url],
                                 meta={'last_update_on': r[t.c.update_on], 'home_url': r[t.c.url], 'dont_cache': True})

    def parse(self, response):
        log.info('Parsing %s list page %s' % (self.name, response.url))

        home_url = response.meta['home_url']
        last_update_on = response.meta['last_update_on']
        new_update_on = last_update_on
        update_done = False

        # if 'Bandwidth exceeded' in response.body:
        #     raise scrapy.exceptions.CloseSpider('bandwidth_exceeded')

        for x in response.css('table.grid > tr'):
            y = x.css('td:first-child > a')
            name = y.css('a::text').extract_first()
            url = y.css('a::attr("href")').extract_first()
            update_on = x.css('td:nth-of-type(5)::text').extract_first()
            update_on = datetime.strptime(update_on, '%y-%m-%d') if update_on else datetime.min
            update_on = update_on.replace(tzinfo=CST)

            if not name or not url:
                continue
            log.debug('extracted: %s %s %s' % (name, update_on.strftime('%Y-%m-%d'), url))

            if update_on >= last_update_on:
                # remember largest update_on date
                if update_on > new_update_on:
                    new_update_on = update_on
                    log.info('new update time becoming: %s' % new_update_on)
            else:
                if update_on == datetime.min:
                    continue
                # update_on date of this novel is smaller than last_update_on,
                # which means novels on rest home-index pages are not updated
                # because home-index pages are sorted by date desc.
                update_done = True
                log.info('%s update done due to novel (%s %s) is not updated (%s) since last update (%s)' % (
                    home_url, name, url, update_on.strftime('%y-%m-%d'), last_update_on.strftime('%y-%m-%d')))
                break

            # only yield item which is later than the date last updated.
            if name and url and update_on >= last_update_on:
                item = {
                    "name": name.strip(),
                    "url": url.strip(),
                    "is_updating": False
                }
                if name in self.saved_novels:
                    item['is_updating'] = True
                yield response.follow(url, meta={"item": item, "dont_cache": True}, callback=self.parse_novel)

        if update_done and new_update_on > last_update_on:
            # update latest update_on date to home
            t = self.db.DB_table_home
            log.info('Updating "%s" table last update_on to %s for %s:' % (t.name, new_update_on, home_url))
            stmt = t.update().values(update_on=new_update_on).where(t.c.url==home_url)
            try:
                self.db.engine.execute(stmt)
            except Exception:
                log.exception('Error when update update_on for home.')

            return

        self.pages += 1
        if self.pages > LIMIT_INDEX_PAGES > 0:
            log.info('Exit due to reach limitation (LIMIT_INDEX_PAGES=%s, %s)' % (LIMIT_INDEX_PAGES, home_url))
            return

        next_page = response.css('div.pagelink > a.next::attr("href")').extract_first()
        log.debug('next page: %s' % next_page)
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, meta=response.meta)

    def parse_novel(self, response):

        # TODO: need to check if None then strip()

        item = response.meta['item']
        r = {}
        # r['url'] = response.url
        r['name'] = response.css('div#content h1::text').extract_first().strip()

        line1 = response.css('div#content > table > tr:first-child > td > table > tr:nth-of-type(2) > td::text')
        r['category'] = line1[0].extract().split('：')[1].strip()
        r['author'] = line1[1].extract().split('：')[1].strip()
        r['length'] = int(line1[3].extract().split('：')[1].rstrip('字'))

        line2 = response.css('div#content > table > tr:first-child > td > table > tr:nth-of-type(3) > td::text')
        r['update_on'] = line2[0].extract().split('：')[1]
        r['status'] = line2[1].extract().split('：')[1]

        line3 = response.css('div#content > table > tr:first-child > td > table > tr:nth-of-type(4) > td::text')
        r['favorites'] = int(line3[0].extract().split('：')[1])
        r['recommends'] = int(line3[1].extract().split('：')[1])
        r['recommends_month'] = int(line3[2].extract().split('：')[1])

        #album
        r['album'] = response.css('div#content > table > tr:nth-of-type(4) > td > table > tr > td:nth-of-type(2) > a::attr("href")').extract()
        desc = response.css('div#content > table > tr:nth-of-type(4) > td > table > tr > td:nth-of-type(2) > div::text').extract()
        sb = []
        for x in desc:
            s = x.strip('\r\n\t ')
            if s:
                sb.append(s)
        r['desc'] = '\n'.join(sb)
        r['url_index'] = response.css('div#content > table > tr:nth-of-type(8)').css('caption > a::attr("href")').extract_first().strip()

        if r['name'] != item['name']:
            log.warn('Novel name on index page (%s) is different from its on novel page (%s) .' % (r['name'], item['name']))

        item.update(r)
        return item
