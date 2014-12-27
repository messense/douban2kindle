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
        self.image_dir = os.path.join(
            settings.STATICFILES_DIRS[0],
            'images',
            self.author,
            self.title
        )
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
                self.page.p(('',), class_='pagebreak')
            elif content_type == 'illus':
                # image
                self.page.div()
                # get original image size
                origin = content_data.get('size').get('orig')
                # get medium image size
                medium = self._get_image(content_data)
                if not medium:
                    logger.warn('Get medium image failed')
                # get image src
                image_src = medium.get('src')
                self.image_srcs.append(image_src)

                image_name = image_src[image_src.rfind('/') + 1:]
                image_path = os.path.join(self.image_dir, image_name)
                self.page.img(
                    width=origin['width'],
                    height=origin['height'],
                    src=image_path
                )
                # image legend
                legend = content_data.get('legend')
                if legend:
                    self.page.label(
                        smart_text(legend),
                        style='color:#555; font-size:.75em; line-height:1.5;'
                    )
                self.page.div.close()
            else:
                text = content_data.get('text')
                if not text:
                    text = '&nbsp;'
                if content_type == 'headline':
                    self.page.h2(
                        (smart_text(text),),
                        class_='chapter',
                        style='text-align:center; line-height:2; font-size:13px; min-height: 2em;'
                    )
                elif content_type == 'paragraph':
                    text_format = content_data.get('format')
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
        # render book HTML end
        self._html = six.text_type(self.page)

    @property
    def html(self):
        return self._html

    def save(self, path):
        filename = '{title}.html'.format(self.title)
        filepath = os.path.join(path, filename)
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
        return plaintexts, footnotes
