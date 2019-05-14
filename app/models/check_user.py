# _*_ coding:utf-8 _*_

__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from app.models.source_image_path import Source_image_path
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc


class Check_user(Base):
    pass
    id = Column(Integer, primary_key=True, autoincrement=True)
    task = relationship('Task')
    task_id = Column(Integer, ForeignKey('task.id'))
    user = Column(String(50))
    check_data = Column(String(50))
    check_num = Column(Integer)
    status = Column(Integer, default=0, comment='0 未质检 1 质检通过 2 质检不通过（返工）')
    total_num = Column(Integer)
    right_rate = Column(Float)
    rework_status = Column(Integer,comment='0 未完成返工，1 已完成返工')

    frame_num = Column(Integer,comment='框数')