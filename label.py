# _*_ coding:utf-8 _*_
import os

from app import create_app

__author__ = 'meto'
__date__ = '2019/3/21 10:09'


app = create_app()


if __name__ == '__main__':

    # 生产环境 nginx+uwsgi
    app.run(host='0.0.0.0',debug=app.config['DEBUG'], port=8282, threaded=True)
