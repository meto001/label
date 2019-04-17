# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float


class Task(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = relationship('Source')
    source_id = Column(Integer, ForeignKey('source.id'))

    # 存放属性值们的字段
    prop_ids = Column(String(300))

    task_name = Column(String(100))

    difficult_num = Column(Float)

    is_complete = Column(Integer)
