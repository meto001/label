# _*_ coding:utf-8 _*_
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
    def __init__(self,prop_values):
        self.path = ''
        self.props = []
        self.__parse(prop_values)

    def __parse(self,prop_values):
        self.props = [self.__map_to_prop(prop_value) for prop_value in prop_values]

    def __map_to_prop(self):
        return dict(
            prop_id='',
            prop_name='',
            prop_value='',
            prop_value_name=''
        )


class ExportTaskCollection:
    def __init__(self):
        self.task_id = ''
        self.task_name = ''
        self.details = []

    def fill(self,x1):
        self.details=[ExportTaskViewModel(x) for x in x1]