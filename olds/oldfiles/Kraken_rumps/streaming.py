# -*- coding: utf-8 -*-

import datetime
from requests.exceptions import MissingSchema
import struct
import time
import urllib.request
import os
from requests_html import HTMLSession

__all__ = ['ImgSession', 'streaming']


class ImgSession:
    def __init__(self, _url):
        session = self.get_htmlsession(_url)
        self.url = _url
        self.title = self.get_title(session)
        self.urls = self.get_urls(session)

    @staticmethod
    def get_htmlsession(url):
        session = HTMLSession()
        return session.get(url).html

    @staticmethod
    def get_urls(session) -> list:
        elements = session.find('img')
        img_urls = [i.element.get('src') for i in elements if i.element.get('src')]
        return img_urls

    @staticmethod
    def get_title(session) -> str:
        return session.find('title', first=True).text


def streaming(_urls, interval, debug=False,
              create_folder=True, title=None, save_directory=os.getcwd(), name_shorten=True,
              restriction=True, restrict_size=(500, 400), logger=False):

    if create_folder:
        folder_path = _create_folder(title, save_directory, name_shorten=name_shorten)
    else:
        folder_path = save_directory

    if restriction:
        urls, invalid_urls = _restriction(_urls, restrict_size)
    else:
        urls = _urls
        invalid_urls = []

    for i, img_url in enumerate(urls):

        if len(img_url) <= 200:
            image_path = os.path.join(folder_path, img_url.split('/')[-1])
        else:
            image_path = os.path.join(folder_path, str(i))

        if not debug:
            with open(image_path, 'wb') as file:
                try:
                    file.write(HTMLSession().get(img_url).content)
                except MissingSchema:
                    pass

            time.sleep(interval)

    if logger:
        with open(os.path.join(folder_path, '.log'), 'a') as file:
            file.write(title + '\n\tvalid urls\n\t' + '\n\t'.join(urls) +
                       '\n\tinvalid urls\n\t' + "\n\t".join(invalid_urls)+'\n\n')


def _title_shorten(name) -> str:
    for _ in range(1, 3):
        c_right = name.find('【')
        c_left = name.find('】')
        if c_right != -1 and c_left != -1:
            name = name[:c_right]+name[c_left+1:]

        bar = name.find('|')
        if bar != -1:
            name = name[:bar]

        minus = name.find('-')
        if minus != -1:
            name = name[:minus]

        c_right = name.find('【')
        c_left = name.find('】')
        if c_right != -1 and c_left != -1:
            name = name[:c_right] + name[c_left + 1:]
        return name


def _create_folder(title, save_directory, name_shorten=True) -> str:
    date = datetime.date.today().strftime('%Y%m%d')
    if name_shorten:
        title = _title_shorten(title)
    folder_path = os.path.join(save_directory, date, title)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def _restriction(urls, restrict_size=(500, 400)) -> (list, list):
    def parse_jpeg(res):
        while not res.closed:
            (marker, size) = struct.unpack('>2sH', res.read(4))
            if marker == b'\xff\xc0':
                (_, height, width, _) = struct.unpack('>chh10s', res.read(size-2))
                return width, height
            else:
                res.read(size-2)

    def get_image_size(_url):
        try:
            with urllib.request.urlopen(_url) as res:
                _size = (-1, -1)
                if res.status == 200:
                    signature = res.read(2)
                    if signature == b'\xff\xd8':
                        _size = parse_jpeg(res)
            return _size
        except ValueError:
            pass

    confirmed = []
    unconfirmed = []
    for url in urls:
        img_size = get_image_size(url)
        try:
            if (restrict_size[0] < img_size[0]) and (restrict_size[1] < img_size[1]):
                confirmed.append(url)
            else:
                unconfirmed.append(url)
        except TypeError:
            unconfirmed.append(url)

    return confirmed, unconfirmed
