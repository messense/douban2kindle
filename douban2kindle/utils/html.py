# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging

from django.conf import settings
from django.utils.encoding import smart_text, smart_bytes
from django.utils import six

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from . import markup


logger = logging.getLogger(__name__)


class HTMLPage(object):

    def __init__(self, title, author):
        """Set basic infomation from book

        :param title: book title
        :param subtitle: book subtitle
        :param author: book author
        :param translator: book translator, optional
        """
        self.title = smart_text(title)
        self.author = smart_text(author)

        # init HTML page
        self.page = markup.page()
        self.page.init(
            title=self.title,
            charset='UTF-8',
            author=self.author
        )

        # image types
        self.image_types = ('medium', 'orig', 'small', 'tiny', 'large')
        # image storage path
        self.book_dir = os.path.join(
            settings.BOOK_BASE_PATH,
            self.author,
            self.title
        )
        if not os.path.exists(self.book_dir):
            os.makedirs(self.book_dir)

        self.image_srcs = []
        self._html = ''

    def create(self, posts):
        """Create HTML from contents

        :param posts: list of posts from douban
        """
        title_class = 'bookTitle'
        if len(posts) > 1:
            title_class = 'chapter'
        # render book contents
        for post in posts:
            self._render_post(post, title_class)

        # render book HTML end
        self._html = six.text_type(self.page)

    def _render_post(self, post, title_class='bookTitle'):
        # render book title
        title = post.get('title')
        self.page.h1((title,), class_=title_class)

        # render book subtitle
        subtitle = post.get('subtitle')
        if subtitle:
            self.page.h2((subtitle,))

        authors = [post.get('orig_author')]
        translator = post.get('translator')
        if translator:
            authors.append('{name} 译'.format(name=translator))
        # render book author and translator
        self.page.p(tuple(authors), style='text-align: left')

        contents = post.get('contents', [])
        for content in contents:
            content_type = content.get('type')
            content_data = content.get('data')

            if content_type == 'pagebreak':
                # page break
                self._render_pagebreak(content_data)
            elif content_type == 'illus':
                # images
                self._render_illus(content_data)
            elif content_type == 'headline':
                # headline
                self._render_headline(content_data)
            elif content_type == 'paragraph':
                # paragraph
                self._render_paragraph(content_data)
            elif content_type == 'code':
                # code
                self._render_code(content_data)
            else:
                # unknown
                logger.error('Unknow type: %s', content_type)

        # force pagebreak
        self.page.p(('',), class_='pagebreak')

    def _render_pagebreak(self, data):
        # render page break
        self.page.p(('',), class_='pagebreak')

    def _render_illus(self, data):
        # render image
        self.page.div()
        # get original image size
        origin = data.get('size').get('orig')
        # get medium image size
        medium = self._get_image(data)
        if not medium:
            logger.warn('Get medium image failed')
        # get image src
        image_src = medium.get('src')
        self.image_srcs.append(image_src)

        image_name = image_src[image_src.rfind('/') + 1:]
        image_path = 'images/{name}'.format(name=image_name)
        self.page.img(
            width=origin['width'],
            height=origin['height'],
            src=image_path
        )
        # image legend
        legend = data.get('legend')
        if legend:
            self.page.label(
                smart_text(legend),
                style='color:#555; font-size:.75em; line-height:1.5;'
            )
        self.page.div.close()

    def _render_paragraph(self, data):
        # render paragraph
        text = data.get('text')
        if not text:
            text = '&nbsp;'
        text_format = data.get('format')
        if isinstance(text, list):
            # multiple content with footnotes
            plaintexts = self._get_text_list(text)
            self.page.p(
                (plaintexts,),
                style=self._get_text_style(text_format)
            )
        else:
            self.page.p(
                (smart_text(text),),
                style=self._get_text_style(text_format)
            )

    def _render_code(self, data):
        # render block code
        code = data.get('text')
        lang = data.get('language')
        lexer = get_lexer_by_name(lang)
        formatter = HtmlFormatter(
            noclasses=True,
            style=settings.CODE_HIGHLIGHT_STYLE,
        )
        text = highlight(code, lexer, formatter)
        self.page.add(text)

    def _render_headline(self, data):
        # render headline
        text = data.get('text')
        if not text:
            text = '&nbsp;'
        text_format = data.get('format')
        self.page.h2(
            (smart_text(text),),
            class_='chapter',
            style=self._get_text_style(text_format, is_headline=True)
        )

    @property
    def html(self):
        return self._html

    def save(self):
        filename = 'book.html'
        filepath = os.path.join(self.book_dir, filename)
        with open(filepath, 'w') as f:
            f.write(smart_bytes(self._html))
        return filepath

    def _get_image(self, data, index=0):
        if index >= len(self.image_types):
            return None
        image = data.get('size').get(self.image_types[index])
        if not image:
            image = self._get_image(data, index + 1)
        return image

    def _get_text_style(self, fmt, is_headline=False):
        style = (
            'text-indent: 2em; line-height:2; '
            'min-height: 2em; text-align:{align};'
        ).format(align=fmt.get('p_align', 'left'))

        if fmt.get('p_bold') == 'true':
            style = '{origin}font-weight:bold;'.format(origin=style)
        if not is_headline:
            style = '{origin}text-indent: 2em;'.format(origin=style)
        return style

    def _get_text_list(self, text_list):
        plaintexts = []
        for text in text_list:
            kind = smart_text(text.get('kind', ''))
            content = smart_text(text.get('content', ''))
            if kind == 'plaintext':
                plaintexts.append(content)
            elif kind == 'footnote':
                footnote = '<span style="color:#333; font-size:13px;">[注：{txt}]</span>'.format(  # NOQA
                    txt=content
                )
                plaintexts.append(footnote)
            elif kind == 'code':
                code = '<span>{txt}</span>'.format(
                    txt=content
                )
                plaintexts.append(code)
            elif kind == 'emphasize':
                plaintexts.append('<span style="font-weight:bold;">{txt}</span>'.format(  # NOQA
                    txt=content
                ))

        return ''.join(plaintexts)
