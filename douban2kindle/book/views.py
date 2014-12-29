# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
try:
    import simplejson as json
except ImportError:
    import json

from django.http import JsonResponse
from django.views.generic import View
from django.utils.encoding import smart_text

from utils.decrypt import decrypt
from utils.html import HTMLPage

from . import tasks
from .models import Book


class SendView(View):

    def post(self, request):
        ret_dict = {}

        # Parse request data
        to_mail = request.POST.get('toMail')
        book_data = request.POST.get('bookData')

        if not (to_mail and book_data):
            ret_dict['status'] = 'WARN'
            ret_dict['msg'] = '参数不能为空！'
            return JsonResponse(ret_dict)

        # Decrypt book data
        data_str = decrypt(book_data)
        try:
            data = json.loads(data_str)
        except ValueError:
            ret_dict['status'] = 'WARN'
            ret_dict['msg'] = '图书数据解析出错！'
            return JsonResponse(ret_dict)

        posts = data['posts'][0]
        title = smart_text(posts.get('title', '')).strip()
        subtitle = smart_text(posts.get('subtitle', '')).strip()
        author = smart_text(posts.get('orig_author', '')).strip()
        translator = smart_text(posts.get('translator', '')).strip()
        book_size = len(book_data)

        book_id = '{author}_{title}_{size}'.format(
            author=author,
            title=title,
            size=book_size
        )

        book = self._get_or_create_book(
            book_id,
            author,
            translator,
            title,
            subtitle,
            book_size,
            posts.get('contents', [])
        )

        if not book.path or not os.path.exists(book.path):
            async_result = tasks.generate_mobi_ebook.delay(book_id)
            res = async_result.get()
            if not res:
                ret_dict['status'] = 'WARN'
                ret_dict['msg'] = '生成电子书失败！'
                return JsonResponse(ret_dict)

        # Refetch book
        book = Book.objects.get(pk=book.id)
        async_result = tasks.send_mail.delay(
            'EBook',
            '',
            to=[to_mail],
            attachments=[book.path]
        )
        res = async_result.get()
        if not res:
            ret_dict['status'] = 'WARN'
            ret_dict['msg'] = '电子书投递邮件发送失败！'
        else:
            ret_dict['status'] = 'SUCCESS'
            ret_dict['msg'] = '推送成功，请稍后查看您的 Kindle'
        return JsonResponse(ret_dict)

    def _save_book_html(self, title, subtitle, author, translator, contents):
        page = HTMLPage(title, subtitle, author, translator)
        page.create(contents)
        image_srcs = page.image_srcs
        html_path = page.save()
        return image_srcs, html_path

    def _get_or_create_book(self,
                            book_id,
                            author,
                            translator,
                            title,
                            subtitle,
                            book_size,
                            contents):
        try:
            # try get from database
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            # create book
            book = Book.objects.create(
                book_id=book_id,
                author=author,
                title=title,
                subtitle=subtitle,
                size=book_size,
                path=''
            )

            # save book html
            image_srcs, html_path = self._save_book_html(
                title,
                subtitle,
                author,
                translator,
                contents
            )

            # save images to db
            for src in image_srcs:
                book.images.create(
                    src=src,
                    path=''
                )

        return book
