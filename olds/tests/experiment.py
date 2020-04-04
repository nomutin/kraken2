# -*- coding: utf-8 -*-
from kraken import *


def print_varsize():
    import types
    print("{}{: >15}{}{: >10}{}".format('|','Variable Name','|','  Size','|'))
    print(" -------------------------- ")
    for k, v in globals().items():
        if hasattr(v, 'size') and not k.startswith('_') and not isinstance(v,types.ModuleType):
            print("{}{: >15}{}{: >10}{}".format('|',k,'|',str(v.size),'|'))
        elif hasattr(v, '__len__') and not k.startswith('_') and not isinstance(v,types.ModuleType):
            print("{}{: >15}{}{: >10}{}".format('|',k,'|',str(len(v)),'|'))

import sys
import struct
import urllib.request

def parse_jpeg(res):
    while not res.closed:
        (marker, size) = struct.unpack('>2sH', res.read(4))
        if marker == b'\xff\xc0':
            (_,height,width,_) = struct.unpack('>chh10s', res.read(size-2))
            return (width,height)
        else:
            res.read(size-2)

def parse_png(res):
    (_,width,height) = struct.unpack(">14sII", res.read(22))
    return (width, height)

def parse_gif(res):
    (_,width,height) = struct.unpack("<4sHH", res.read(8))
    return (width, height)

def get_image_size(url):

    request = urllib.request.Request(url=url, headers=camouflage_headers)
    with urllib.request.urlopen(request) as res:
        size = (-1,-1)
        if res.status == 200:
            signature = res.read(2)
            if signature == b'\xff\xd8': #jpg
                size = parse_jpeg(res)
            elif signature == b'\x89\x50': #png
                size = parse_png(res)
            elif signature == b'\x47\x49': #gif
                size = parse_gif(res)
        res.close()
        return size


if __name__ == '__main__':
    img = ImageURL('http://eromangaget.com/wp-content/uploads/2018/09/1536019486.jpg')
    print(get_image_size('http://eromangaget.com/wp-content/uploads/2018/09/1536019486.jpg'))