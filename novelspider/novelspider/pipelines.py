# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from .db import Database, String, mark_done, select
from sqlalchemy.sql import cast
import logging

log = logging.getLogger(__name__)


class NovelspiderDBPipeline(object):

    counters = {}

    def __init__(self):
        self.db = Database()
        self.conn = None

    def open_spider(self, spider):
        self.conn = self.db.create_connection()
        log.info('Database connected (%s).' % self.db.status)

    def close_spider(self, spider):
        self.conn.close()
        log.info('Database disconnected (%s).' % self.db.status)

    def process_item(self, item, spider):
        if spider.name == 'home':
            stmt = self.db.DB_table_home.insert().values(url=item['url'])
            try:
                self.conn.execute(stmt)
            except Database.IntegrityError:
                log.warn('Conflict (home): %(name)s %(url)s' % item)

        elif spider.name == 'novel':
            log.info('<spider:novel>: %(name)s %(url)s' % item)

            t = self.db.DB_table_novel
            stmt = t.insert().values(
                url=item['url'],
                name=item['name'],
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
                timestamp=datetime.datetime.now()
            ).returning(t.c.id)

            try:
                rs = self.conn.execute(stmt)
                r = rs.fetchone()

                stmt2 = t.update().values(
                    chapter_table='novel_' + cast(t.c.id, String) + '_' + item['name'],
                ).where(t.c.id==r[t.c.id])
                self.conn.execute(stmt2)
            except Database.IntegrityError as err:
                s = str(err)
                if s.find('name') > 0:
                    log.error('-----  Novel with same name:  %(name)s %(url)s' % item)
                log.warn('Conflict (home): %(name)s %(url)s' % item)

        elif spider.name == 'chapter':

            novel_id = item['novel_id']

            # get total count of chapters from spider
            total = spider.chapter_counters.get(novel_id)
            # local counter to count save chapters
            if novel_id not in self.counters:
                self.counters[novel_id] = total['saved']     # count number begin from saved count

            log.debug('Chapters counts: total=%s(%s), saved=%s' % (total['count'],
                       'done' if total['done'] else 'counting', self.counters[novel_id]))

            # get db table definition
            table = item['table']
            t = self.db.get_chapter_table(table)

            # insert chapter/section
            is_section = item['url'] is None
            stmt = t.insert().values(id=item['idx'], name=item['name'], url=item['url'], content=item['content'],
                                     timestamp=datetime.datetime.now(), is_section=is_section, done=True)
            try:
                self.conn.execute(stmt)
                log.info('Saved %(name)s(id=%(idx)s, url=%(url)s)' % item)
            except Database.IntegrityError:
                log.warn('Conflict (%(table)s): %(name)s %(url)s' % item)

                # add conflict chapter to conflict table
                stmt = select([t.c.id]).where(t.c.name==item['name'])
                cid = self.conn.execute(stmt).scalar()
                if cid:
                    tc = self.db.get_chapter_conflict_table(table)
                    stmt = tc.insert().values(id=item['idx'], name=item['name'], url=item['url'],
                                              content=item['content'], conflict_chapter_id=cid,
                                              timestamp=datetime.datetime.now(), is_section=is_section)
                    self.conn.execute(stmt)

            self.counters[novel_id] += 1

            if total['done'] and self.counters[novel_id] >= total['count']:
                # TODO: possible finished but chapters counting not done ?
                # mark this novel done
                tn = self.db.DB_table_novel
                mark_done(self.db.engine, tn, tn.c.id, [novel_id, ])

        else:
            log.error('Unknown spider <%s>' % spider.name)
        return item


class NovelspiderAlbumPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if info.spider.name == 'novel':
            for url in item[self.images_urls_field]:
                yield scrapy.Request(url, meta={'item': item})

    # def item_completed(self, results, item, info):
    #     image_paths = [x['path'] for ok, x in results if ok]
    #     if not image_paths:
    #         raise DropItem("Item contains no images")
    #     return item

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        name = item['name']
        filename = '%s.jpg' % name
        return filename