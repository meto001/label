# _*_ coding:utf-8 _*_


__author__ = 'meto'
__date__ = '2019/4/17 15:41'
from sqlalchemy import Column, String, Integer, ForeignKey, desc, asc, func
from sqlalchemy.orm import relationship

from app.models.base import Base, db
from app.models.task import Task


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
    quality_inspection = Column(Integer, default=0)

    quality_lock = Column(Integer, default=0, comment='质检锁，仅在返工时使用，1为锁定，当锁定时，此数据不允许标注员修改')

    # 存疑，1为存在疑问，0为正常
    is_doubt = Column(Integer, default=0, comment='存疑')

    @classmethod
    def get_already_count(cls, task_id):
        already_count = Task_details.query.filter_by(task_id=task_id, is_complete=1).count()

        return already_count

    @classmethod
    def get_user_already_count(cls, task_id, user):
        user_already_count = Task_details.query.filter_by(task_id=task_id, is_complete=1, operate_user=user).count()

        return user_already_count

    @classmethod
    def get_user_today_count(cls, task_id, user, today_start_time):
        user_today_count = Task_details.query.filter(Task_details.task_id == task_id, Task_details.operate_user == user,
                                                     Task_details.operate_time > today_start_time,
                                                     Task_details.quality_inspection != -1,
                                                     Task_details.is_complete == 1).count()
        return user_today_count

    @classmethod
    def get_be_left_doubt_count(cls, task_id, user):
        be_left_doubt_count = Task_details.query.filter_by(task_id=task_id, is_complete=0, operate_user=user,
                                                           is_doubt=1).count()
        return be_left_doubt_count

    @classmethod
    def get_has_locks(cls, user, task_id):
        locks = Task_details.query.filter_by(operate_user=user, task_id=task_id, locks=1, quality_inspection=0).first()
        return locks

    classmethod

    def get_has_doubt_locks(cls, user, task_id):
        locks = Task_details.query.filter_by(operate_user=user, task_id=task_id, locks=1, quality_inspection=0,
                                             is_doubt=1).first()
        return locks

    @classmethod
    def get_new_data(cls, task_id, task_detail_id):
        new_data = Task_details.query.filter_by(is_complete=0, locks=0, task_id=task_id, quality_inspection=0,
                                                id=task_detail_id).first()
        return new_data

    @classmethod
    def get_new_doubt_data(cls, task_id, user):
        new_data = Task_details.query.filter_by(is_complete=0, locks=0, task_id=task_id, quality_inspection=0,
                                                is_doubt=1, operate_user=user).first()
        return new_data

    @classmethod
    def get_last_data(cls, user, task_id, task_detail_id, now_time, today_time):
        # select * from task_details WHERE  operate_user = 'meto' AND task_id = 4 and is_complete =1 and
        # operate_create_time >10000 and operate_create_time < 2556709299 and id < 6320 ORDER BY id DESC LIMIT 1
        last_data = Task_details.query.filter(Task_details.operate_user == user, Task_details.task_id == task_id,
                                              Task_details.operate_create_time > today_time,
                                              Task_details.operate_create_time <= now_time,
                                              Task_details.id < task_detail_id).order_by(
            desc(Task_details.id)).first()
        return last_data

    @classmethod
    def get_last_doubt_data(cls, user, task_id, task_detail_id, now_time, today_time):
        last_data = Task_details.query.filter(Task_details.operate_user == user,
                                              Task_details.task_id == task_id,
                                              Task_details.is_doubt == 1,
                                              Task_details.operate_time <= now_time,
                                              Task_details.id < task_detail_id).order_by(
            desc(Task_details.id)).first()
        return last_data

    @classmethod
    def get_next_data(cls, user, task_id, task_detail_id, now_time, today_time):
        next_data = Task_details.query.filter(Task_details.operate_user == user, Task_details.task_id == task_id,
                                              Task_details.operate_create_time > today_time,
                                              Task_details.operate_create_time < now_time,
                                              Task_details.id > task_detail_id).order_by(
            asc(Task_details.id)).first()
        return next_data

    @classmethod
    def get_next_doubt_data(cls, user, task_id, task_detail_id, now_time, today_time):
        next_data = Task_details.query.filter(Task_details.operate_user == user,
                                              Task_details.task_id == task_id,
                                              Task_details.is_doubt == 1,
                                              Task_details.operate_time < now_time,
                                              Task_details.id > task_detail_id).order_by(
            asc(Task_details.id)).first()
        return next_data

    @classmethod
    def get_first_data(cls, user, task_id, task_detail_id, now_time, today_time):
        first_data = Task_details.query.filter(Task_details.operate_user == user,
                                               Task_details.task_id == task_id,
                                               Task_details.operate_create_time > today_time,
                                               Task_details.id < task_detail_id).order_by(
            asc(Task_details.id)).first()
        return first_data

    # 获取指定的跳转页数据
    @classmethod
    def get_quick_jump_data(cls, task_id, user, page, today_time):
        data = Task_details.query.filter(Task_details.task_id == task_id,
                                         Task_details.operate_user == user,
                                         Task_details.operate_create_time > today_time).order_by(
            asc(Task_details.id)).slice(page-1,page).first()
        return data


    @classmethod
    def is_check(cls, task_detail_id):
        boolean = True
        data = Task_details.query.filter_by(id=task_detail_id).first()
        # 生成过质检则为True，返工或者未生成质检为False
        if data and data.quality_inspection <= 0:
            boolean = False
        return boolean

    @classmethod
    def get_uncheck_user_task_details(cls, yesterday_time, today_time, task, user):
        return Task_details.query.filter(Task_details.task_id == task.id,
                                         Task_details.operate_create_time > yesterday_time,
                                         Task_details.operate_create_time <= today_time,
                                         Task_details.operate_user == user, Task_details.quality_inspection == 0,
                                         Task_details.is_complete == 1).all()

    @classmethod
    def get_users(cls, yesterday_time, today_time, task):
        return db.session.query(Task_details.operate_user, func.count(Task_details.operate_user)).filter(
            Task_details.task_id == task.id,
            Task_details.is_complete == 1,
            Task_details.operate_create_time > yesterday_time,
            Task_details.operate_create_time <= today_time).group_by(
            Task_details.operate_user,
        ).all()

    @classmethod
    def is_have_new_data(cls, yesterday_time, today_time):
        return Task_details.query.filter(Task_details.operate_create_time > yesterday_time,
                                         Task_details.operate_create_time <= today_time,
                                         Task_details.quality_inspection == 0).all()

    @classmethod
    def set_rework(cls, start_time, task_id, user):
        end_time = start_time + 86400
        all_rework = Task_details.query.filter(Task_details.operate_user == user, Task_details.task_id == task_id,
                                               Task_details.operate_create_time <= end_time,
                                               Task_details.operate_create_time > start_time, Task_details.is_complete == 1).all()
        return all_rework

    @classmethod
    def check_is_complete(cls, task_id):
        return Task_details.query.filter_by(task_id=task_id, is_complete=0).first()

    @classmethod
    def get_rework_data(cls, task_id, start_time, label_user):
        end_time = start_time + 86400
        rework_data = Task_details.query.filter(Task_details.operate_user == label_user,
                                                Task_details.task_id == task_id,
                                                Task_details.operate_create_time > start_time,
                                                Task_details.operate_create_time <= end_time,
                                                Task_details.is_complete == -1).first()
        return rework_data

    @classmethod
    def get_last_rework_data(cls, task_id, start_time, label_user, task_details_id):
        end_time = start_time + 86400
        rework_data = Task_details.query.filter(Task_details.operate_user == label_user,
                                                Task_details.task_id == task_id,
                                                Task_details.operate_create_time > start_time,
                                                Task_details.operate_create_time <= end_time,
                                                Task_details.is_complete == 1,
                                                Task_details.id < task_details_id).order_by(
            desc(Task_details.id)).first()
        return rework_data

    @classmethod
    def get_next_rework_data(cls, task_id, start_time, label_user, task_details_id):
        end_time = start_time + 86400
        rework_data = Task_details.query.filter(Task_details.operate_user == label_user,
                                                Task_details.task_id == task_id,
                                                Task_details.operate_create_time > start_time,
                                                Task_details.operate_create_time <= end_time,
                                                Task_details.is_complete == 1,
                                                Task_details.id > task_details_id).order_by(
            asc(Task_details.id)).first()
        return rework_data



    @classmethod
    def get_rework_check_details(cls, start_time, task_id, label_user):
        # 获取返未质检的数据详情
        return Task_details.query.filter(Task_details.task_id == task_id,
                                         Task_details.operate_create_time > start_time,
                                         Task_details.operate_create_time <= start_time + 86400,
                                         Task_details.operate_user == label_user, Task_details.quality_inspection == -1,
                                         Task_details.quality_lock == 0
                                         ).all()
        pass

    @classmethod
    def get_quality_status(cls, task_id):
        # 如果为空，则所有quality_inspection均等于2，该任务已完成，返回True,否则返回False
        details = Task_details.query.filter(Task_details.task_id == task_id,
                                            Task_details.quality_inspection != 2).first()
        if details is None:
            return True
        else:
            return False

    @classmethod
    def get_task_all_data(cls, task_id):
        return Task_details.query.filter_by(task_id=task_id).all()
        # 只导出一小部分
        # return Task_details.query.filter(Task_details.task_id == task_id, Task_details.operate_time <= 1589644800).all()

    @classmethod
    def get_already_task(cls, start_time):
        task_ids = []
        tasks_id = db.session.query(Task_details.task_id).filter(Task_details.operate_create_time >= start_time,
                                                                 Task_details.operate_create_time < start_time + 86400,
                                                                 Task_details.is_complete == 1).group_by(
            Task_details.task_id).all()
        for id in tasks_id:
            task_ids.append(id[0])
        tasks = Task.query.filter(Task.id.in_(task_ids), Task.is_complete == 1).all()
        return tasks

    @classmethod
    def get_undone_ids(cls, task_id):
        ids = db.session.query(Task_details.id).filter(Task_details.task_id == task_id, Task_details.is_complete == 0,
                                                       Task_details.locks == 0, Task_details.is_doubt == 0).all()
        undone_id = []
        for id in ids:
            undone_id.append(id[0])
        return undone_id

