"""
オレオレ画像ストリーミングアプリケーション(3代目) Kraken

nomutin's squid-like web-image streaming specialized URL wrapper '''Kraken'''

"""

import requests
import datetime


__version__ = '0.0.0.a'
__author__ = 'nomutin'


class KrakenException(Exception):
    pass


class KrakenConnectionError(KrakenException):
    pass


class KrakenURLTypeError(KrakenException):
    pass


class Kraken:
    def __init__(self, _url):
        try:
            self.name = _url
            self._genome = requests.get(self.name)
            self.specie = 'URL'

        except requests.exceptions.ConnectionError:
            raise KrakenConnectionError(f'I cannot connect to {self.name} which you named me!')

    @property
    def specie(self):
        return self._specie

    @specie.setter
    def specie(self, _):
        content_type = self._genome.headers['Content-Type']

        if 'image' in content_type:
            self._specie = 'image'
        elif 'html' in content_type:
            self.specie = 'html'
        else:
            raise KrakenURLTypeError(f'We Kraken are not given specie {content_type} !!')
