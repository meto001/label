# _*_ coding:utf-8 _*_
from flask import Blueprint

__author__ = 'meto'
__date__ = '2019/3/21 15:29'

# 此代码也可以写在web/__init__中。放在此处为了便于理解
web = Blueprint('web', __name__, static_folder='', static_url_path='')
