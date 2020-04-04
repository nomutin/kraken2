from requests_html import HTMLSession
import os
import img2pdf


class HowToUseRequestsHtml:
    def get_htmlsession(self, url):
        session = HTMLSession()
        return session.get(url).html

    def get_img_urls(self, session):
        elements = session.find('img')
        img_urls = [i.element.get('src') for i in elements if i.element.get('src')]
        return img_urls

    def get_title(self, session):
        return session.find('title', first=True).text

    def get_content(self, img_path, url):
        with open(img_path, 'wb') as file:
            file.write(HTMLSession().get(url).content)


def tk_select_directory(func):
    def wrapper():
        from tkinter import filedialog, Tk, messagebox
        loop = True
        while loop:
            root = Tk()
            root.withdraw()
            folder_path = filedialog.askdirectory(initialdir='/Users/nomura/streaming_env')
            save_path = '/'.join(folder_path.split('/')[:-1])
            res = func(folder_path, save_path)
            loop = messagebox.askyesno('succeed', 'Would you like to continue '+func.__name__+'?')
        return res
    return wrapper


@tk_select_directory
def folder2pdf(folder_directory, save_directory):
    from os import listdir, path
    import img2pdf
    img_list = [path.join(folder_directory, i) for i in listdir(folder_directory) if i.endswith('.jpg')]
    img_list.sort()
    pdf_name = path.join(save_directory, folder_directory.split('/')[-1]+'.pdf')
    with open(pdf_name, 'wb') as file:
        file.write(img2pdf.convert(img_list))


def f2p(_dir):
    img_list = [os.path.join(_dir, i) for i in os.listdir(_dir) if i.endswith('.jpg')]
    img_list.sort()
    pdf_name = _dir.split('/')[:-1] + '.pdf'
    with open(pdf_name, 'wb') as file:
        file.write(img2pdf.convert(img_list)) # todo PDF作成後元ファイル削除
        
#==========================

import datetime
import io
import time
import os
import requests
import subprocess
import tqdm
import threading
from bs4 import BeautifulSoup
from PIL import Image


def watch_clip(func):
    def wrapper(**kwargs):
        while True:
            present_clip = _paste()
            time.sleep(0.6)
            if _is_url(_paste()) and present_clip != _paste():
                threading.Thread(target=func, args=(_paste(), *kwargs)).start()
    return wrapper


@watch_clip
def kraken(_url, _interval, _debug, _restrict_size):
    _html = get_html(_url)
    _urls, _title = get_jpg_url_and_page_title(_html)
    print(_urls)
    _folder_path = create_folder(_title)
    print(_title[:50])
    for i, url in tqdm.tqdm(enumerate(_urls)):
        image_path = os.path.join(_folder_path, str(i) + '.jpg')
        if not _debug:
            stream(image_path, url, _restrict_size)
        time.sleep(_interval)
    print(f'{_title[:40]} streaming completed')


def stream(_path, _url, restrict_size):
    content = get_html(_url).content
    img = Image.open(io.BytesIO(content))
    if (img.width > restrict_size[0]) and (img.height > restrict_size[1]):
        with open(_path, 'wb') as file:
            file.write(content)


def _paste():
    p = subprocess.Popen(['pbpaste', 'r'], stdout=subprocess.PIPE,
                         close_fds=True)
    return p.communicate()[0].decode('utf-8')


def _is_url(text: str):
    return True if text.startswith('http') else False


def get_html(_url):
    return requests.get(_url)


def get_jpg_url_and_page_title(_html):
    _soup = BeautifulSoup(_html.content, 'lxml')
    _img_urls = [i.get("src") for i in _soup.find_all("img")
                 if i.get("src").endswith(".jpg")]
    return _img_urls, _soup.title.string


def shorten(txt):
    if '【' in txt and '】' in txt:
        txt = txt[:txt.find('【')]+txt[txt.find('】')+1:]
    for obj in ('|', '-'):
        if obj in txt:
            txt = txt[:txt.find(obj)]
    return txt


def create_folder(_title, save_directory=os.getcwd()) -> str:
    date = datetime.date.today().strftime('%Y%m%d')
    title = shorten(_title)
    folder_path = os.path.join(save_directory, date, title)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

