# _*_ coding:utf-8 _*_

__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from app.models.source_image_path import Source_image_path
from sqlalchemy.orm import relationship
from app.models.base import Base, db
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc


class Check_user(Base):
    pass
    id = Column(Integer, primary_key=True, autoincrement=True)
    task = relationship('Task')
    task_id = Column(Integer, ForeignKey('task.id'))

    check_task = relationship('Check_task')
    check_task_id = Column(Integer, ForeignKey('check_task.id'))

    user = Column(String(50))
    check_date = Column(String(50))
    check_num = Column(Integer)
    status = Column(Integer, default=0, comment='0 未质检 1 质检通过 2 质检不通过（返工）')
    total_num = Column(Integer)
    right_rate = Column(Float)
    rework_status = Column(Integer,comment='0 未完成返工，1 已完成返工')

    frame_num = Column(Integer,comment='框数')

    # @classmethod
    # def get_check_task(cls):
    #     db.session.query().filter_by(status=0).group_by(Check_user.task_id).all()
    #

    @classmethod
    def get_check_user(cls,check_task_id, task_id):
        check_users = Check_user.query.filter_by(check_task_id=check_task_id, task_id=task_id, status=0).all()
        return check_users

    @classmethod
    def get_id(cls, check_date, user, task_id, check_task_id):
        check_user= Check_user.query.filter_by(check_date=check_date, user=user, task_id=task_id, check_task_id=check_task_id).first()
        if check_user:
            check_user_id = check_user.id
        else:
            check_user_id = None
        return check_user_id
