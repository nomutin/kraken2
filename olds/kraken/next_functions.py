# -*- coding: utf-8 -*-
import os
import img2pdf
import re
import requests
import time


def folder2pdf(folder_directory, save_directory):
    img_list = [os.path.join(folder_directory, i) for i in os.listdir(folder_directory) if i.endswith('.jpg')]
    # img_list.sort()
    pdf_name = os.path.join(save_directory, folder_directory.split('/')[-1]+'.pdf')
    with open(pdf_name, 'wb') as file:
        file.write(img2pdf.convert(img_list))


def search_nearest_url(data):
    url = data.url
    anchors = data.anchors
    degrees = [match_degree(decompose(url), decompose(anchor)) for anchor in anchors]
    return degrees


def match_degree(decomposed_obj, decomposed_anchor):

    if len(decomposed_obj) != len(decomposed_anchor):
        return 0

    if decomposed_obj == decomposed_anchor:
        return 0   # todo 消せないか？

    _match_degree = 0
    for _obj, _anchor in zip(decomposed_obj, decomposed_anchor):

        if _obj == _anchor:
            _match_degree += 1

        elif _obj.isdecimal() and _anchor.isdecimal():
            if float(_anchor) <= float(_obj):
                return 0
            else:
                _match_degree += 1 - (float(_anchor) - float(_obj))/float(_obj)
    return _match_degree/len(decomposed_obj)


def decompose(_url):
    decomposed_list = re.split('[/.,]', _url)
    return decomposed_list


def streaming(image_urls, save_directory=os.getcwd(), debug=False, interval=1):
    for i, image_url in image_urls:
        image_path = os.path.join(save_directory, str(i) + '.jpg')
        if not debug:
            with open(image_path, 'wb') as file:
                file.write(requests.get(image_url).content)
                time.sleep(interval)
