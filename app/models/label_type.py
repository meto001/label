# _*_ coding:utf-8 _*_
from sqlalchemy import Column, Integer, String,Float

from app.models.base import Base

__author__ = 'meto'
__date__ = '2019/4/12 14:27'


class Label_type(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, unique=True)
    name = Column(String(50))

    # 新增合格率字段
    pass_rate = Column(Float)

    # 新增抽检率
    sampling_rate = Column(Float)