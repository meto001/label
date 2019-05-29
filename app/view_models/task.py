# _*_ coding:utf-8 _*_
from app.models.task_details_value import Task_details_value
from app.models.property_value import Property_value

__author__ = 'meto'
__date__ = '2019/4/19 10:18'


class TaskViewModel:


    def __init__(self, task):
        self.task_id = task.id
        self.task_name = task.task_name
        self.label_type = task.source.label_type.name
        self.count = task.source.count
        self.create_time = task.create_time
        self.difficult_num = task.difficult_num
        if task.is_complete == 0:
            self.is_complete = '未完成'
        elif task.is_complete == 1:
            self.is_complete = '已完成'
        self.sampling_rate = task.source.label_type.sampling_rate


class TaskCollection:

    def __init__(self):
        self.total = 0
        self.tasks = []

    def fill(self,total, tasks):
        self.total = total
        self.tasks = [TaskViewModel(task) for task in tasks]


class SourcesAndPorps:


    def __init__(self, sources, props, label_type_id):
        self.label_type_id = label_type_id
        self.sources = []
        self.props = []
        self.__parse(sources, props)

    def __map_to_prop(self, prop):
        return dict(
            prop_id=prop.id,
            prop_name=prop.prop_name
        )

    def __map_to_source(self, source):
        return dict(
            source_id=source.id,
            source_name=source.source_name
        )

    def __parse(self, sources, props):
        self.sources = [self.__map_to_source(source) for source in sources]
        self.props = [self.__map_to_prop(prop) for prop in props]



class ExportTaskViewModel:
    def __init__(self, task_detail):
        self.path = ''
        self.props = []
        self.__parse(task_detail)

    def __parse(self,task_detail):
        # 处理数据
        self.path = task_detail.photo_path
        task_detail_id = task_detail.id
        detail_values = Task_details_value().query.filter_by(task_detail_id=task_detail_id).all()
        self.props = [self.__map_to_prop(detail_value) for detail_value in detail_values]

    def __map_to_prop(self, detail_value):
        # 属性值名字
        prop_value = Property_value().query.filter_by(prop_id=detail_value.prop_id, option_value=detail_value.prop_option_value_final).first()
        if prop_value:
            prop_value_name = prop_value.option_name
        else:
            prop_value_name = None

        return dict(
            prop_id=detail_value.prop_id,
            prop_name=detail_value.prop.prop_name,
            prop_type=detail_value.prop_type,
            prop_value=detail_value.prop_option_value_final,
            prop_value_name =prop_value_name
        )


class ExportTaskCollection:
    def __init__(self):
        self.task_id = ''
        self.task_name = ''
        self.details = []

    def fill(self,task_details):
        self.task_id = task_details[0].task_id
        self.task_name = task_details[0].task.task_name
        self.details=[ExportTaskViewModel(task_detail) for task_detail in task_details]