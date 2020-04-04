# -*- coding: utf-8 -*-
import threading
import time
import requests  # 謎エラーのため
import os

import img2pdf
import rumps
from requests_html import HTMLSession
import pyperclip as ppc
from pync import Notifier
from functions import (name_shorten, create_date_number, isurl)

DEBUG_MODE = 1
download_directory = os.getcwd()
streaming_interval = 2


class Frame(rumps.App):
    def __init__(self):
        super(Frame, self).__init__(name=' ', title=None, icon='glasses.png')
        self.quit_button = rumps.MenuItem('Quit', key='q')
        self.menu = ('downloading', 'completed', 'save directory', ('interval', ('0s', '2s', '5s')), None)
        self.menu['interval']['2s'].state = True
        self.menu['save directory'].add(download_directory)
        check_clip = CheckClip()
        check_clip.start()

    @rumps.clicked('interval', '0s')
    @rumps.clicked('interval', '2s')
    @rumps.clicked('interval', '5s')
    def toggle(self, sender):
        global streaming_interval
        intervals = {'0s': 0, '2s': 2, '5s': 5, 0: '0s', 2: '2s', 5: '5s'}
        if sender.state:
            pass
        else:
            sender.state = True
            self.menu['interval'][intervals[streaming_interval]].state = False
            streaming_interval = intervals[sender.title]

    @rumps.clicked('save directory', download_directory)
    def go_to_main(self, sender):
        pass


class CheckClip(threading.Thread):
    daemon = True

    def run(self):
        while True:
            present_clip = ppc.paste()
            time.sleep(1)
            last_clip = ppc.paste()
            if present_clip != last_clip and isurl(last_clip):
                ims = ImageStreaming(last_clip)
                ims.start()


class ImageStreaming(threading.Thread):
    def __init__(self, _url):
        super().__init__()
        self._url = _url
        self.source = None
        self.daemon = True

    def run(self):
        Notifier.notify(message=f'Start Streaming: \n{self._url}',
                        title='Glasses', appIcon='glasses.png')
        try:
            self.image_streaming()
        except requests.exceptions.ConnectionError:
            Notifier.notify(message=f'Streaming Failed[requests.exceptions.ConnectionError]: {self._url}',
                            title='Glasses', appIcon='glasses.png')
        else:
            Notifier.notify(message=f'Succeed Streaming!: \n{self._url}',
                            title='Glasses', appIcon='glasses.png')

    def image_streaming(self):
        self.source = HTMLSession().get(self._url)
        img_elements = self.source.html.find('img')
        img_urls = [i.element.get('src') for i in img_elements if i.element.get('src').endswith('.jpg')]
        self._create_folder()
        for i, img_url in enumerate(img_urls, 1):
            image_path = os.path.join(self.folder_path, img_url.split('/')[-1])
            with open(image_path, 'wb') as file:
                if DEBUG_MODE:
                    pass
                else:
                    file.write(HTMLSession().get(img_url).content)
            time.sleep(streaming_interval)
        self._logger(img_urls)

    def _logger(self, _img_urls):  # todo  ここに除外プログラム
        _path_to_logger = os.path.join(self.folder_path, 'log.txt')
        _str_img_urls = '\n\t\t'.join(_img_urls)
        with open(_path_to_logger, 'a') as file:
            file.write(f'\n[\n\t{self._url}\n\t[\n\t\t{_str_img_urls}\n\t]\n]')

    def _create_folder(self):
        self.folder_name = self.source.html.find('title', first=True).text
        self.folder_name = name_shorten(self.folder_name)
        self.folder_path = os.path.join(os.getcwd(), create_date_number(), self.folder_name)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)


class Progress:
    @staticmethod
    def add(_url, i, overall):
        app.menu['downloading'].add(f'...{_url[-10:]} {i}/{overall}')
        print(_url)

    @staticmethod
    def pop(_url, i, overall):
        try:
            app.menu['downloading'].pop(f'...{_url[-10:]} {i}/{overall}')
        except KeyError:
            pass

    @staticmethod
    def completed(_url, overall):
        pass


def f2p(_dir):
    img_list = [os.path.join(_dir, i) for i in os.listdir(_dir) if i.endswith('.jpg')]
    img_list.sort()
    pdf_name = _dir.split('/')[:-1] + '.pdf'
    with open(pdf_name, 'wb') as file:
        file.write(img2pdf.convert(img_list))


if __name__ == '__main__':
    app = Frame()
    app.run()  # todo main()に入れるとinner_scopeでappの参照ができなくなる

# todo directoryを可変に
# todo 進行状況を表示
# todo DL完了ファイルの移動
# todo folder2pdfと結合
# todo ファイル選択プログラムを完成
# todo img_listに含まれないurlの表示を考える
# todo 上のはPDFに情報として格納する
# todo その前はテキストファイルとして保存
