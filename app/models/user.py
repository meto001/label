# _*_ coding:utf-8 _*_
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models.base import Base
from app import login_manager
__author__ = 'meto'
__date__ = '2019/3/20 18:25'
# db = SQLAlchemy()


class User(UserMixin, Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # email = Column(String(30), nullable=False)
    nickname = Column(String(24), nullable=False)
    realname = Column(String(24), nullable=False)
    _password = Column('password',String(128), nullable=False)
    phone_number = Column(String(18), unique=True)
    level = Column(Integer)
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,raw):
        #这是加密
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        #这是验证，第一个参数是数据库里的加密串，raw是用户输入的密码：123456.  这两个参数传进去之后 自动就会返回Ture或者False。不需要你考虑别的问题。简单调用这个函数就OK
        return check_password_hash(self._password,raw)

    # 继承了UserMixin之后就不用这个get_id函数了
    # def get_id(self):
    #     return self.id


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
