# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .db import Database, String, and_
from sqlalchemy.sql import cast
import logging

log = logging.getLogger(__name__)


class NovelspiderDBPipeline(object):

    def __init__(self):
        self.db = Database()

    def open_spider(self, spider):
        self.conn = self.db.create_connection()
        log.debug('Database connected (%s).' % self.db.status)

    def close_spider(self, spider):
        self.conn.close()
        log.debug('Database disconnected.')

    def process_item(self, item, spider):
        log.debug('processing <spider:%s> %s' % (spider.name, item))
        if spider.name == 'home':
            stmt = self.db.DB_table_home.insert().values(url=item['url'])
            try:
                self.conn.execute(stmt)
            except Database.IntegrityError:
                log.warn('Conflict (home): %s' % item)

        elif spider.name == 'novel':
            t = self.db.DB_table_novel
            if len(item) < 3:
                stmt = self.db.DB_table_novel.insert().values(url=item['url'], name=item['name'])
            else:
                stmt = t.update().values(
                    author=item['author'],
                    category=item['category'],
                    length=item['length'],
                    status=item['status'],
                    desc=item['desc'],
                    favorites=item['favorites'],
                    recommends=item['recommends'],
                    recommends_month=item['recommends_month'],
                    update_on=item['update_on'],
                    url_index=item['url_index'],
                    chapter_table='novel_' + cast(t.c.id, String) + '_' + item['name'],
                ).where(and_(t.c.url==item['url'], t.c.name==item['name']))
            try:
                self.conn.execute(stmt)
            except Database.IntegrityError:
                log.warn('Conflict (novel): %s' % item)

        elif spider.name == 'chapter':
            table = item['table']
            t = self.db.get_chapter_table(table)
            t.create(self.db.engine, checkfirst=True)   # TODO: move outside

            is_section = item['url'] is None
            stmt = t.insert().values(name=item['name'], url=item['url'], content=item['content'],
                                     is_section=is_section, done=True)
            try:
                self.conn.execute(stmt)
            except Database.IntegrityError:
                log.warn('Conflict (%s): %s' % (table, item))
        elif spider.name == 'content':
            table = item['table']
            t = self.db.get_chapter_table(table)
            t.create(self.db.engine, checkfirst=True) # TODO: move outside

            id = item['id']
            content = item['content']
            stmt = t.update().values(content=content, done=True).where(id==id)

            try:
                self.conn.execute(stmt)
            except Database.IntegrityError:
                log.warn('Conflict (content): %s - %s' % (table, id))
        return item
