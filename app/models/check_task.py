# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/15 16:02'

from app.models.source_image_path import Source_image_path
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc


class Check_task(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_task_name = Column(String(100), comment='名称格式为：2019-05-15质检任务')
    status = Column(Integer, default=0,comment='0 未完成质检，1 已完成质检')