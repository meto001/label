# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/14 17:20'

from app.models.source_image_path import Source_image_path
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc, asc


class Check_data_info(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_user = relationship('Check_user')
    check_user_id = Column(Integer, ForeignKey('check_user.id'))
    task_id = Column(Integer)
    task_details = relationship('Task_details')
    task_details_id = Column(Integer, ForeignKey('task_details.id'))

    result_status = Column(Integer,comment='质检结果：0 错误，1 正确')
    is_complate = Column(Integer)
    locks = Column(Integer, default=0)
    quality_user = Column(String(50))
    quality_time = Column(Integer)
    error_count = Column(Integer)

    @classmethod
    def get_has_locks(cls, check_user_id,quality_user):
        locks = Check_data_info.query.filter_by(check_user_id=check_user_id,locks=1,quality_user=quality_user).first()
        return locks

    @classmethod
    def get_new_quality_data(cls, check_user_id):
        new_quality_data = Check_data_info.query.filter_by(check_user_id=check_user_id,is_complate=0, locks=0).first()
        return new_quality_data

    @classmethod
    def get_last_quality_data(cls, quality_user,task_details_id, check_user_id):

        check_data_info = Check_data_info.query.filter_by(task_details_id=task_details_id, check_user_id=check_user_id).first()
        if check_data_info:
            check_data_info_id = check_data_info.id

            last_quality_data = Check_data_info.query.filter(Check_data_info.quality_user==quality_user,Check_data_info.check_user_id==check_user_id,
                                                             Check_data_info.is_complate == 1, Check_data_info.id<check_data_info_id
                                                             ).order_by(desc(Check_data_info.id)).first()
            return last_quality_data
        else:
            return None

    @classmethod
    def get_next_quality_data(cls, quality_user,task_details_id, check_user_id):

        check_data_info = Check_data_info.query.filter_by(task_details_id=task_details_id,
                                                             check_user_id=check_user_id).first()
        if check_data_info:
            check_data_info_id = check_data_info.id

            next_quality_data = Check_data_info.query.filter(Check_data_info.quality_user==quality_user,Check_data_info.check_user_id==check_user_id,
                                                             Check_data_info.is_complate == 1, Check_data_info.id>check_data_info_id).order_by(asc(Check_data_info.id)).first()
            return next_quality_data
        else:
            return None