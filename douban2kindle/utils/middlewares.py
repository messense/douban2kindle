# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class ExceptionMiddleware(object):

    def process_exception(self, request, exception):
        import pdb; pdb.set_trace()
