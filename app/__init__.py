# _*_ coding:utf-8 _*_
import os



__author__ = 'meto'
__date__ = '2019/3/20 18:18'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.base import db
from flask_login import LoginManager
from flask_cors import CORS
from flask_apscheduler import APScheduler
from app.config import APSchedulerJobConfig
login_manager = LoginManager()
# 注册APScheduler
scheduler = APScheduler()
def create_app():
    app = Flask(__name__)
    try:
        CORS(app, resources=r'/*',support_credentials=True )
    except Exception as e:
        print(e)
    app.config.from_object('app.secure')
    app.config.from_object(APSchedulerJobConfig)
    register_blueprint(app)
    db.init_app(app)
    db.create_all(app=app)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message = '请先登录或注册'

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print('scheduler is start')
        scheduler.init_app(app)
        scheduler.start()
    else:
        print('scheduler is not start')

    return app


def register_blueprint(app):
    from app.web.blue_print import web
    app.register_blueprint(web)


