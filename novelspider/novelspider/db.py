#!/usr/bin/env python
# coding:utf-8

__author__ = 'samuel'
__date__ = '18/3/2'

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Boolean, Text, DateTime, BLOB
from sqlalchemy import MetaData, ForeignKey, Sequence
from sqlalchemy.sql import select, update
from sqlalchemy.sql.expression import not_, and_, or_, true as true_
from sqlalchemy.exc import IntegrityError
import datetime
import logging

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
log = logging.getLogger('db')


def mark_done(engine_or_conn, table, col_pk, pks, col_returns=[]):
    stmt = table.update().where(and_(col_pk.in_(pks), table.c.done==False)).values(done=True)
    if col_returns:
        stmt = stmt.returning(col_returns)
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
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.datetime.utcnow),       # last modified datetime of record
        schema=schema
    )


# create a conflict table corresponding to chapter table
# conflict table name should be novel_id_name_conflict (chapter_table + "_conflict")
def create_db_table_chapter_conflicts(name, meta, schema=None):
    return Table(name, meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(100), nullable=False),
        Column('is_section', Boolean, default=False),
        Column('url', Text),
        Column('content', Text),
        Column('conflict_chapter_id', Integer),
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.datetime.utcnow),       # last modified datetime of record
        schema=schema
    )


class Database(object):

    IntegrityError = IntegrityError
    meta = MetaData()
    schema = None

    DB_table_home = Table('home', meta,
        Column('url', Text, primary_key=True, index=True, unique=True),
        Column('update_on', DateTime(timezone=True)),
        # Column('done', Boolean, default=False)
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
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.datetime.utcnow),

        schema=schema
    )

    DB_table_novel_lock = Table('novel_lock', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('novel_id', Integer, unique=True, index=True),
        Column('name', String(100)),
        Column('locker', String(100), index=True),
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.datetime.utcnow),

        schema=schema
    )

    def __init__(self, conn_str='', schema=None):
        self.schema = schema
        self.__engine = None
        self.__conn_str = conn_str

    @staticmethod
    def __internal_settings():
        from scrapy.utils.project import get_project_settings
        return get_project_settings()

    @property
    def conn_str(self):
        if not self.__conn_str:
            settings = Database.__internal_settings()
            self.__conn_str = settings['DB_CONNECTION_STRING']
        return self.__conn_str

    @conn_str.setter
    def conn_str(self, value):
        self.__conn_str = value

    @property
    def engine(self):
        if not self.__engine:
            conn_str = self.conn_str
            if conn_str.startswith('sqlite'):
                self.__engine = create_engine(conn_str)
            else:
                self.__engine = create_engine(conn_str, pool_size=20, max_overflow=1)
        return self.__engine

    @property
    def status(self):
        return self.engine.url

    @staticmethod
    def get_chapter_table(name):
        table = Database.meta.tables.get(name, None)
        if table is None:
            table = create_db_table_chapter(name, meta=Database.meta, schema=Database.schema)
        return table

    @staticmethod
    def get_chapter_conflict_table(name):
        # arg "name" is chapter table name.
        # conflict table will be name + "_conflict"
        tname = name + '_conflict'
        table = Database.meta.tables.get(tname, None)
        if table is None:
            table = create_db_table_chapter_conflicts(tname, meta=Database.meta, schema=Database.schema)
        return table

    def exist_table(self, name):
        # return name in Database.meta.tables
        sql = '''select tablename from pg_catalog.pg_tables where tablename='%s';''' % name
        tname = self.engine.execute(sql).scalar()
        return tname == name

    def create_connection(self, **kwargs):
        conn = self.engine.connect(**kwargs)
        return conn

    def init(self):
        log.info('Initialize database.')
        self.DB_table_home.create(self.engine, checkfirst=True)
        self.DB_table_novel.create(self.engine, checkfirst=True)

    # def drop_all(self):
    #     log.warn('Your are DELETING ALL your database content!!!')
    #     # list all table names of novels
    #     stmt = select([self.DB_table_novel.c.chapter_table]).where(not_(self.DB_table_novel.c.chapter_table==None))
    #     result = self.engine.execute(stmt)
    #     for row in result:
    #         table = row['chapter_table']
    #         t = create_db_table_chapter(table, self.meta, self.schema)
    #         t.drop(self.engine, checkfirst=True)
    #
    #     self.DB_table_home.drop(self.engine, checkfirst=True)
    #     self.DB_table_novel.drop(self.engine, checkfirst=True)

    def lock_novel(self, novel_id, locker, name=None, conn=None):
        rc = 0      # succeed (unlocked novel is locked)
        tl = self.DB_table_novel_lock
        stmt = tl.insert().values(novel_id=novel_id, name=name, locker=locker, timestamp=datetime.datetime.utcnow())
        if not conn:
            conn = self.engine
        try:
            conn.execute(stmt)
            log.info('Locked novel %s(id=%s).' % (name or '', novel_id))
        except IntegrityError as err:
            try:
                stmt = select([tl.c.locker]).where(novel_id==novel_id)
                lckr = conn.execute(stmt).scalar()
                if lckr == locker:
                    rc = 1      # novel was locked by self
                    log.info('Novel %s(id=%s) is locked by self' % (name or '', novel_id))
                else:
                    rc = -1     # novel was locked by other
                    log.info('Novel %s(id=%s) was locked by other.' % (name or '', novel_id))
            except Exception as err:
                log.error('Fail to lock novel %s(id=%s). %s.' % (name or '', novel_id, str(err)))

        return rc

    def unlock_novel(self, novel_id, conn=None):
        tl = self.DB_table_novel_lock
        stmt = tl.delete().where(novel_id==novel_id)
        count = 0
        try:
            if conn:
                rs = conn.execute(stmt)
            else:
                rs = self.engine.execute(stmt)
            count = rs.rowcount
        except Exception as err:
            log.exception(err)

        if count == 0:
            log.warn('Novel (id=%s) was not locked to unlock.' % novel_id)
        elif count > 1:
            log.warn('Unlocked more than 1 novels which has id=%s' % novel_id)
        else:
            log.info('Unlocked novel (id=%s).' % novel_id)

        return count


if __name__ == '__main__':
    db = Database()
    # db.drop_all()
    db.init()
