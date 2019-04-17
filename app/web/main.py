# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/3/26 10:24'

from .blue_print import web


@web.route('/')
def index():
    return 'index'