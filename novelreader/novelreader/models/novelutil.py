#!/usr/bin/env python

from django.conf import settings
import os, sys
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
    print(stmt)
    novels = []
    try:
        conn = db.create_connection()
        rs = conn.execute(stmt)

        for r in rs:
            if add_last_chapter and db.exist_table(r[tn.c.chapter_table]):
                t = db.get_chapter_table(r[tn.c.chapter_table])
                stmt = select([t.c.name]).order_by(t.c.id.desc()).limit(1)
                last_chapter = conn.execute(stmt).scalar()
            else:
                last_chapter = ''
            novel = {item[0]: item[1] for item in r.items()}
            novel["last_chapter"] = last_chapter
            novels.append(novel)
    except:
        log.exception('Fail to list novels.')
    finally:
        conn.close()

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
    return list_recommend_novels(page=page, page_items=page_items, add_last_chapter=add_last_chapter)


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
