# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float


class Task_details(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)

    task = relationship('Task')
    task_id = Column(Integer, ForeignKey('task.id'))

    photo_path = Column(String(300))

    is_complete = Column(Integer)
