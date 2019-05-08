# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, SmallInteger, desc, asc


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

    # 质检，-1为返工, 0为未质检，1为已生成质检，2为质检完成
    quality_inspection= Column(Integer,default=0)

    def get_already_count(self,task_id):
        already_count = Task_details.query.filter_by(task_id=task_id,is_complete=1).count()

        return already_count

    def get_user_already_count(self,task_id,user):
        user_already_count = Task_details.query.filter_by(task_id=task_id,is_complete=1,operate_user=user).count()

        return user_already_count

    def get_has_locks(self,user, task_id):
        locks = Task_details.query.filter_by(operate_user=user,task_id=task_id, locks=1).first()
        return locks

    def get_new_data(self, task_id):
        new_data =Task_details.query.filter_by(is_complete=0, locks=0, task_id=task_id).first()
        return new_data

    def get_last_data(self, user, task_id, task_detail_id, now_time, today_time):
        # select * from task_details WHERE  operate_user = 'meto' AND task_id = 4 and is_complete =1 and
        # operate_create_time >10000 and operate_create_time < 2556709299 and id < 6320 ORDER BY id DESC LIMIT 1
        last_data = Task_details.query.filter(Task_details.operate_user == user, Task_details.task_id == task_id,
                                              Task_details.is_complete == 1, Task_details.operate_create_time > today_time,
                                              Task_details.operate_create_time < now_time, Task_details.id < task_detail_id).order_by(
            desc(Task_details.id)).first()
        return last_data

    def get_next_data(self, user, task_id, task_detail_id, now_time, today_time):
        next_data = Task_details.query.filter(Task_details.operate_user == user, Task_details.task_id == task_id,
                                              Task_details.is_complete == 1, Task_details.operate_create_time > today_time,
                                              Task_details.operate_create_time < now_time, Task_details.id > task_detail_id).order_by(
            asc(Task_details.id)).first()
        return next_data

    def is_check(self, task_detail_id):
        boolean = True
        data = Task_details.query.filter_by(id=task_detail_id).first()
        # 生成过质检则为True，返工或者未生成质检为False
        if data.quality_inspection <=0:
            boolean = False
        return boolean
