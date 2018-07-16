#!/usr/bin/evn python

import logging
from django.http import Http404, StreamingHttpResponse, HttpResponseRedirect
from django.utils.encoding import escape_uri_path
from django.contrib.messages import error, debug, info, warning
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.conf import settings
import unicodedata
from ..models.novelutil import (
    get_novel_info, get_latest_chapters, get_all_chapters,
    list_hot_novels, list_recommend_novels, list_favorite_novels
)
from .base import BaseViewMixin

import zipfile
import os
from utils.utils import clean_content
from django.template.defaultfilters import striptags, linebreaksbr
from django.core.mail import EmailMessage


__author__ = 'samuel'

log = logging.getLogger(__name__)


class NovelView(TemplateView, BaseViewMixin):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        novel = context.get('novel')
        if 'download' in self.request.GET:
            zipbook = self.gen_ebook(novel)
            head, fname = os.path.split(zipbook)
            url = settings.MEDIA_URL + fname
            f = open(zipbook, 'rb')
            return HttpResponseRedirect(url)
            # response = StreamingHttpResponse(f, content_type='application/zip')
            # response['Content-Disposition'] = 'attachment;filename="%s.zip"' % escape_uri_path(novel['name'])
            # return response
        elif 'email' in self.request.GET:
            user = self.request.user
            zipbook = self.gen_ebook(novel)

            email = EmailMessage(
                novel['name'],             # mail subject
                novel['name'],      # mail body
                # user.email,             # from
                to=[user.email, ],         # to
                # [],                     # bcc
                reply_to=[user.email],
                # headers={'Message-ID': 'foo'},
            )
            email.attach_file(zipbook)
            email.send()
            log.info('%s sent as email attachment to %s' % (novel['name'], user))
            info(request, _('%s is sent to your email box as attachment.' % novel['name']))
        return super(NovelView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NovelView, self).get_context_data(**kwargs)
        nid = kwargs.get('nid', None)
        if nid is None:
            raise Http404('Novel does not exist.')

        novel = get_novel_info(nid, add_last_chapter=True, with_actions_user_id=self.request.user.id)
        if not novel:
            raise Http404('Novel (id=%s) is not found' % nid)

        context['novel'] = novel
        context['latest_chapters'] = get_latest_chapters(nid)
        context['chapters'] = get_all_chapters(nid)


        context['top_a'] = {
            "title": "热门小说", "subtitle": "", "keyword": "hot", "icon": "fa fa-fire",
            "novels": list_hot_novels(page_items=5)
        }

        context['tops_b'] = [
            {"title": "推荐榜", "subtitle": "", "keyword": "recommend",
             "novels": list_recommend_novels(page_items=6), "icon": "fa fa-thumbs-up"},
            {"title": "收藏榜", "subtitle": "",  "keyword": "favorite",
             "novels": list_favorite_novels(page_items=6), "icon": "fa fa-star"},
        ]

        return context

    def gen_ebook(self, novel):

        nid = novel['id']
        name = unicodedata.normalize("NFKD", novel['name'])
        author = unicodedata.normalize("NFKD", novel['author'])
        desc = unicodedata.normalize("NFKD", novel['desc'])

        # folder = os.environ.get('TMP')
        folder = settings.MEDIA_ROOT
        # zipname = '%s_%s.zip' % (nid, name)
        zipname = '%s.zip' % nid
        zippath = os.path.join(folder, zipname)
        # fname = '%s_%s.txt' % (nid, name)
        fname = '%s.txt' % nid
        fpath = os.path.join(folder, fname)

        if os.path.exists(zippath):
            return zippath

        line_bold = '=' * 30
        line = '-' * 30
        line_break = '\r\n' * 2

        chapters = get_all_chapters(nid, with_content=True)

        with open(fpath, 'w') as f:
            log.debug('\tExport novel %s(id=%s) to file %s' % (name or '', nid, zippath))
            f.writelines([line_bold, line_break, ' ' * 10, name, line_break, '作者: ' + author,
                          line_break, line_bold, line_break, '简介:' + desc, line_break * 5])

            for c in chapters:
                if c['is_section']:
                    f.writelines([line_bold, c['name'], line_bold, line_break])
                    continue
                f.writelines([line, c['name'], line, line_break])
                content = unicodedata.normalize("NFKD", c['content'])
                content = striptags(clean_content(content))
                f.write(content)
                f.writelines(line_break)
                log.debug('\tExported chapter %s_%s' % (c.id, c.name))

        with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) as myzip:
                myzip.write(fpath, fname)
        os.remove(fpath)
        return zippath