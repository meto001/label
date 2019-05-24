# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/23 15:44'

class ReworkViewModel:
    def __init__(self,rework_data):
        self.rework_id = rework_data.id
        self.date = rework_data.rework_date
        self.task_id = rework_data.task_id
        self.task_name = rework_data.task.task_name
        self.all_count = rework_data.all_count
        self.right_rate = rework_data.right_rate


class ReworkCollection:

    def __init__(self):
        self.rework_datas = ''

    def fill(self, rework_datas):
        self.rework_datas = [ReworkViewModel(rework_data) for rework_data in rework_datas]