# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import urllib2
import logging
import multiprocessing
from multiprocessing.pool import ThreadPool


logger = logging.getLogger(__name__)


def _download_image(url, save_dir):
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.URLError:
        logger.exception('Error downloading image: %s', url)
        return None
    image_name = url[url.rfind('/')+1:]
    save_path = os.path.join(save_dir, image_name)
    with open(save_path, 'w') as f:
        f.write(data)

    logger.info('Download image %s succeed, saved to %s', url, save_path)
    return save_path


def download_images(urls, save_dir):
    if not urls:
        return
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    pool = ThreadPool(multiprocessing.cpu_count())
    async_results = []
    for url in urls:
        async_results.append(pool.apply_async(
            _download_image,
            args=(url, save_dir)
        ))
    pool.close()
    pool.join()

    local_paths = []
    for result in async_results:
        path = result.get()
        local_paths.append(path)
    return local_paths
