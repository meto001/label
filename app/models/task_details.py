# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, SmallInteger


class Task_details(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)

    task = relationship('Task')
    task_id = Column(Integer, ForeignKey('task.id'))

    # 图片路径
    photo_path = Column(String(300))

    # 默认为0 未完成, 完成为1
    is_complete = Column(Integer, default=0)

    # 锁定状态，0为未锁定，1为锁定
    locks = Column(Integer, default=0)

    # 操作创建时间和锁定时间都用这个字段
    operate_create_time = Column(Integer)

    # 操作用户
    operate_user = Column(String(24))

    # 操作更新时间（包括修改等）
    operate_time = Column(Integer)


