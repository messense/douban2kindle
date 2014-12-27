# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging


class ExceptionMiddleware(object):

    logger = logging.getLogger('utils.ExceptionMiddleware')

    def process_exception(self, request, exception):
        self.logger.exception('Got an exception when processing request.')
