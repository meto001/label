# _*_ coding:utf-8 _*_
import json

from app.models.property import Property
from app.models.property_value import Property_value
from app.models.task_details import Task_details
from app.models.task_details_value import Task_details_value

__author__ = 'meto'
__date__ = '2019/4/25 17:09'


class LabelTaskViewModel:

    def __init__(self, task, completed_count, my_label_count, my_today_label_count, be_left_doubt_count):
        self.task_id = task.id
        self.task_name = task.task_name
        self.label_type = task.source.label_type.name
        # 总量
        self.all_count = task.source.count

        # 该任务已完成数量
        self.completed_count = completed_count

        # 该用户已完成数量
        self.my_label_count = my_label_count

        self.my_today_label_count = my_today_label_count

        self.be_left_doubt_count = be_left_doubt_count
        # 用户已完成框数（标注不需要）
        self.my_frame_count = ''


class LabelTaskCollection:

    def __init__(self):
        self.total = 0
        self.tasks = []
        # 是否有返工数据
        self.rework_data =False

    def fill(self, total, tasks, user, today_start_time, rework_data):
        self.total = total
        self.rework_data = rework_data
        for task in tasks:
            # print(task.id)
            # 已经完成的数量
            task_detail = Task_details()
            completed_count = task_detail.get_already_count(task.id)
            my_label_count = task_detail.get_user_already_count(task.id, user)
            my_today_label_count = task_detail.get_user_today_count(task.id, user, today_start_time)
            be_left_doubt_count = task_detail.get_be_left_doubt_count(task.id, user)
            self.tasks.append(LabelTaskViewModel(task, completed_count, my_label_count, my_today_label_count, be_left_doubt_count))


class LabelTaskDetailViewModel:

    def __init__(self, prop, task_detail_id, detail_type, mongo_con):
        self.prop_type = prop.prop_type
        self.prop_id = prop.id
        self.prop_name = prop.prop_name

        # 如果是新数据，此值为空，如果是查询历史数据，使用此值

        # 预处理修改这里，将里面的值进行替换
        # mongo_con[task_detail_id][prop.id]
        if mongo_con:
            try:
                self.prop_option_value = mongo_con[str(task_detail_id)][str(prop.id)]
                self.prop_option_value_final = mongo_con[str(task_detail_id)][str(prop.id)]
            except KeyError as e:
                # print(e)
                if self.prop_type == 5 or self.prop_type == 6:
                    self.prop_option_value = []
                    self.prop_option_value_final = []
                elif self.prop_type == 2:
                    self.prop_option_value = ''
                    self.prop_option_value_final = ''
                else:
                    self.prop_option_value = 0
                    self.prop_option_value_final = 0

        elif self.prop_type == 5 or self.prop_type == 6:
            self.prop_option_value = []
            self.prop_option_value_final = []
        elif self.prop_type == 2:
            self.prop_option_value = ''
            self.prop_option_value_final = ''
        else:
            self.prop_option_value = 0
            self.prop_option_value_final = 0
        self.property_values = []
        if self.prop_type == 5:
            self.right_status = []
        self.__parse(task_detail_id, detail_type)

    # property_values
    def __parse(self, task_detail_id, detail_type):
        # task_detail_values = Task_details_value()
        # if detail_type == 2 or detail_type == 3:
        prop_option_value = Task_details_value().query.filter_by(prop_id=self.prop_id,
                                                                 task_detail_id=task_detail_id).first()
        options = Property_value.query.filter_by(prop_id=self.prop_id).order_by(Property_value.option_value).all()
        self.property_values = [self.__map_to_option(option) for option in options]
        if prop_option_value:
            # if self.prop_type == 4:
            #     self.prop_option_value = list(prop_option_value.prop_option_value)
            #     self.prop_option_value_final = list(prop_option_value.prop_option_value_final)
            # else:
            # 直接返回数组
            if prop_option_value.prop_type == 5 or prop_option_value.prop_type == 6 :
                self.prop_option_value = json.loads(prop_option_value.prop_option_value)
                self.prop_option_value_final = json.loads(prop_option_value.prop_option_value_final)
            else:
                self.prop_option_value = prop_option_value.prop_option_value
                self.prop_option_value_final = prop_option_value.prop_option_value_final

            if prop_option_value.prop_type == 5:
                # 获取所有的选项值
                all_index = []
                for op in options:
                    all_index.append(op.option_value)
                self.right_status = [None] * len(self.property_values)
                for value in self.prop_option_value:
                    if value not in self.prop_option_value_final:
                        v = all_index.index(value)
                        self.right_status[v] = 'red'
                for value in self.prop_option_value_final:
                    if value not in self.prop_option_value:
                        v = all_index.index(value)
                        self.right_status[v] = 'red'


        options = Property_value.query.filter_by(prop_id=self.prop_id).order_by(Property_value.option_value).all()
        self.property_values = [self.__map_to_option(option) for option in options]




    def __map_to_option(self, option):
        return dict(
            option_value=option.option_value,
            option_name=option.option_name
        )


class LabelTaskDetailCollection:

    def __init__(self):
        self.task_id = ''
        self.task_detail_id = ''
        self.photo_path = ''
        self.quality_lock = ''
        self.quality_inspection = ''
        self.check_data_info_id = ''
        self.props = []
        self.result_status = ''
        self.detail_type = ''
        self.is_doubt = ''

    def fill(self, task_id, task_detail_id, url, prop_ids, detail_type, check_data_info_id, mongo_con, result_status, is_doubt):
        self.photo_path = url
        self.task_id = task_id
        self.task_detail_id = task_detail_id
        self.result_status = result_status
        self.detail_type = detail_type
        self.is_doubt = is_doubt
        # 查询出所有的属性
        # prop_ids = Property.query.filter(Property.id.in_(prop_ids)).all()
        # prop_ids = [16,12]
        prop_ids = Property.query.filter(Property.id.in_(prop_ids)).order_by(Property.order).all()
        task_details = Task_details().query.filter_by(id=task_detail_id).first()
        #.order_by( asc(Task_details.id)).first()
        self.quality_lock = task_details.quality_lock
        self.quality_inspection = task_details.quality_inspection
        self.check_data_info_id = check_data_info_id
        self.props = [LabelTaskDetailViewModel(prop, task_detail_id, detail_type, mongo_con) for prop in prop_ids]


class FramesViewModel:
    def __init__(self, frame):
        pass
        self.graph_index = frame.graph_index
        self.split_type = frame.split_type
        self.pic_type = frame.pic_type
        self.coordinate = frame.coordinate
        self.final_coordinate = frame.final_coordinate


class FramesCollection:

    def __init__(self):
        self.task_id = ''
        self.task_detail_id = ''
        self.photo_path = ''
        self.quality_lock = ''
        self.quality_inspection = ''
        self.check_data_info_id = ''
        self.frames = []

    def fill(self, task_id, task_detail_id, url, detail_type, check_data_info_id, frames):
        self.photo_path = url
        self.task_id = task_id
        self.task_detail_id = task_detail_id
        self.detail_type = detail_type
        task_details = Task_details().query.filter_by(id=task_detail_id).first()
        self.quality_lock = task_details.quality_lock
        self.quality_inspection = task_details.quality_inspection
        self.check_data_info_id = check_data_info_id
        self.frames = [FramesViewModel(frame) for frame in frames]


class PreprocessingCollection:

    def fill(self, details, task_id):
        d = {}
        for detail in details:
            # 取到path，然后通过path和task_id去mysql中查询到task_details_id,将task_details_id作为键保存到mongodb中
            path = detail['path']
            task_detail = Task_details.query.filter_by(task_id=task_id, photo_path=path).first()

        # 插入到mongodb中，这里需要将detail值做优化，只保存里面的prop_id和prop_value,prop_id作为键，prop_value作为值
            d1 ={}
            for prop in detail['props']:
                key1 = prop['prop_id']
                value1 = prop['prop_value']

                d1[str(key1)] = value1
            d[str(task_detail.id)] =d1

        # print(d1)
        return d