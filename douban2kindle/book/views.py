# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.shortcuts import render
from django.views.generic import View


class SendView(View):

    def post(self, request):
        import pdb; pdb.set_trace()
