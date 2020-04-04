# -*- coding: utf-8 -*-
"""
オレオレ画像ストリーミングアプリ　Kraken
　
ダウンロード方法
:現在はまだストリーミング不可(ver.2)

todo htmlのエラーを消す
"""

import abc
import datetime
import os
import requests_html
import struct
import urllib.request
import requests
import sys

from .helpers import shorten_string_for_comic
from .helpers import Define, camouflage_headers

from .exceptions import URLTypeError


__version__ = '2.6.0'
__author__ = 'nomutin'
# __all__ = ['PageURL', 'ImageURL']

AVAILABLE_EXTENSIONS = ['jpg', 'png']


class URL(object, metaclass=abc.ABCMeta):
    """ URLの基底クラス """

    def __init__(self, _url: str):
        try:
            URL.is_available_url(_url)
            self.url = _url
            self.html = Define
        except URLTypeError:
            print(f'url: {_url} is not available (occurred on URL.__init__)')
            sys.exit(1)

    def __repr__(self):
        return self.url

    @property
    def html(self):
        return self.__html

    @html.setter
    def html(self, _):
        """ 複数回使う可能性があるため、setterと.helpers/Defineを使用する """
        session = requests_html.HTMLSession()
        self.__html = session.get(self.url)

    @staticmethod
    def is_available_url(_url):
        res = requests.get(_url)
        status = res.status_code
        if not 200 <= int(status) <= 299:
            raise URLTypeError


class PageURL(URL):
    """
    Webページのクラス
    いつかは漫画についているタグなどの情報もプロパティとして追加していきたい
    """
    def __init__(self, _url: str):
        super().__init__(_url)
        self.title = Define
        self.image_urls = Define

    @property
    def title(self):
        return self._title

    @property
    def image_urls(self):
        return self.__image_urls

    @title.setter
    def title(self, _):
        """
        htmlからtitle属性のテキストを参照する
        複数回使う可能性があるため、setterと.helpers/Defineを使用する

        :rtype: str
        """
        title = self.html.html.find('title', first=True).text
        self._title = shorten_string_for_comic(title)

    @image_urls.setter
    def image_urls(self, _):
        """
        htmlのimgタグから、src属性を取得する
        拡張子は無差別に取得されるため、AVAILABLE_EXTENSIONSをここで用いるのもありかもしれない.
        複数回使う可能性があるため、setterと.helpers/Defineを使用する

        :rtype: list
        """
        elements = self.html.html.find('img')
        self.__image_urls = [i.element.get('src') for i in elements if i.element.get('src')]

    @property
    def path(self):
        """
        kraken/日付/titleのdirectoryのpathを返す
        :rtype: str
        """
        date_str = datetime.date.today().strftime('%Y%m%d')
        return os.path.join(os.getcwd(), date_str, self.title)

    def restrict_image_urls(self, restrict_size: (int, int) = (700, 700)):
        """
        restrict_sizeよりも大きいサイズの画像のみをimage_urlsに残す
        サイズを得る過程で画像でurlをImageURLにするので、そのままリストに登録している

        str()を用いているのは、再帰的に引数のimage_urlのtypeがImageURLだと判定されてしまうため
        __init__で型指定しているのでstrしかできない
        """
        passed_urls = []
        for i, image_url in enumerate(self.image_urls):
            image = ImageURL(str(image_url))
            try:
                if image.is_valid_image():
                    print(image_url)
                    print(image.size)
                    if image.size >= restrict_size:
                        passed_urls.append(image)
                    else:
                        print(f'{self.url} isnt vaild')
            except URLTypeError:
                print(f'url: {image_url} is not available (occurred on ImageURL.restrict_image_urls())')

        self.__image_urls = passed_urls


class ImageURL(URL):
    """画像単体URLのクラス"""

    def is_valid_image(self):
        """
        urlがAVAILABLE_EXTENSIONに含まれた画像がどうか調べるメソッド
        URLTypeErrorをraiseする
        """
        image_signatures = {b'\xff\xd8': 'jpg', b'\x89\x50': 'png', b'\x47\x49': 'gif'}
        request = urllib.request.Request(url=self.url, headers=camouflage_headers)
        with urllib.request.urlopen(request) as _res:
            signature = _res.read(2)
            if not (signature in image_signatures):
                raise URLTypeError
            elif image_signatures[signature] in AVAILABLE_EXTENSIONS:
                return True
            else:
                return False

    @property
    def content(self):
        """
        注意：画像データをそのままメモリに格納するため、とても負荷がかかるメソッド
             できれば使用後はすぐに解放できるようにしたい

        todo　使用後データ即削除方法の検証
        :rtype: binary
        """
        return self.html.content

    @property
    def size(self):
        """
        現在jpg, png使用可能
        最初のsignatureの部分を消すとなぜか動かなくなる

        headersを指定しているのは、Firefoxに偽装してurllib.error.HTTPError: HTTP Error 403: Forbidden を回避するため
         (https://ja.stackoverflow.com/questions/27922)

        コード参照:
         (https://qiita.com/zakuro/items/398dccaa8809c4613cd3)

        多分一度しか使わないのでsetter/getterは使わない

        :rtype: (int, int)
        """

        request = urllib.request.Request(url=self.url, headers=camouflage_headers)
        with urllib.request.urlopen(request) as res:
            signature = res.read(2)

            # jpg
            if signature == b'\xff\xd8':
                while not res.closed:
                    marker, size = struct.unpack('>2sH', res.read(4))
                    if marker == b'\xff\xc0':
                        _, height, width, _ = struct.unpack('>chh10s', res.read(size - 2))
                        return width, height
                    else:
                        res.read(size - 2)

            # png
            elif signature == b'\x89\x50':
                _, width, height = struct.unpack(">14sII", res.read(22))
                return width, height
