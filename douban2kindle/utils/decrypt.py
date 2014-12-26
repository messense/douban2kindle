# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re


def _x2y(a):
    i = 0
    l = []
    while i < len(a):
        c = a[i]
        i += 1
        if i < len(a):
            l.append(256 * c + a[i])
        i += 1
    return ''.join(map(unichr, l))


def decrypt(encrypted):
    _hex_chs = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$_~'
    _key = [
        37, 7, 20, 41, 59, 53, 8, 24, 5, 62, 31, 4, 32, 6, 50, 36, 63, 35, 51,
        0, 13, 43, 46, 40, 15, 27, 17, 57, 28, 54, 1, 60, 21, 22, 47, 42, 30,
        39, 12, 3, 9, 45, 29, 23, 56, 2, 16, 61, 52, 44, 25, 14, 49, 34, 33,
        10, 58, 55, 19, 26, 11, 18, 48, 38
    ]
    _str_reg = re.compile(r'[^0-9A-Za-z$_~]')
    # init
    key = []
    tbl = {}
    for i in range(64):
        key.append(_hex_chs[_key[i]])
        tbl[key[i]] = i

    pad = _hex_chs[64]
    n1 = n2 = n3 = n4 = 0
    sa = []

    encrypted = _str_reg.sub('', encrypted)
    encrypted_len = len(encrypted)
    i = 0
    while i < encrypted_len:
        n1 = n2 = n3 = n4 = 0
        if encrypted[i] in tbl:
            n1 = tbl[encrypted[i]]

        i += 1
        if i < encrypted_len:
            if encrypted[i] in tbl:
                n2 = tbl[encrypted[i]]

        i += 1
        if i < encrypted_len:
            if encrypted[i] in tbl:
                n3 = tbl[encrypted[i]]

        i += 1
        if i < encrypted_len:
            if encrypted[i] in tbl:
                n4 = tbl[encrypted[i]]

        i += 1
        sa.append(n1 << 2 | n2 >> 4)
        sa.append((15 & n2) << 4 | n3 >> 2)
        sa.append((3 & n3) << 6 | n4)

    e2 = encrypted[-2:]
    if e2[0] == pad:
        sa = sa[:-2]
    else:
        if e2[1] == pad:
            sa = sa[:-1]

    return _x2y(sa)
