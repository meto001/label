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
        self.tasks = []

    def fill(self, tasks):
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
