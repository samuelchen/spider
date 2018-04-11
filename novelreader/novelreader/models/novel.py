from __future__ import unicode_literals

from novelspider.db import Database
from sqlalchemy import (
    Table,
    Column, ForeignKey, UniqueConstraint,
    Integer, String, Boolean, DateTime,
    select,
    and_, or_, true as true_,
)
import logging
from datetime import datetime

__author__ = 'samuel'
log = logging.getLogger(__name__)


class ReaderDatabase(Database):

    # ----- actions states by user ------

    DB_table_reader_favorites = Table('reader_favorites', Database.meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, nullable=False, index=True),
        Column('novel_id', Integer, nullable=False, index=True),

        UniqueConstraint('user_id', 'novel_id'),
        schema=Database.schema
    )

    DB_table_reader_recommends = Table('reader_recommends', Database.meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', Integer, nullable=False, index=True),
        Column('novel_id', Integer, nullable=False, index=True),
        Column('count', Integer, default=0),
        UniqueConstraint('user_id', 'novel_id'),
        schema=Database.schema
    )

    # DB_table_reader_shares = Table('reader_shares', Database.meta,
    #     Column('id', Integer, primary_key=True, autoincrement=True),
    #     Column('user_id', Integer, nullable=False, index=True),
    #     Column('novel_id', Integer, nullable=False, index=True),
    #     Column('target', String(50), nullable=False),
    #     Column('count', Integer, default=0),
    #     UniqueConstraint('user_id', 'novel_id', 'target'),
    #     schema=Database.schema
    # )


    DB_table_reader_views = Table('reader_views', Database.meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('novel_id', Integer, nullable=False, unique=True, index=True),
        Column('views', Integer, default=0),
        Column('views_year', Integer, default=0),
        Column('views_month', Integer, default=0),
        schema=Database.schema
    )

    DB_table_reader_searches = Table('reader_searches', Database.meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('term', String(100), nullable=False, index=True),
        Column('type', String(50), nullable=False),
        Column('novel_id', Integer, index=True),   # finally user selected
        Column('user_id', Integer),
        Column('timestamp', DateTime(timezone=True), onupdate=datetime.utcnow),
        schema=Database.schema
    )

