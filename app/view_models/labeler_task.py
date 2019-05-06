# _*_ coding:utf-8 _*_
from sqlalchemy import desc

from app.models.property import Property
from app.models.property_value import Property_value
from app.models.task_details import Task_details

__author__ = 'meto'
__date__ = '2019/4/25 17:09'


class LabelTaskViewModel:


    def __init__(self, task, completed_count, my_label_count):
        self.task_id = task.id
        self.task_name = task.task_name
        self.label_type = task.source.label_type.name
        # 总量
        self.all_count = task.source.count

        # 该任务已完成数量
        self.completed_count = completed_count

        # 该用户已完成数量
        self.my_label_count = my_label_count

        # 用户已完成框数（标注不需要）
        self.my_frame_count = ''


class LabelTaskCollection:


    def __init__(self):
        self.total = 0
        self.tasks = []

    def fill(self,total, tasks, user):
        self.total = total
        for task in tasks:
            print(task.id)
            # 已经完成的数量
            task_detail = Task_details()
            completed_count = task_detail.get_already_count(task.id)
            my_label_count = task_detail.get_user_already_count(task.id, user)

            self.tasks.append(LabelTaskViewModel(task,completed_count,my_label_count))


class LabelTaskDetailViewModel:

    def __init__(self,prop):
        self.prop_type = prop.prop_type
        self.prop_id = prop.id
        self.prop_name = prop.prop_name
        self.property_values = []
        self.__parse()

    # property_values
    def __parse(self):
        options = Property_value.query.filter_by(prop_id=self.prop_id).order_by(desc(Property_value.option_value)).all()
        self.property_values = [self.__map_to_option(option) for option in options]

    def __map_to_option(self,option):
        return dict(
            option_value=option.option_value,
            option_name=option.option_name
        )


class LabelTaskDetailCollection:

    def __init__(self):
        self.task_id = ''
        self.task_detail_id = ''
        self.photo_path = ''
        self.props = []

    def fill(self,task_id, task_detail_id, url, prop_ids):
        self.photo_path = url
        self.task_id=task_id
        self.task_detail_id = task_detail_id
        # 查询出所有的属性
        prop_ids = Property.query.filter(Property.id.in_(prop_ids)).all()

        self.props = [LabelTaskDetailViewModel(prop) for prop in prop_ids]