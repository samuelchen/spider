#!/usr/bin/sh env

from novelspider.db import Database, select, or_
import re

__author__ = 'samuel'

# change these
# novel_ids = [29, 6011, 6232, 6445, 8320, 8335, 8463, 8627]
novel_ids = [13, ]
domains_to_clean = ['www.piaotian.com', 'piaotian.com']
names_to_clean = ['飘天文学', '飘天']
my_domain = '${DOMAIN}'
my_site_name = '${SITENAME}'

# vars
regx_domains = [r'%s' % k.replace('.', r'\.') for k in domains_to_clean]
regx_names = [r'%s' % k.replace('.', r'\.') for k in names_to_clean]
print(regx_domains)
print(regx_names)
regx_domains = [re.compile(k, re.IGNORECASE | re.MULTILINE) for k in regx_domains]
regx_names = [re.compile(k, re.IGNORECASE | re.MULTILINE) for k in regx_names]

sql_keys = ['%%%s%%' % k for k in domains_to_clean]
sql_keys.extend(['%%%s%%' % k for k in names_to_clean])

db = Database()

def clean():

    conn = db.create_connection()

    # obtain chapter tables
    tn = db.DB_table_novel
    stmt = select([tn.c.id, tn.c.name, tn.c.chapter_table]).where(tn.c.id.in_(novel_ids))
    rs = conn.execute(stmt)

    # loop novels
    for r in rs:
        table = r[tn.c.chapter_table]
        t = db.get_chapter_table(table)
        stmt = select([t.c.id, t.c.name, t.c.content]).where(or_(t.c.content.like(k) for k in sql_keys))
        rs1 = conn.execute(stmt)
        # loop found chapter contents
        for r1 in rs1:
            print(r1[t.c.id], r1[t.c.name])
            for regx in regx_domains:
                matches = regx.findall(r1[t.c.content])
                print('  * "%s" found:%d' % (regx.pattern, len(matches)))
                for m in matches:
                    print('    -', m)
            for regx in regx_names:
                matches = regx.findall(r1[t.c.content])
                print('  * "%s" found:%d' % (regx.pattern, len(matches)))
                for m in matches:
                    print('    -', m)
    conn.close()

if __name__ == '__main__':
    clean()