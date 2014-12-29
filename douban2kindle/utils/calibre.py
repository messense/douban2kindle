# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging
import subprocess


logger = logging.getLogger(__name__)


def convert(input_path, output_path, author, cover=None):
    try:
        args = [
            'ebook-convert',
            input_path,
            output_path,
            '--authors',
            author,
            '--chapter-mark',
            'none',
            '--page-breaks-before',
            '//*[@class="pagebreak"]'
        ]
        if cover and not cover.startswith('http://') and os.path.exists(cover):
            args.extend(['--cover', cover, '--prefer-metadata-cover'])

        status = subprocess.call(args)
    except:
        logger.exception('Error calling ebook-convert.')
        return False
    else:
        if status == 0:
            return True
    logger.error(
        'Error convert ebook, input: %s, output: %s',
        input_path,
        output_path
    )
    return False
