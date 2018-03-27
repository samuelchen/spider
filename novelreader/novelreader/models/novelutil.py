#!/usr/bin/env python

from django.conf import settings
import os, sys
from django.http import Http404

sys.path.append(os.path.join(settings.BASE_DIR, '..', 'novelspider'))
from novelspider.db import Database, select, and_, or_, true_
import logging

__author__ = 'samuel'

db = Database(conn_str=settings.NOVEL_DB_CONNECTION_STRING)
log = logging.getLogger(__name__)


# 列出所有小说，默认排序
def list_novels(where_clause=None, order_clause=None,
                page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    tn = db.DB_table_novel

    # default where clause
    wclause = tn.c.id.in_(novels_has_chapters)
    if where_clause is not None:
        wclause = and_(wclause, where_clause)
    # wclause = true_()

    # default order by clause
    oclause = tn.c.id.desc()
    if order_clause is not None:
        oclause = order_clause
    oclause = None

    stmt = select([tn.c.id, tn.c.name, tn.c.author, tn.c.category, tn.c.status, tn.c.desc,
                   tn.c.update_on, tn.c.chapter_table]
                  ).where(wclause
                  ).order_by(oclause
                  ).limit(page_items
                  ).offset(page * page_items)
    # print(stmt)
    novels = []
    rs = None
    conn = None
    try:
        conn = db.create_connection()
        rs = conn.execute(stmt)

        for r in rs:
            novel = dict(r)
            if add_last_chapter:
                last_chapter_id, last_chapter = get_last_chapter(chapter_table=r[tn.c.chapter_table], conn=conn)
                novel["last_chapter"] = last_chapter
                novel['last_chapter_id'] = last_chapter_id
            novels.append(novel)
    except Exception:
        log.exception('Fail to list novels.')
    finally:
        if rs is not None: rs.close()
        if conn is not None: conn.close()

    return novels


# 最近更新小说，默认排序
def list_update_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    tn = db.DB_table_novel
    order_clause = tn.c.update_on.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 总收藏，收藏数倒序
def list_favorite_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    tn = db.DB_table_novel
    order_clause = tn.c.favorites.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 总推荐，推荐数倒序
def list_recommend_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    tn = db.DB_table_novel
    order_clause = tn.c.recommends.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 总点击，点击数倒序
def list_hot_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    # TODO: return real
    return list_favorite_novels(page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 月点击
def list_hot_novels_cur_month(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    pass


# 周点击
def list_hot_novels_cur_week(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    tn = db.DB_table_novel
    order_clause = tn.c.recommends.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 强推，编辑选择，等等 （站内系统，非爬取）
def list_choice_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    # TODO: return real
    return list_recommend_novels(page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 完本
def list_finished_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    tn = db.DB_table_novel
    where_clause = and_(tn.c.status=='已完本')
    return list_novels(where_clause=where_clause, page=page, page_items=page_items, add_last_chapter=add_last_chapter)


# 所有已有章节小说
def list_novels_has_chapters(name_as_key=False):
    novels = {}
    for name in db.engine.table_names():
        if name.endswith('_conflict') or name in ['home', 'novel', 'novel_lock']:
            continue
        arr = name.split('_')
        novel_id = int(arr[1])
        novel_name = arr[2]
        if name_as_key:
            novels[novel_name] = novel_id
        else:
            novels[novel_id] = novel_name
    return novels
novels_has_chapters = list_novels_has_chapters()


def get_novel_info(nid, add_last_chapter=False):
    info = {}
    tn = db.DB_table_novel
    stmt = select(tn.c).where(tn.c.id==nid)

    try:
        # since there is pool. use engine.execute directly
        rs = db.engine.execute(stmt)
        if rs.rowcount <= 0:
            raise Http404('Novel (id=%s) is not found' % nid)
        r = rs.fetchone()
        info = dict(r)
        rs.close()

        if add_last_chapter:
            last_chapter_id, last_chapter = get_last_chapter(chapter_table=r[tn.c.chapter_table])
            info['last_chapter'] = last_chapter
            info['last_chapter_id'] = last_chapter_id
    except Http404:
        raise
    except Exception as err:
        log.exception(err)

    return info


def get_chapter(cid, nid=None, chapter_table=None, conn=None, with_prev=False, with_next=False):

    if nid is None and not chapter_table:
        raise ValueError('Must specify either novel id or chapter table name.')

    tn = db.DB_table_novel
    chapter = {}

    if conn is None:
        conn = db.engine

    try:
        if not chapter_table:
            stmt = select([tn.c.chapter_table]).where(tn.c.id==nid)
            chapter_table = conn.execute(stmt).scalar()

        if db.exist_table(chapter_table):
            t = db.get_chapter_table(chapter_table)
            stmt = select(t.c).where(and_(t.c.id==cid, t.c.is_section==False)).order_by(t.c.id.desc()).limit(1)
            rs = conn.execute(stmt)
            r = rs.fetchone()
            if r is None:
                raise Http404('Chapter %s of novel %s not found.' % (cid, nid))
            chapter = dict(r)
            rs.close()

            if with_next:
                stmt = select(t.c).where(and_(t.c.id>cid, t.c.is_section==False)).order_by(t.c.id.desc()).limit(1)
                rs = conn.execute(stmt)
                r = rs.fetchone()
                chapter['next'] = dict(r) if r else None
                rs.close()

            if with_prev:
                stmt = select(t.c).where(and_(t.c.id<cid, t.c.is_section==False)).order_by(t.c.id.desc()).limit(1)
                rs = conn.execute(stmt)
                r = rs.fetchone()
                chapter['prev'] = dict(r) if r else None
                rs.close()

    except Http404:
        raise
    except Exception as err:
        log.exception(err)

    return chapter


def get_last_chapter(nid=None, chapter_table=None, conn=None):

    if nid is None and not chapter_table:
        raise ValueError('Must specify either novel id or chapter table name.')

    tn = db.DB_table_novel
    last_chapter_id = -1
    last_chapter = ''

    if conn is None:
        conn = db.engine

    try:
        if not chapter_table:
            stmt = select([tn.c.chapter_table]).where(tn.c.id==nid)
            chapter_table = conn.execute(stmt).scalar()

        if db.exist_table(chapter_table):
            t = db.get_chapter_table(chapter_table)
            stmt = select([t.c.id, t.c.name]).where(t.c.is_section==False).order_by(t.c.id.desc()).limit(1)
            rs = conn.execute(stmt)
            r = rs.fetchone()
            if r is not None:
                last_chapter_id = r[t.c.id]
                last_chapter = r[t.c.name]
    except Exception as err:
        log.exception(err)

    return last_chapter_id, last_chapter


def get_latest_chapters(nid, count=12):
    tn = db.DB_table_novel
    stmt = select([tn.c.chapter_table]).where(tn.c.id==nid)
    chapters = []
    try:
        # since there is pool, use engine.execute directly
        table = db.engine.execute(stmt).scalar()
        if db.exist_table(table):
            t = db.get_chapter_table(table)
            stmt = select([t.c.id, t.c.name, t.c.is_section, t.c.url]
                          ).where(t.c.is_section==False
                          ).order_by(t.c.id.desc()
                          ).limit(count)

            rs = db.engine.execute(stmt)
            for r in rs:
                chapters.append(r)
            rs.close()
    except Exception as err:
        log.exception(err)

    return chapters


def get_all_chapters(nid):
    tn = db.DB_table_novel
    stmt = select([tn.c.chapter_table]).where(tn.c.id==nid)
    # chapters = []
    rs = []
    try:
        # since there is pool, use engine.execute directly
        table = db.engine.execute(stmt).scalar()
        if db.exist_table(table):
            t = db.get_chapter_table(table)
            stmt = select([t.c.id, t.c.name, t.c.is_section, t.c.url]
                          ).order_by(t.c.id)
            rs = db.engine.execute(stmt)
    except Exception as err:
        log.exception(err)

    return rs