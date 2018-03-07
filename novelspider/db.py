#!/usr/bin/env python
# coding:utf-8

__author__ = 'samuel'
__date__ = '18/3/2'

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Boolean, Text, DateTime, BLOB
from sqlalchemy import MetaData, ForeignKey, Sequence
from sqlalchemy.sql import select, update
from sqlalchemy.sql.expression import not_, and_
from sqlalchemy.exc import IntegrityError
from scrapy.utils.project import get_project_settings
import datetime
import logging

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
log = logging.getLogger('db')

settings = get_project_settings()
DB_CONNECTION_STRING = settings['DB_CONNECTION_STRING']


def get_all_undone(engine_or_conn, DB_columns):
    stmt = select(DB_columns).where(done==False)
    records = engine_or_conn.execute(stmt)
    return records


def mark_done(engine_or_conn, table, col_pk, pks):
    stmt = table.update().where(and_(col_pk.in_(pks), table.c.done==False)).values(done=True)
    return engine_or_conn.execute(stmt)


# create a table to store all chapters for a novel
# name is table name (may be novel name, name hash or etc.)
def create_db_table_chapter(name, meta, schema=None):
    return Table(name, meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(100), unique=True, nullable=False),
        Column('is_section', Boolean, default=False),
        Column('url', Text, unique=True),
        Column('content', Text),
        Column('done', Boolean, default=False),
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.datetime.now),       # last modified datetime of record
        schema=schema
    )


class Database(object):

    IntegrityError = IntegrityError
    meta = MetaData()
    schema = None

    DB_table_home = Table('home', meta,
        Column('url', Text, primary_key=True, index=True, unique=True),
        Column('done', Boolean, default=False)
    )

    DB_table_novel = Table('novel', meta,
        Column('id', Integer, primary_key=True, index=True, autoincrement=True),
        Column('name', String(100), unique=True, index=True),           # novel name
        Column('url', Text, unique=True, index=True),                   # novel home url
        Column('done', Boolean, default=False, index=True),             # whether downloaded.

        Column('author', String(50), index=True),                       # novel author name
        Column('category', String(50), index=True),                     # novel type
        Column('length', Integer),                                      # novel length in words
        Column('status', String(50), index=True),                       # completed or to be continued
        Column('desc', Text),
        Column('license', String(50)),                                  # which site has the license
        Column('favorites', Integer, default=0),                        # favorite count
        Column('recommends', Integer, default=0),                       # recommendation count
        Column('recommends_month', Integer, default=0),                 # recommendation count of this month
        Column('update_on', DateTime(timezone=True)),                   # last updated datetime by the author
        Column('url_index', Text),                                      # url of index page

        Column('chapter_table', String(100), unique=True),              # chapter table name in DB for this novel
        # last modified datetime of record
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.datetime.now),

        schema=schema
    )

    DB_table_chapter_failure = Table('chapter_failure', meta,
        Column('id', Integer, primary_key=True),
        Column('novel_id', Integer, index=True),
        Column('novel_name', String(100)),
        Column('chapter_table', String(100)),
        Column('chapter_id', Integer, index=True),
        Column('error', Text),
        Column('created_on', DateTime(timezone=True)),
        Column('retry_count', Integer),
        Column('timestamp', DateTime(timezone=True)),

        schema=schema
    )


    def __init__(self, schema=None):
        self.schema = schema
        self.engine = Database.create_engine()

    @staticmethod
    def create_engine():
        if DB_CONNECTION_STRING.startswith('sqlite'):
            return create_engine(DB_CONNECTION_STRING)
        else:
            return create_engine(DB_CONNECTION_STRING, pool_size=20, max_overflow=1)

    @property
    def status(self):
        return self.engine.url

    def get_chapter_table(self, name):
        table = Database.meta.tables.get(name, None)
        if table is None:
            table = create_db_table_chapter(name, meta=self.meta, schema=self.schema)
        return table

    def create_connection(self, *args, **kwargs):
        conn = self.engine.connect()
        return conn

    def init(self):
        log.info('Initialize database.')
        self.DB_table_home.create(self.engine, checkfirst=True)
        self.DB_table_novel.create(self.engine, checkfirst=True)

    def drop_all(self):
        log.warn('Your are DELETING ALL your database content!!!')
        # list all table names of novels
        stmt = select([self.DB_table_novel.c.chapter_table]).where(not_(self.DB_table_novel.c.chapter_table==None))
        result = self.engine.execute(stmt)
        for row in result:
            table = row['chapter_table']
            t = create_db_table_chapter(table, self.meta, self.schema)
            t.drop(self.engine, checkfirst=True)

        self.DB_table_home.drop(self.engine, checkfirst=True)
        self.DB_table_novel.drop(self.engine, checkfirst=True)


if __name__ == '__main__':
    db = Database()
    db.drop_all()
    db.init()