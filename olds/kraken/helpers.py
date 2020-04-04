# -*- coding: utf-8 -*-
"""
helpers functions and variables for Kraken
"""

import os

AVAILABLE_EXTENSIONS = ['jpg', 'png']

Define = True

camouflage_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
}


def mkdir(_path) -> None:
    """
    :param _path: URL.pathを用いる
    :return: None
    """
    if not os.path.exists(_path):
        os.makedirs(_path)


def shorten_string_for_comic(t):
    """
    【】とその中の文字、｜・ーとその後の文字を削除する
    """
    if '【' in t and '】' in t:
        t = t[:t.find('【')] + t[t.find('】') + 1:]
    for obj in ('|', '-'):
        if obj in t:
            t = t[:t.find(obj)]
    return t
