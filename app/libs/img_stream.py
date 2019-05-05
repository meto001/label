# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/5 15:51'

import base64


def return_img_stream(img_local_path):
    img_stream = ''
    with open(img_local_path,'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode(encoding='UTF-8')
    return img_stream
