# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging
import subprocess


logger = logging.getLogger(__name__)


def convert(input_path, output_path, author):
    try:
        subprocess.call([
            'ebook-convert',
            input_path,
            output_path,
            '--authors',
            author,
            '--chapter-mark',
            'none',
            '--page-breaks-before',
            '//*[@class="pagebreak"]'
        ])
    except:
        logger.exception('Error calling ebook-convert.')
        return False
    else:
        return True
