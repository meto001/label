# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/14 17:20'

from app.models.source_image_path import Source_image_path
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc


class Check_data_info(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_user = relationship('Check_user')
    check_user_id = Column(Integer, ForeignKey('check_user.id'))
    task_details = relationship('Task_details')
    task_details_id = Column(Integer, ForeignKey('task_details.id'))

    result_status = Column(Integer,comment='质检结果：0 错误，1 正确')
    locks = Column(Integer, default=0)
    lock_user = Column(String(50))
    quality_user = Column(String(50))
    quality_time = Column(Integer)
    error_count = Column(Integer)
