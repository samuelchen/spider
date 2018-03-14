# -*- coding: utf-8 -*-
import scrapy
import re
import logging
from ..db import Database

log = logging.getLogger(__name__)


class HomeSpider(scrapy.Spider):
    name = 'home'
    allowed_domains = ['piaotian.com']
    start_urls = ['http://www.piaotian.com/']
    rex = re.compile(r'^/booksort\d/')

    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.db.DB_table_home.create(self.db.engine, checkfirst=True)
        super(HomeSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        for x in response.css('ul.navlist').css('a'):
            url = x.css('a::attr("href")').extract_first()
            if self.rex.match(url):
                name = x.css('a::text').extract()
                url = 'http://www.piaotian.com%s' % url
                yield {
                    "url": url,
                    "name": name
                }
