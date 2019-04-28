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
        self.total = 0
        self.tasks = []

    def fill(self,total, tasks, user):
        self.total = total
        for task in tasks:
            print(task.id)
            # 已经完成的数量
            task_detail = Task_details()
            already_count = task_detail.get_already_count(task.id)
            user_already_count = task_detail.get_user_already_count(task.id, user)

            self.tasks.append(LabelTaskViewModel(task,already_count,user_already_count))



class LabelTaskDetailViewModel:
    # 设计最底层的选项
    dict1 = {'photo_path': 'url', 'props': [
        {'prop_id': '12', 'prop_name': '衣服', 'property_values': [
            {'option_id': '1', 'option_name': '黄皮'}, {'option_id': '2', 'option_name': '黑皮'}, {'option_id': '3', 'option_name': '绿皮'}]},
        {'prop_id': '13', 'prop_name': '衣服', 'property_values': [
            {'option_id': '4', 'option_name': '穿衣服'}, {'option_id': '2', 'option_name': '没穿衣服'}, {'option_id': '3', 'option_name': '穿了衣服'}]}]}

    def __init__(self,url):

        self.photo_path = url
        self.props = []

    def __parse_two(self,prop_ids):
        prop_ids = list(eval(prop_ids))
        self.props = [self.__first_fill(prop) for prop in prop_ids]


    # 处理属性里面的选项
    def __first_fill(self,prop):
        self.prop_id = prop.id
        self.prop_name = prop.prop_name
        self.property_values = []
        self.__parse()

    def __parse(self,options):
       self.property_values = [self.__map_to_option(option) for option in options]

    def __map_to_option(self,option):
        return dict(
            option_id = option.id,
            option_name = option.name
        )