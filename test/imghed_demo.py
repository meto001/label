# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/11 17:13'

import imghdr
import os
path = 'F:/数据需求/标注系统测试/1/'

list1 = os.listdir(path)

for file in list1:
    a = imghdr.what(path+file)
    pass
pass