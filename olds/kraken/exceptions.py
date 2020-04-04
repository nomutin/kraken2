# -*- coding: utf-8 -*-


class KrakenError(Exception):
    """Krakenの基底例外クラス"""


class URLTypeError(KrakenError, TypeError):
    """URLに関する例外クラス"""
