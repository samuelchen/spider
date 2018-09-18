#!/usr/bin/env python
from collections import Iterable
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from .novel import ReaderDatabase as Database
from sqlalchemy import (
    Boolean,
    select, text, literal_column,
    and_, or_, true as true_,
    alias, cast, exists, func
)
import logging

__author__ = 'samuel'

db = Database(conn_str=settings.NOVEL_DB_CONNECTION_STRING)

db.DB_table_reader_favorites.create(db.engine, checkfirst=True)
db.DB_table_reader_recommends.create(db.engine, checkfirst=True)
db.DB_table_reader_views.create(db.engine, checkfirst=True)
db.DB_table_reader_searches.create(db.engine, checkfirst=True)

log = logging.getLogger(__name__)


class SubQuery():

    @staticmethod
    def user_favorites(user_id):
        tf = Database.DB_table_reader_favorites
        stmt = select(tf.c).where(tf.c.user_id==user_id)
        stmt = alias(stmt, tf.name)
        return stmt

    @staticmethod
    def user_recommends(user_id):
        tr = Database.DB_table_reader_recommends
        stmt = select(tr.c).where(tr.c.user_id==user_id)
        stmt = alias(stmt, tr.name)
        return stmt

    @staticmethod
    def user_shares(user_id):
        ts = Database.DB_table_reader_shares
        stmt = select(ts.c).where(ts.c.user_id==user_id)
        stmt = alias(stmt, ts.name)
        return stmt

    @staticmethod
    def novel_views():
        tv = Database.DB_table_reader_views
        stmt = select(tv.c)
        stmt = alias(stmt, tv.name)
        return stmt

    @staticmethod
    def novel_searches(user_id):
        ts = Database.DB_table_reader_searches
        stmt = select(ts.c).where(ts.c.user_id==user_id)
        stmt = alias(stmt, ts.name)
        return stmt

    @staticmethod
    def novel_recommends():
        tr = Database.DB_table_reader_recommends
        stmt = select([tr.c.novel_id, func.sum(tr.c.count).label('recmds')]).select_from(tr).group_by(tr.c.novel_id)
        stmt = alias(stmt, 'novel_recommends')
        return stmt

    @staticmethod
    def novels_has_chapters():
        tn = db.DB_table_novel
        stmt = text('''(select tablename from pg_catalog.pg_tables where tablename = %s)''' % tn.c.chapter_table)
        stmt = stmt.columns(literal_column("tablename"))
        return stmt


# ===== Novel List functions =====

# 列出所有小说，默认排序
def list_novels(cols=None, where_clause=None, order_clause=None, page=0, page_items=settings.ITEMS_PER_PAGE,
                add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel

    # default where clause
    wclause = exists(SubQuery.novels_has_chapters())        # All novels which have chapters
    if where_clause is not None:
        wclause = and_(wclause, where_clause)

    # TODO: remove for production
    if settings.DEBUG and settings.ALL_NOVELS:
        wclause = where_clause if where_clause is not None else true_()

    # default order by clause
    oclauses = (tn.c.id.desc(), )
    if order_clause is not None:
        if isinstance(order_clause, Iterable):
            oclauses = order_clause
        else:
            oclauses = (order_clause, )

    columns = [c for c in cols] if cols else [tn.c.id, tn.c.name, tn.c.author, tn.c.category, tn.c.status,
                                              tn.c.desc, tn.c.update_on, tn.c.chapter_table]

    # join clause to query status/statics
    jclause = None
    tf = SubQuery.user_favorites(user_id=with_actions_user_id)
    tr = SubQuery.user_recommends(user_id=with_actions_user_id)
    tv = SubQuery.novel_views()

    # user actions status
    if with_actions_user_id is not None:
        jclause = tn.join(tf, tn.c.id==tf.c.novel_id, isouter=True
                          ).join(tr, tn.c.id==tr.c.novel_id, isouter=True)
        columns.append(cast(tf.c.id, Boolean).label('is_favor'))
        columns.append(tr.c.count.label('my_recmd'))

    # novel statics
    if with_stat is not None:
        if jclause is None:
            jclause = tn
        tnr = SubQuery.novel_recommends()
        jclause = jclause.join(tv, tn.c.id==tv.c.novel_id, isouter=True)
        jclause = jclause.join(tnr, tn.c.id==tnr.c.novel_id, isouter=True)
        columns.extend([tv.c.views, tv.c.views_year, tv.c.views_month])
        columns.extend([tnr.c.recmds])

    # statement
    stmt = select(columns)

    if jclause is not None:
        stmt = stmt.select_from(jclause)

    stmt = stmt.where(wclause
                      ).order_by(*oclauses
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


# 最近更新小说，更新日期排序
def list_update_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False,
                       with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    order_clause = tn.c.update_on.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 最近更新小说（分类），更新日期排序
def list_update_novels_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False,
                                   with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    order_clause = tn.c.update_on.desc()
    return list_novels(where_clause=_get_category_where_clause(category), order_clause=order_clause,
                       page=page, page_items=page_items, add_last_chapter=add_last_chapter,
                       with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 总收藏，收藏数倒序
def list_favorite_novels(page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False,
                         with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    order_clause = tn.c.favorites.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 总收藏（分类），收藏数倒序
def list_favorite_novels_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE,
                                     add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    order_clause = tn.c.favorites.desc()
    return list_novels(where_clause=_get_category_where_clause(category), order_clause=order_clause,
                       page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 总推荐，推荐数倒序
def list_recommend_novels(page=0, page_items=settings.ITEMS_PER_PAGE,
                          add_last_chapter=False, with_actions_user_id=None):
    tn = db.DB_table_novel
    tnr = SubQuery.novel_recommends()
    order_clause = tnr.c.recmds.desc().nullslast(), tn.c.recommends.desc()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items, add_last_chapter=add_last_chapter,
                       with_actions_user_id=with_actions_user_id, with_stat=True)


# 总推荐（分类），推荐数倒序
def list_recommend_novels_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE,
                                      add_last_chapter=False, with_actions_user_id=None):
    tn = db.DB_table_novel
    tnr = SubQuery.novel_recommends()
    order_clause = tnr.c.recmds.desc().nullslast(), tn.c.recommends.desc()
    return list_novels(where_clause=_get_category_where_clause(category), order_clause=order_clause,
                       page=page, page_items=page_items, add_last_chapter=add_last_chapter,
                       with_actions_user_id=with_actions_user_id, with_stat=True)


# 月推荐，推荐数倒序
def list_recommend_novels_month(page=0, page_items=settings.ITEMS_PER_PAGE,
                                add_last_chapter=False, with_actions_user_id=None):
    # TODO: add count_year, count_month to 'reader_recommends'
    tn = db.DB_table_novel
    tnr = SubQuery.novel_recommends()
    order_clause = tn.c.recommends_month.desc(), tnr.c.recmds.desc().nullslast()
    return list_novels(order_clause=order_clause, page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=True)


# 月推荐（分类），推荐数倒序
def list_recommend_novels_month_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE,
                                            add_last_chapter=False, with_actions_user_id=None):
    # TODO: add count_year, count_month to 'reader_recommends'
    tn = db.DB_table_novel
    tnr = SubQuery.novel_recommends()
    order_clause = tn.c.recommends_month.desc(), tnr.c.recmds.desc().nullslast()
    return list_novels(where_clause=_get_category_where_clause(category), order_clause=order_clause,
                       page=page, page_items=page_items, add_last_chapter=add_last_chapter,
                       with_actions_user_id=with_actions_user_id, with_stat=True)


# 总点击，点击数倒序
def list_hot_novels(page=0, page_items=settings.ITEMS_PER_PAGE,
                    add_last_chapter=False, with_actions_user_id=None):
    tv = db.DB_table_reader_views
    order_clause = tv.c.views.desc().nullslast(), tv.c.views_month.desc().nullslast()
    novels = list_novels(order_clause=order_clause, page=page, page_items=page_items,
                         add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id,
                         with_stat=True)
    return novels


# 总点击（分类），点击数倒序
def list_hot_novels_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE,
                                add_last_chapter=False, with_actions_user_id=None):
    tv = db.DB_table_reader_views
    order_clause = tv.c.views.desc().nullslast(), tv.c.views_month.desc().nullslast()
    novels = list_novels(where_clause=_get_category_where_clause(category),
                         order_clause=order_clause, page=page, page_items=page_items,
                         add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id,
                         with_stat=True)
    return novels


# 月点击
def list_hot_novels_month(page=0, page_items=settings.ITEMS_PER_PAGE,
                          add_last_chapter=False, with_actions_user_id=None):
    tv = db.DB_table_reader_views
    order_clause = tv.c.views_month.desc().nullslast(), tv.c.views.desc().nullslast()
    novels = list_novels(order_clause=order_clause, page=page, page_items=page_items,
                         add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id,
                         with_stat=True)
    return novels


# 强推，编辑选择，等等 （站内系统，非爬取）
def list_choice_novels(page=0, page_items=settings.ITEMS_PER_PAGE,
                       add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    # TODO: return real
    return list_recommend_novels(page=page, page_items=page_items,
                                 add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id)


# 完本
def list_finished_novels(page=0, page_items=settings.ITEMS_PER_PAGE,
                         add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    where_clause = and_(tn.c.status=='已完本')
    return list_novels(where_clause=where_clause, page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 完本（分类）
def list_finished_novels_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE,
                                     add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    where_clause = and_(tn.c.status=='已完本', tn.c.category==category)
    return list_novels(where_clause=where_clause, page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 分类
def list_novels_by_category(category, page=0, page_items=settings.ITEMS_PER_PAGE,
                            add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    order_clause = tn.c.update_on.desc()
    return list_novels(where_clause=_get_category_where_clause(category), order_clause=order_clause,
                       page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# 所有已有章节小说
# def list_novels_has_chapters(name_as_key=False):
#     #TODO: change
#     novels = {}
#     for name in db.engine.table_names():
#         if name.endswith('_conflict') or name.startswith('reader_') or name in ['home', 'novel', 'novel_lock']:
#             continue
#         arr = name.split('_')
#         novel_id = int(arr[1])
#         novel_name = arr[2]
#         if name_as_key:
#             novels[novel_name] = novel_id
#         else:
#             novels[novel_id] = novel_name
#     return novels
# novels_has_chapters = list_novels_has_chapters()


def _get_category_where_clause(category):
    tn = db.DB_table_novel
    if category == '全本':
        where_clause = and_(tn.c.status=='已完成')
    else:
        where_clause = and_(tn.c.category==category)

    return where_clause


# ===== Search functions =====


def search_novels(term, qtype=None, page=0, page_items=settings.ITEMS_PER_PAGE,
                  add_last_chapter=False, with_actions_user_id=None, with_stat=False):
    tn = db.DB_table_novel
    if qtype == 'name':
        where_clause = tn.c.name.like('%%%s%%' % term)
    elif qtype == 'author':
        where_clause = tn.c.author.like('%%%s%%' % term)
    else:
        where_clause = or_(tn.c.name.like('%%%s%%' % term), tn.c.author.like('%%%s%%' % term))

    return list_novels(where_clause=where_clause, page=page, page_items=page_items,
                       add_last_chapter=add_last_chapter, with_actions_user_id=with_actions_user_id, with_stat=with_stat)


# ===== Novel functions =====


def get_novel_info(nid, add_last_chapter=False, with_actions_user_id=None, with_stat=False):

    tn = db.DB_table_novel
    wclause = (tn.c.id==nid)
    novels = list_novels(cols=tn.c, page_items=1, where_clause=wclause, add_last_chapter=add_last_chapter,
                         with_actions_user_id=with_actions_user_id, with_stat=with_stat)
    if len(novels) <= 0:
        info = {}
    else:
        info = novels[0]

    return info


# ===== Chapter functions =====


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
                stmt = select(t.c).where(and_(t.c.id>cid, t.c.is_section==False)).order_by(t.c.id).limit(1)
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


def get_all_chapters(nid, with_content=False):
    tn = db.DB_table_novel
    stmt = select([tn.c.chapter_table]).where(tn.c.id==nid)
    # chapters = []

    rs = []
    try:
        # since there is pool, use engine.execute directly
        table = db.engine.execute(stmt).scalar()
        if db.exist_table(table):
            t = db.get_chapter_table(table)
            cols = [t.c.id, t.c.name, t.c.is_section, t.c.url]
            if with_content:
                cols.append(t.c.content)
            stmt = select(cols).order_by(t.c.id)
            rs = db.engine.execute(stmt)
    except Exception as err:
        log.exception(err)

    return rs


# ===== Chapter functions =====
# TODO: add call frequent limit

def list_user_favorites(user_id, page=0, page_items=settings.ITEMS_PER_PAGE, add_last_chapter=False):
    if user_id is None:
        return []

    tf = db.DB_table_reader_favorites
    tn = db.DB_table_novel
    conn = db.create_connection()

    columns = [tn.c.id, tn.c.name, tn.c.author, tn.c.category, tn.c.status,
               tn.c.desc, tn.c.update_on, tn.c.chapter_table, cast(tf.c.id, Boolean).label('is_favor')]
    stmt = select(columns
                  ).where(and_(tn.c.id==tf.c.novel_id, tf.c.user_id==user_id)
                  ).order_by(tf.c.id.desc()
                  ).limit(page_items
                  ).offset(page * page_items)

    novels = []
    try:
        rs = conn.execute(stmt)
        for r in rs:
            novel = dict(r)
            if add_last_chapter:
                last_chapter_id, last_chapter = get_last_chapter(chapter_table=r[tn.c.chapter_table], conn=conn)
                novel["last_chapter"] = last_chapter
                novel['last_chapter_id'] = last_chapter_id
            novels.append(novel)
    except Exception as err:
        log.exception(err)

    return novels


def switch_novel_favorite(nid, user_id):
    t = db.DB_table_reader_favorites
    stmt = select([t.c.id]).where(and_(t.c.user_id==user_id, t.c.novel_id==nid))

    rc = True
    try:
        fid = db.engine.execute(stmt).scalar()
        if fid is not None:
            stmt = t.delete().where(t.c.id==fid)
            rc = False
        else:
            stmt = t.insert().values(user_id=user_id, novel_id=nid, timestamp=timezone.now())
            rc = True
        db.engine.execute(stmt)
    except Exception as err:
        log.exception(err)

    return rc


def recommend_novel(nid, uid):
    t = db.DB_table_reader_recommends
    stmt = select([t.c.id]).where(and_(t.c.user_id==uid, t.c.novel_id==nid))

    rc = 0
    try:
        rid = db.engine.execute(stmt).scalar()
        if rid is not None:
            stmt = t.update().where(t.c.id==rid).values(count=t.c.count+1).returning(t.c.count)
        else:
            stmt = t.insert().values(user_id=uid, novel_id=nid, count=1, timestamp=timezone.now()).returning(t.c.count)
        rc = db.engine.execute(stmt).scalar()
    except Exception as err:
        log.exception(err)

    return rc


def add_search_stat(qterm, qtype, nid=None, uid=None):
    t = db.DB_table_reader_searches
    stmt = t.insert().values(term=qterm, type=qtype, novel_id=nid, user_id=uid, timestamp=timezone.now()).returning(t.c.id)
    sid = None
    try:
        sid = db.engine.execute(stmt).scalar()
    except Exception as err:
        log.exception(err)

    return sid


def update_search_hit(sid, nid):
    t = db.DB_table_reader_searches
    stmt = t.update().values(novel_id=nid).where(t.c.id==sid)
    rc = False
    try:
        db.engine.execute(stmt)
        rc = True
    except Exception as err:
        log.exception(err)

    return rc


def add_novel_view_count(novel_id):
    t = db.DB_table_reader_views
    stmt = select(t.c).where(t.c.novel_id==novel_id)

    now = timezone.now()
    rc = None
    try:
        rs = db.engine.execute(stmt)
        if rs.rowcount > 0:
            r = rs.fetchone()
            v = dict(r)
            rs.close()
            rc = r[t.c.id]

            # if duration is less than 10s from last update, ignore it.
            duration = now - r[t.c.timestamp]
            if duration.total_seconds() < 10:
                return rc

            # TODO: batch update view(total) view_year and reset view_month

            # update count
            stmt = t.update().values(views_month=t.c.views_month+1).where(t.c.novel_id==novel_id)
            db.engine.execute(stmt)
        else:
            stmt = t.insert().values(novel_id=novel_id, views_month=1, timestamp=timezone.now()).returning(t.c.id)
            rc = db.engine.execute(stmt).scalar()
    except Exception as err:
        log.exception(err)

    return rc