# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task
from django.core.mail import EmailMessage


logger = logging.getLogger(__name__)


@shared_task
def send_mail(subject='', body='', from_email=None, to=None, attachments=None):
    email = EmailMessage(
        subject,
        body,
        from_email,
        to,
        attachments=attachments
    )
    try:
        email.send()
    except Exception as e:
        logger.exception(
            'Error sending email to: %s, subject: %s',
            to,
            subject
        )
        return False
    else:
        return True
