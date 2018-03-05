#!/usr/bin/python
# -*- coding=utf-8 -*-

'''
Created on Jun 3, 2011

@author: Sam
'''

import os, sys
import web
from sam.db.utility import DatabaseUtility
from sam.tools.helper import get_hash, websafe, unzip

reload(sys)
sys.setdefaultencoding('utf-8')
del sys.setdefaultencoding

from sam.logging import init_log
init_log(40)

urls = (
        "/([^/]*)/([^/]+)", "ReadArticle",
        "/([^/]*)", "ReadNovel"
)
app = web.application(urls, globals())

class RenderBase(object):
    
    def render_page(self, content, encoding='utf-8'):
        sb = []
        sb.append('''
<!doctype html>
<head>
<meta charset="{0}" />
<meta http-equiv="content-type" content="text/html; charset={0}" />
<style type="text/css">
  body, pre, p, div, input, h1,h2,h3,h4,h5 {{
    font-family : MS Yahei, Consolas, Courier New;
  }}
  
  body, pre, p, div, input {{
      font-size: 1em;
  }}
  .cache_field {{
    border: 0px;
    readonly: readonly;
    margin: 0px;
    padding: 0px
  }}
  
  .error {{
    color: red;
  }}
  
  .notice {{
    color: blue;
  }}
</style>
</head>
<body>
    <div>
        '''.format(encoding))
        
        if isinstance(content, list):
            sb.extend(content)
        elif isinstance(content, str) or isinstance(content, unicode):
            sb.append(content)
        else:
            raise 'Error: render_page needs list or str/unicode as input.'
        
        sb.append('''
    </div>
</body>
        ''')
        rc = ''.join(sb)
        del sb
        return rc     
    
    
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
