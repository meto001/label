# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/25 11:28'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, SmallInteger


class Task_details_value(Base):

    id = Column(Integer,primary_key=True,autoincrement=True)

    task_detail = relationship('Task_details')

    task_detail_id = Column(Integer, ForeignKey('task_detail.id'))

    task_id = Column(Integer)

    prop_id = Column(Integer)

    prop_value_id = Column(Integer)

    create_user = Column(String(24))