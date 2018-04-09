#!/usr/bin/sh env

from novelspider.db import Database, select, or_
from settings import DB_CONNECTION_STRING
import sys
import re

__author__ = 'samuel'

# change these
# novel_ids = [29, 6011, 6232, 6445, 8320, 8335, 8463, 8627]
# novel_ids = [6232, ]

keywords_to_clean = ['飘天文学', '飘天', '起点', '17k', '纵横']
keywords_to_clean.extend(['piaotian.com', 'qidian.com', '17k.com', 'zongheng.com'])
my_domain = '${DOMAIN}'
my_site_name = '${SITENAME}'

# vars
regx_keywords = [r'%s' % k.replace('.', r'\.') for k in keywords_to_clean]
print('keywords to be replaced:', regx_keywords)
regx_keywords = [re.compile(k, re.IGNORECASE | re.MULTILINE) for k in regx_keywords]
sql_keys = ['%%%s%%' % k for k in keywords_to_clean]

db = Database(conn_str=DB_CONNECTION_STRING)


def clean_all(novel_ids=None):

    conn = db.create_connection()

    # obtain chapter tables
    if novel_ids:
        print('novel_ids defined. Clean specified novel ids', novel_ids)
        tn = db.DB_table_novel
        stmt = select([tn.c.id, tn.c.name, tn.c.chapter_table]).where(tn.c.id.in_(novel_ids))
        rs = conn.execute(stmt)
    else:
        print('novel_ids not defined. Clean all novels.')
        # all tables
        tn = db.DB_table_novel
        stmt = 'select tablename from pg_catalog.pg_tables'
        rs = conn.execute(stmt)


    counts = {}
    # loop novels
    for r in rs:
        novel_cnt_keywords = [0] * len(keywords_to_clean)

        if novel_ids:
            table = r[tn.c.chapter_table]
        else:
            table = r['tablename']
            if table.startswith('novel_') and not table.endswith('_conflict') \
                    and table not in ['home', 'novel', 'novel_lock', 'novel_statics', 'novel_featured']:
                print('cleaning %s ...' % table)
            else:
                # print(' > skip %s' % table)
                continue

        t = db.get_chapter_table(table)
        stmt = select([t.c.id, t.c.name, t.c.content]).where(or_(t.c.content.like(k) for k in sql_keys))
        rs1 = conn.execute(stmt)

        # loop found chapter contents
        for r1 in rs1:
            print(' > ', r1[t.c.id], r1[t.c.name])
            cnt_keywords = clean(r1[t.c.content])
            for i in range(0, len(keywords_to_clean)):
                novel_cnt_keywords[i] += cnt_keywords[i]

        counts[table] = novel_cnt_keywords

    conn.close()

    for table, cnt_keywords in counts.items():
        total = sum(cnt_keywords)
        print('counts for %s' % table, total)
        if total > 0:
            for i in range(0, len(keywords_to_clean)):
                if cnt_keywords[i] > 0:
                    print(' - ', keywords_to_clean[i], ":", cnt_keywords[i])


def clean(content):

    cnts = []

    for regx in regx_keywords:
        matches = regx.findall(content)
        cnt = len(matches)
        cnts.append(cnt)
        if cnt > 0:
            print('    - "%s" found:%d' % (regx.pattern, cnt))
        # for m in matches:
        #     print('        # ', m)

    return cnts

if __name__ == '__main__':

    if len(sys.argv) > 1:
        clean_all(sys.argv[1:])
    else:
        clean_all()