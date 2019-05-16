# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/25 11:28'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, SmallInteger


class Task_details_value(Base):

    id = Column(Integer,primary_key=True,autoincrement=True)

    task_details = relationship('Task_details')

    task_detail_id = Column(Integer, ForeignKey('task_details.id'))

    task_id = Column(Integer)

    prop = relationship('Property')

    prop_id = Column(Integer, ForeignKey('property.id'))

    prop_type = Column(Integer)

    # 如果prop_type=2的话，则prop_option_id 值为坐标值
    prop_option_value = Column(String(24))

    # 此字段作为prop_option_value的备用字段，标注员数据同时保存两个字段，如果质检员修改了数据，则放到这里。
    prop_option_value_final = Column(String(24),comment='此字段作为prop_option_value的备用字段，标注员数据同时保存两个字段，如果质检员修改了数据，则放到这里。')


    photo_path = Column(String(300))

    create_user = Column(String(24))