# _*_ coding:utf-8 _*_
import json
from flask import escape
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/5/30 15:09'

@web.route('/viewlog',methods=['GET','POST'])
def show_log():
    with open('app/static/label.log','r') as f:
        contents = f.read()
        cont = contents.replace('\n','<br/>')
    return cont
