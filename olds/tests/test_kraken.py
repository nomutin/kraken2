# -*- coding: utf-8 -*-
import unittest
from kraken import PageURL
from kraken import ImageURL

PAGE_TEST_URL = 'http://abehiroshi.la.coocan.jp/tv/appare.htm'
IMAGE_TEST_URL = 'http://abehiroshi.la.coocan.jp/tv/abe.jpg'


class TestPageURL(unittest.TestCase):
    page = PageURL(PAGE_TEST_URL)

    def test_title(self):
        self.assertEqual('天晴れ夜十郎', self.page.title)

    def test_image_urls(self):
        self.assertEqual(['abe.jpg', 'appare.jpg'], self.page.image_urls)


class TestImageURL(unittest.TestCase):
    image = ImageURL(IMAGE_TEST_URL)

    def test_size(self):
        self.assertEqual((400, 509), self.image.size)

    def test_content_jpg(self):
        # todo pngのテストも行うべし
        with open('abe.jpg', 'rb') as abe:
            abe_binary = abe.read()
            self.assertEqual(abe_binary, self.image.content)


if __name__ == '__main__':
    unittest.main()
