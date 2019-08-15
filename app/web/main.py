# _*_ coding:utf-8 _*_
from flask import request

__author__ = 'meto'
__date__ = '2019/3/26 10:24'

from .blue_print import web


@web.route('/')
def index():
    request
    return 'index'