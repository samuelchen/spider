#!/usr/bin/python
# -*- coding=utf-8 -*-

__author__ = 'samuel'

import os
import sys
from flask import Flask, request, render_template_string, make_response, url_for
from jinja2 import Template
from novelspider.db import Database, select, and_, not_
from novelspider.settings import IMAGES_STORE
import logging

log = logging.getLogger(__name__)
# logging.basicConfig({'level': logging.DEBUG})
app = Flask(__name__, static_folder=IMAGES_STORE, static_url_path='/s')
db = Database()

template_page = '''
<html>
<head>
<meta charset="{{ encoding }}" />
<meta http-equiv="content-type" content="text/html; charset={{ encoding }}" />
<style type="text/css">

  body, pre, p, div, input, h1,h2,h3,h4,h5 {
    font-family : MS Yahei, Consolas, Courier New;
  }

  body, pre, p, div, input {
      font-size: 1em;
  }

  .article {
    font-family: KaiTi;
    font-size: 26px;
    border: 0px;
    background-color: #eee;
    width: 90%;
    // max-width: 960px;
    min-width: 320px;
    margin: auto;
  }

  .cache_field {
    border: 0px;
    readonly: readonly;
    margin: 0px;
    padding: 0px
  }

  .error {
    color: red;
  }

  .notice {
    color: blue;
  }
</style>
</head>
<body>
    <div>
        {{ content | safe }}
    </div>
</body>'''


@app.route('/', methods=['GET'])
def novel_index():
    context = {
        "encoding": 'utf-8'
    }

    tn = db.DB_table_novel
    stmt = select([tn.c.id, tn.c.name, tn.c.author, tn.c.category, tn.c.length, tn.c.status, tn.c.desc, tn.c.recommends,
                  tn.c.favorites, tn.c.recommends_month, tn.c.update_on, tn.c.chapter_table, tn.c.timestamp])
    try:
        rs = db.engine.execute(stmt)
        i = 0
        odd = True
        sb = []
        sb.append('<h1 align="center">书库</div>')
        sb.append('<table align="center" width="100%" cellpadding="5">')
        for r in rs:
            if i % 4 == 0:
                sb.append('<tr style="%s;">' % 'background-color:#eee' if odd else '')
                odd = not odd
            sb.append('<td align="right"><img src="/s/%(name)s.jpg" width="100px" height="125px"></td>' % r)
            sb.append('<td><h3><a href="/%(id)s/" alt="%(desc)s">%(name)s</a></h3>作者: <a href="/author/%(author)s/">%(author)s</a>' % r)
            i += 1
            if i % 4 == 0:
                sb.append('</tr>')
        sb.append('</table>')
        content = '\n'.join(sb)
    except Exception as err:
        content = '<p class="error">' + str(err) + '</p>'

    context['content'] = content
    resp = make_response(render_template_string(template_page, **context))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp


@app.route('/<int:novel_id>/', methods=['GET'])
def novel_page(novel_id):
    context = {
        "encoding": 'utf-8'
    }

    cols = 4

    tn = db.DB_table_novel
    stmt = select([tn.c.id, tn.c.name, tn.c.author, tn.c.category, tn.c.length, tn.c.status, tn.c.desc, tn.c.recommends,
                  tn.c.favorites, tn.c.recommends_month, tn.c.update_on, tn.c.chapter_table, tn.c.timestamp]
                  ).where(tn.c.id==novel_id)
    try:
        rs = db.engine.execute(stmt)
        rn = rs.fetchone()
        table = 'novel_%(id)s_%(name)s' % rn
        t = db.get_chapter_table(table)
        stmt = select([t.c.id, t.c.name, t.c.is_section]).order_by(t.c.id)
        rs = db.engine.execute(stmt)

        i = 0
        odd = True
        sb = []
        sb.append('<h1 align="center">%(name)s</div>' % rn)
        sb.append('<p align="center"><a href="/">返回书库首页</a></p>\n')
        sb.append('<table align="center" width="100%">')
        for r in rs:
            if i % cols == 0:
                sb.append('<tr style="%s">' % 'background-color:#eee' if odd else '')
                odd = not odd
            if r['is_section']:
                sb.append('</tr><tr style="background-color:silver"><td colspan="%s" align="center">%s</td></tr>' % (cols, r['name']))
                i = 0
            else:
                sb.append('<td><a href="/%s/%s/">%s</a></td>' % (novel_id, r['id'], r['name']))
                i += 1
            if i % cols == 0:
                sb.append('</tr>')
        sb.append('</table>')
        content = '\n'.join(sb)
    except Exception as err:
        content = '<h1>Error</h1><p class="error">' + str(err) + '</p>'

    context['content'] = content
    resp = make_response(render_template_string(template_page, **context))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp



@app.route('/<int:novel_id>/<int:chapter_id>/', methods=['GET'])
def chapter(novel_id, chapter_id):
    context = {
        "encoding": 'utf-8'
    }

    tn = db.DB_table_novel
    stmt = select([tn.c.name]).where(tn.c.id==novel_id)
    try:
        novel_name = db.engine.execute(stmt).scalar()
        table = 'novel_%s_%s' % (novel_id, novel_name)
        t = db.get_chapter_table(table)
        stmt = select([t.c.id, t.c.name, t.c.content, t.c.is_section]).where(t.c.id==chapter_id)
        rs = db.engine.execute(stmt)
        r = rs.fetchone()

        stmt = select([t.c.id]).where(and_(t.c.id<chapter_id, t.c.is_section==False)).order_by(t.c.id.desc()).limit(1)
        prev = db.engine.execute(stmt).scalar()

        stmt = select([t.c.id]).where(and_(t.c.id>chapter_id, t.c.is_section==False)).order_by(t.c.id).limit(1)
        nxt = db.engine.execute(stmt).scalar()

        prev = '/%s/%s/' % (novel_id, prev) if prev else '#'
        nxt = '/%s/%s/' % (novel_id, nxt) if nxt else '#'
        nav = '<div align="center"><a href="{1}">上一章</a>  <a href="/{0}">返回书页</a>  <a href="{2}">下一章</a></div>'.format(novel_id, prev, nxt)

        sb = []
        sb.append('<h1 align="center">%(name)s</div>' % r)
        sb.append('<center><p>快捷键：左、右键 翻页，-、=(+)键 字体大小</p></center>')
        sb.append(nav)
        sb.append('<div style="width:100%;background-color:#eee;">')
        sb.append('<hr />')
        sb.append('<div id="content" class="article">%s</div>\n' % r['content'])
        sb.append('<hr />')
        sb.append('</div>')
        sb.append(nav)
        sb.append('''
        <script language="javascript">
        document.onkeydown = key_pressed;
        var prev_page="{0}";
        var next_page="{1}";
        function key_pressed(event) {{
          if (event.keyCode==37) location=prev_page;
          if (event.keyCode==39) location=next_page;

          if (event.keyCode==189) {{
            size = parseInt(document.all["content"].style['font-size']);
            size -= 2;
            if (size <= 8) size = 8;
            document.all["content"].style['font-size'] = size + 'px';
          }}
          if (event.keyCode==187) {{
            size = parseInt(document.all["content"].style['font-size']);;
            size += 2;
            if (size >= 48) size = 68;
            document.all["content"].style['font-size'] = size + 2 + 'px';
          }}
          if (event.keyCode==48) {{
            document.all["content"].style['font-size'] = '26px';
          }}
        }}
        </script>
        '''.format(prev, nxt))

        content = '\n'.join(sb)
    except Exception as err:
        log.exception(err)
        content = '<h1>Error</h1><p class="error">' + str(err) + '</p>'

    context['content'] = content
    resp = make_response(render_template_string(template_page, **context))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp



class RenderBase(object):
    pass

class ReadNovel(RenderBase):
    def GET(self, name):
        web.header('Content-Type','text/html; charset=utf-8', unique=True)

        if not name:
            rc = self.render_novels()
        elif name.find('favicon') >= 0:
            rc = ''
        else:
            rc = self.render_index(name)

        return rc

    def render_novels(self):

        sb = []
        root = './db'
        files = os.listdir(root)

        for f in files:
            if not f.endswith('.novel'): continue
            name = os.path.basename(f)
            name = websafe(name.replace('.novel', ''))
            # name = name.decode('GBK')
            link = '<li><a href="/{0}">{0}</a></li>'.format(name)
            sb.append(link)
        sb = sorted(sb, reverse=True)
        sb.insert(0, '<ul>')
        sb.append('</ul>')

        return self.render_page(sb)

    def render_index(self, bookname):
        name = bookname
        db = DatabaseUtility()
        db.open('db/%s.novel' % name)
        succeed, rows, dur = db.execute('SELECT idx, name, link FROM novel_index')

        if not succeed:
            db.close()
            return 'Select from db failed.'

        sb = []
        sb.append('<center><h1>%s</h1></center>\n' % name)
        sb.append('<center><p><a href="/">返回书库首页</a></p></center>\n')
        sb.append('<table style="border:0px;">\n')
        i = 0
        j = 0
        for rec in rows:
            hash = get_hash(rec['name'])
            if i == 0:
                if j == 0:
                    sb.append('<tr>\n')
                    j = 1
                else:
                    sb.append('<tr style="background-color:#eee;">\n')
                    j = 0

            sb.append('<td><a href="/%s/%s">%s</a></td>\n' % (name, hash, rec['name']))
            if i == 3:
                sb.append('</tr>\n')
                i = 0
            else:
                i += 1
        sb.append('</table>\n')
        db.close()
        return self.render_page(sb)

class ReadArticle(RenderBase):
    def GET(self, name, id):
        web.header('Content-Type','text/html; charset=utf-8', unique=True)

        if not id:
            rc = 'no id specified'
        else:
            rc = self.render_article(name, id)

        return rc

    def render_article(self, bookname, article_id):
        name = bookname
        id = article_id
        db = DatabaseUtility()
        db.open('db/%s.novel' % name)
        succeed, cursor, dur = db.execute('''
            select a.name, a.idx, b.content
            from novel_index as a, novel_article as b
            where a.id = b.id
            and a.id = ?
            limit 1
        ''', [id])

        if not succeed:
            db.close()
            return 'Select from db failed.'

        rec = cursor.fetchone()
        if not rec:
            content = '本章未下载'
            db.close()
            return self.render_page(content)

        succeed, prev, dur = db.execute_none_query('''
            select id
            from novel_index
            where cast(idx as int) < %s
            order by cast(idx as int) desc
            limit 1
        ''' % rec['idx'])

        succeed, next, dur = db.execute_none_query('''
            select id
            from novel_index
            where cast(idx as int) > %s
            order by cast(idx as int)
            limit 1
        ''' % rec['idx'])

        content = 'zip' in sys.argv and unzip(rec['content']) or rec['content']

        next = '/' + next if next else ''
        prev = '/' + prev if prev else ''
        nav = '<center><a href="/{0}{1}">上一章</a>  <a href="/{0}">目录</a>   <a href="/{0}{2}">下一章</a></center>'.format(name, prev, next)

        sb = []
        sb.append('<div style="width:100%;height:100%;background-color:#eee;">')
        sb.append('<center><h1>%s - %s</h1></center>\n' % (name, rec['name']))
        # sb.append('<center><a href="/{0}/{1}">上一章</a>  <a href="/{0}">目录</a>   <a href="/{0}/{2}">下一章</a></center>'.format(name, prev, next))
        sb.append(nav)
        sb.append('<center><p>快捷键：左、右键 翻页，-、=(+)键 字体大小</p></center>')
        sb.append('<hr />')
        sb.append('<div id="content" style="font-family:kaiti;font-size:26px;border:0px;max-width:960px;margin:auto;">%s</div>\n' % content)
        sb.append('<hr />')
        # sb.append('<center><a href="/{0}/{1}">上一章</a>  <a href="/{0}">目录</a>   <a href="/{0}/{2}">下一章</a></center>'.format(name, prev, next))
        sb.append(nav)
        sb.append('</div>')
        sb.append('''
        <script language="javascript">
        document.onkeydown=keypage
        var prevpage="/{0}{1}"
        var nextpage="/{0}{2}"
        function keypage() {{
          if (event.keyCode==37) location=prevpage
          if (event.keyCode==39) location=nextpage

          if (event.keyCode==189) {{
            size = parseInt(document.all["content"].style['font-size']);
            size -= 2
            if (size <= 8) size = 8
            document.all["content"].style['font-size'] = size + 'px'
          }}
          if (event.keyCode==187) {{
            size = parseInt(document.all["content"].style['font-size']);
            size += 2
            if (size >= 48) size = 68
            document.all["content"].style['font-size'] = size + 2 + 'px'
          }}
          if (event.keyCode==48) {{
            document.all["content"].style['font-size'] = '26px'
          }}
        }}
        </script>
        '''.format(name, prev, next))

        db.close()
        return self.render_page(sb)

#web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
if __name__ == "__main__":
    app.run()
