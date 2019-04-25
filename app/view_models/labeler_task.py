# _*_ coding:utf-8 _*_
from app.models.task_details import Task_details

__author__ = 'meto'
__date__ = '2019/4/25 17:09'


class LabelTaskViewModel:

    def __init__(self, task, already_count, user_already_count):
        self.task_id = task.id
        self.task_name = task.task_name
        self.label_type = task.source.label_type.name
        # 总量
        self.all_count = task.source.count

        # 该任务已完成数量
        self.already_count = already_count

        # 该用户已完成数量
        self.user_already_count = user_already_count

        # 用户已完成框数（标注不需要）
        self.user_already_freame_count = ''


class LabelTaskCollection:

    def __init__(self):
        self.tasks = []

    def fill(self, tasks, user):

        for task in tasks:
            print(task.id)
            # 已经完成的数量
            task_detail = Task_details()
            already_count = task_detail.get_already_count(task.id)
            user_already_count = task_detail.get_user_already_count(task.id, user)

            self.tasks.append(LabelTaskViewModel(task,already_count,user_already_count))