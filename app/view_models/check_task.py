# _*_ coding:utf-8 _*_
import time

from app import db
from app.models.check_data_info import Check_data_info
from app.models.check_user import Check_user
from app.models.task import Task

__author__ = 'meto'
__date__ = '2019/5/16 10:10'


class CheckTaskViewModel:
    def __init__(self, check_task):
        self.date = ''
        self.check_task_id = check_task.id
        self.tasks = []
        self.__parse(check_task)

    def __parse(self, check_task):
        timeArray = time.localtime(check_task.create_time - 86400)
        self.date = time.strftime('%Y-%m-%d', timeArray)
        # 通过id查询到数据,
        task_ids = db.session.query(Check_user.task_id).filter(Check_user.check_task_id==check_task.id, Check_user.status == 0).group_by(Check_user.task_id).all()
        # print(task_ids)
        task_id = []
        for id in task_ids:
            task_id.append(id[0])
        self.tasks = [self.__map_to_task(id,check_task) for id in task_id]

    def __map_to_task(self,id,check_task):
        task = Task.query.filter_by(id=id).first()
        date = Check_user.query.filter_by(check_task_id = check_task.id).first().check_date
        # timeArray = time.localtime(check_task.create_time-86400)
        # date = time.strftime('%Y-%m-%d', timeArray)
        return dict(
            check_task_id = check_task.id,
            date=date,
            task_name=task.task_name,
            task_id=id,
            task_type=task.source.label_type.name
        )


class CheckTaskCollection:

    def __init__(self):
        self.quality_data = ''

    def fill(self, check_tasks):
        self.quality_data = [CheckTaskViewModel(check_task) for check_task in check_tasks]

    data = {
        'users':[
            {'check_user': 'paopao', 'check_num': 100, 'total_num': 200, 'error_num': 2, 'already_num': 50},
            {'check_user': 'wangwei', 'check_num': 60, 'total_num': 300, 'error_num': 4, 'already_num': 40}
        ]
    }


class CheckUserViewModel:
    def __init__(self, check_user):
        self.label_user = check_user.user
        self.check_num = check_user.check_num
        self.total_num = check_user.total_num
        self.check_date = check_user.check_date
        self.error_num = ''
        self.already_num = ''
        self.__parse(check_user.id)

    def __parse(self,check_user_id):
        error_num = Check_data_info().query.filter_by(check_user_id=check_user_id, result_status=0).count()
        self.error_num = error_num
        already_num = Check_data_info().query.filter(Check_data_info.check_user_id==check_user_id, Check_data_info.result_status != None).count()
        self.already_num = already_num


class CheckUserCollection:
    def __init__(self):
        self.check_task_id = ''
        self.users = []

    def fill(self,check_users, check_task_id):
        self.check_task_id = check_task_id
        self.users = [CheckUserViewModel(check_user) for check_user in check_users]