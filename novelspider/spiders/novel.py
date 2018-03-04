# -*- coding: utf-8 -*-
import scrapy
import logging
from ..db import Database, select
from ..settings import LIMIT_INDEX_PAGES

log = logging.getLogger(__name__)


class NovelSpider(scrapy.Spider):
    name = 'novel'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/booksort1/0/1.html']

    def __init__(self, *args, **kwargs):
        self.db = Database()

        self.db.DB_table_novel.create(self.db.engine, checkfirst=True)
        self.pages = 0

        t = self.db.DB_table_home
        stmt = select([t.c.url]).where(t.c.done==False)
        rs = self.db.engine.execute(stmt)
        self.start_urls = [r['url'] for r in rs]

        return super(NovelSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        for x in response.css('table.grid > tr > td:first-child > a'):
            name = x.css('a::text').extract_first()
            url = x.css('a::attr("href")').extract_first()
            item = {
                "name": name,
                "url": url
            }

            yield response.follow(url, meta={"item":item}, callback=self.parse_novel)

        # mark_done(self.db.engine, self.db.DB_table_home,
        #           self.db.DB_table_home.c.url, [response.url])

        self.pages += 1
        if LIMIT_INDEX_PAGES > 0 and self.pages > LIMIT_INDEX_PAGES:
            return

        next_page = response.css('div.pagelink > a.next::attr("href")').extract_first()
        log.debug('next page: %s' % next_page)
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_novel(self, response):

        item = response.meta['item']
        r = {}
        # r['url'] = response.url
        r['name'] = response.css('div#content h1::text').extract_first()
        assert r['name'] == item['name']
        line1 = response.css('div#content > table > tr:first-child > td > table > tr:nth-of-type(2) > td::text')
        r['category'] = line1[0].extract().split('：')[1]
        r['author'] = line1[1].extract().split('：')[1]
        r['length'] = int(line1[3].extract().split('：')[1].strip('字'))

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
        r['url_index'] = response.css('div#content > table > tr:nth-of-type(8)').css('caption > a::attr("href")').extract_first()

        item.update(r)
        return item