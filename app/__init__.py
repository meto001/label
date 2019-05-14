# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/3/20 18:18'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.base import db
from flask_login import LoginManager
from flask_cors import CORS

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    CORS(app, resources=r'/*',support_credentials=True )
    app.config.from_object('app.secure')
    register_blueprint(app)
    db.init_app(app)
    db.create_all(app=app)
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message = '请先登录或注册'

    return app


def register_blueprint(app):
    from app.web.blue_print import web
    app.register_blueprint(web)
