# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
try:
    import simplejson as json
except ImportError:
    import json

from django.http import JsonResponse
from django.views.generic import View
from django.utils.encoding import smart_text

from utils.decrypt import decrypt


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
        author_id = smart_text(data.get('authorId', '')).strip()
        book_size = len(book_data)

        import pdb; pdb.set_trace()
