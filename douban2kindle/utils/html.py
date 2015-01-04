# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging

from django.conf import settings
from django.utils.encoding import smart_text, smart_bytes
from django.utils import six

from . import markup


logger = logging.getLogger(__name__)


class HTMLPage(object):

    def __init__(self, title, subtitle, author, translator=''):
        """Set basic infomation from book

        :param title: book title
        :param subtitle: book subtitle
        :param author: book author
        :param translator: book translator, optional
        """
        self.title = smart_text(title)
        self.subtitle = smart_text(subtitle)
        self.author = smart_text(author)
        self.translator = smart_text(translator)

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

    def create(self, contents):
        """Create HTML from contents

        :param contents: list of book contents from douban
        """
        # render book title
        self.page.h1((self.title,), class_='bookTitle')
        # render book subtitle
        self.page.h2((self.subtitle,))

        authors = [self.author]
        if self.translator:
            authors.append('{name} 译'.format(name=self.translator))
        # render book author and translator
        self.page.p(tuple(authors), style='text-align: left')

        # render book contents
        for content in contents:
            content_type = content.get('type')
            content_data = content.get('data')

            if content_type == 'pagebreak':
                # page break
                self._render_pagebreak(content_data)
            elif content_type == 'illus':
                self._render_illus(content_data)
            elif content_type == 'headline':
                self._render_headline(content_data)
            elif content_type == 'paragraph':
                self._render_paragraph(content_data)
            elif content_type == 'code':
                self._render_code(content_data)
            else:
                logger.error('Unknow type: %s', content_type)

        # render book HTML end
        self._html = six.text_type(self.page)

    def _render_pagebreak(self, data):
        # page break
        self.page.p(('',), class_='pagebreak')

    def _render_illus(self, data):
        # image
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
        text = data.get('text')
        if not text:
            text = '&nbsp;'
        text_format = data.get('format')
        if isinstance(text, list):
            # multiple content with footnotes
            plaintexts, footnotes = self._get_text_list(text)
            self.page.p(
                (''.join(plaintexts),),
                style=self._get_text_style(text_format)
            )
            if footnotes:
                self.page.p(
                    tuple(footnotes),
                    style='color:#333;font-size:13px;'
                )
        else:
            self.page.p(
                (smart_text(text),),
                style=self._get_text_style(text_format)
            )

    def _render_code(self, data):
        code = data.get('text')
        lang = data.get('language')
        # TODO: render code

    def _render_headline(self, data):
        text = data.get('text')
        if not text:
            text = '&nbsp;'
        self.page.h2(
            (smart_text(text),),
            class_='chapter',
            style='text-align:center; line-height:2; font-size:13px; min-height: 2em;'
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

    def _get_text_style(self, fmt):
        style = ('text-indent: 2em; line-height:2; '
                'min-height: 2em; text-align:{align};').format(
                    align=fmt.get('p_align', 'left')
                )
        if fmt.get('p_bold') == 'true':
            style = '{origin}font-weight:bold;'.format(origin=style)
        return style

    def _get_text_list(self, text_list):
        plaintexts = []
        footnotes = []
        index = 1
        desc = ''
        for text_index, text in enumerate(text_list):
            kind = smart_text(text.get('kind', ''))
            content = smart_text(text.get('content', ''))
            if kind == 'plaintext':
                plaintexts.append(content)
                if text_index < len(text_list) - 1:
                    desc = '[{index}]'.format(index=index)
                    plaintexts.append(desc)
                    index += 1
            elif kind == 'footnote':
                footnotes.append('{desc}{content}'.format(
                    desc=desc,
                    content=content
                ))
            elif kind == 'code':
                # TODO: render inline code style
                plaintexts.append(content)
        return plaintexts, footnotes
