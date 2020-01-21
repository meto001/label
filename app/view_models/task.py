# _*_ coding:utf-8 _*_
import json

from app.models.task_details_value import Task_details_value
from app.models.property_value import Property_value
from app.models.task_details_cut import Task_details_cut
from app.models.property import Property

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

        # 裁剪
        if task_detail.task.source.label_type == 2:
            detail_frames = Task_details_cut().query.filter(Task_details_cut.task_detail_id==task_detail_id,
                                                            Task_details_cut.final_coordinate!=None).all()
            self.props = [self.__map_to_frame(detail_frame) for detail_frame in detail_frames]

        else:
            detail_values = Task_details_value().query.filter_by(task_detail_id=task_detail_id).all()
            self.props = [self.__map_to_prop(detail_value) for detail_value in detail_values]

    # 这里有两种选择，一是导出带属性名的，一是不带属性名，带属性名需要多去数据库中查询一次，以下为测试时间
    # 以3000数据为例，不带属性名用时2分钟，查询数据库3000次；带属性名用时4分钟，查询数据库3000*属性类型（次）
    def __map_to_prop(self, detail_value):
        # 属性值名字
        # prop_value = Property_value().query.filter_by(prop_id=detail_value.prop_id, option_value=detail_value.prop_option_value_final).first()
        # if prop_value:
        #     prop_value_name = prop_value.option_name
        # else:
        #     prop_value_name = None

        if detail_value.prop_type == 5:
            prop_values = json.loads(detail_value.prop_option_value_final)
            prop_value_name = None
        else:
            prop_values = detail_value.prop_option_value_final

        return dict(
            prop_id=detail_value.prop_id,
            prop_name=detail_value.prop.prop_name,
            prop_type=detail_value.prop_type,
            prop_value=prop_values,
            # prop_value_name =prop_value_name
        )

    def __map_to_frame(detail_frame):
        return dict(
            graph_index=detail_frame.graph_index,
            split_type=detail_frame.split_type,
            final_coordinate=detail_frame.final_coordinate,
            pic_type=detail_frame.pic_type
        )

        pass


class ExportProps:
    def __init__(self,prop):
        self.prop_type = prop.prop_type
        self.prop_id = prop.id
        self.prop_name = prop.prop_name
        self.property_values = []
        self.__parse()

    def __parse(self):
        options = Property_value.query.filter_by(prop_id=self.prop_id).order_by(Property_value.option_value).all()
        self.property_values = [self.__map_to_option(option) for option in options]

    def __map_to_option(self, option):
        return dict(
            option_value=option.option_value,
            option_name=option.option_name.split('.')[-1] # 此处是为了优化导出的json结构，以便算法同学解析
        )


class ExportTaskCollection:
    def __init__(self):
        self.task_id = ''
        self.task_name = ''
        self.props = []
        self.details = []

    def fill(self,task_details,prop_ids):
        self.task_id = task_details[0].task_id
        self.task_name = task_details[0].task.task_name
        self.details=[ExportTaskViewModel(task_detail) for task_detail in task_details]

        # 查询出所有的属性
        prop_ids = Property.query.filter(Property.id.in_(prop_ids)).all()
        self.props = [ExportProps(prop) for prop in prop_ids]

