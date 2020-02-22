"""
オレオレ画像ストリーミングアプリケーション(3代目) Kraken

nomutin's squid-like web-image streaming specialized URL wrapper '''Kraken'''

"""

import requests
from bs4 import BeautifulSoup
import dataclasses
from typing import List

__version__ = '0.0.0.e'
__author__ = 'nomutin'


class KrakenException(Exception):
    pass


class KrakenConnectionError(KrakenException):
    pass


class KrakenURLTypeError(KrakenException):
    pass


class Kraken:
    def __init__(self, _url):
        self.name = _url

        try:
            _mimicry = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
            self._genome = requests.get(self.name, headers=_mimicry)

        except requests.exceptions.ConnectionError:
            raise KrakenConnectionError(f'I cannot connect to {self.name} which you named me!')

        _content_type = self._genome.headers['Content-Type']
        if 'html' not in _content_type:
            raise KrakenURLTypeError(f'We Kraken are not given specie {_content_type} !!')

        self.tentacles = []

    @property
    def tentacles(self):
        return self._tentacles

    @tentacles.setter
    def tentacles(self, _):
        _content = self._genome.content
        _soup = BeautifulSoup(_content, 'lxml')
        self._tentacles = _soup.find_all('img')


@dataclasses.dataclass
class Tentacle:
    name: str

    def __post_init__(self):
        try:
            _mimicry = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
            if 'image' not in requests.get(self.name, headers=_mimicry).headers['Content-Type']:
                raise KrakenURLTypeError(f'My Tentacles')

        except requests.exceptions.ConnectionError:
            raise KrakenConnectionError(f'I cannot connect to {self.name} which you named my tentacle!!')
