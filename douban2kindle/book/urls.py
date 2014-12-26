# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = patterns(
    '', # prefix
    url(r'send$', csrf_exempt(views.SendView.as_view()), name='book.send'),
)
