# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/19 10:18'


class TaskViewModel:

    def __init__(self, task):
        self.id = task.id
        self.name = task.task_name
        self.label_type = task.source.label_type.name
        self.count = task.source.count
        self.create_time = task.create_time
        self.difficult_num = task.difficult_num
        self.is_complete = task.is_complete
        self.sampling_rate = task.source.label_type.sampling_rate


class TaskCollection:

    def __init__(self):
        self.tasks = []

    def fill(self, tasks):
        self.tasks = [TaskViewModel(task) for task in tasks]
