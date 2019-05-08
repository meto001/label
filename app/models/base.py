# _*_ coding:utf-8 _*_
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Column, SmallInteger, Integer

__author__ = 'meto'
__date__ = '2019/3/21 15:48'
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy


class SQLAlchemy(_SQLAlchemy):

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            raise e


db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True

    # 1为有效，0为废弃
    status = Column(SmallInteger, default=1)

    create_time = Column('create_time', Integer)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    def set_attrs(self, attrs_dict):
        for k, v in attrs_dict.items():
            if hasattr(self, k) and k != 'id':
                setattr(self, k, v)

    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None