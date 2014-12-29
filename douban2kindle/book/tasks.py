# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage

from book.models import Book

from utils.calibre import convert
from utils.download import download_images


logger = logging.getLogger(__name__)


@shared_task
def send_mail(subject='', body='', to=None, attachments=None):
    attachments = attachments or []
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=to
    )
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment)
    try:
        email.send()
    except:
        logger.exception(
            'Error sending email to: %s, subject: %s',
            to,
            subject
        )
        return False
    else:
        return True


@shared_task
def generate_mobi_ebook(book_id):

    def _image_exists(path):
        """Check whether path exists or not"""
        return path and os.path.exists(path)

    try:
        book = Book.objects.get(book_id=book_id)
    except Book.DoesNotExist:
        logger.warning('Can not find book with book_id: %s', book_id)

    book_dir = os.path.join(
        settings.BOOK_BASE_PATH,
        book.author,
        book.title
    )
    images_dir = os.path.join(book_dir, 'images')
    book_path = os.path.join(book_dir, 'book.html')

    images = book.images.all()
    if images:
        nonexist_imgs = [img for img in images if not _image_exists(img.path)]
        image_urls = [img.src for img in nonexist_imgs]
        # download book images
        local_images = download_images(image_urls, images_dir)

        for index, image in enumerate(nonexist_imgs):
            if local_images[index]:
                image.path = local_images[index]
                image.save()

    ebook_path = os.path.join(book_dir, 'book.mobi')
    succeed = convert(book_path, ebook_path, book.author)
    if not succeed:
        logger.warning(
            'Generate mobi ebook failed, author: %s, title: %s, subtitle: %s',
            book.author,
            book.title,
            book.subtitle
        )
        return False

    book.path = ebook_path
    book.save()

    return True
