# _*_ coding:utf-8 _*_
import json
import time

from flask import request

from app.models.base import db
from app.models.rework import Rework
from app.models.task_details import Task_details
from app.models.task_details_cut import Task_details_cut
from app.view_models.labeler_task import LabelTaskDetailCollection, FramesCollection
from app.view_models.rework import ReworkCollection
from app.models.check_data_info import Check_data_info
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/5/23 14:42'


@web.route('/rework_list', methods=['GET', 'POST'])
def rework_list():
    if request.data:
        form = json.loads(request.data)
    else:
        form = {'nickname': 'wangwei', 'group_id': 2}
    user = form.get('nickname')
    rework_datas = Rework().get_rework_data(user)

    rework = ReworkCollection()
    rework.fill(rework_datas)
    return json.dumps(rework, default=lambda o: o.__dict__)


@web.route('/rework_details', methods=['POST'])
def rework_details():
    """
    返工请求新的数据
    :return:
    """

    if request.data:
        form = json.loads(request.data)

    else:
        form = {'rework_id': 1, 'task_id': 14, 'date': '2019-05-22', 'label_user': 'wangwei',
                'detail_type': 1, 'task_detail_id': '9392'}

    task_id = form.get('task_id')
    label_user = form.get('label_user')
    detail_type = form.get('detail_type')
    rework_id = form.get('rework_id')
    date = form.get('date')
    time_array = time.strptime(date, '%Y-%m-%d')
    start_time = time.mktime(time_array)
    task_details_id = form.get('task_detail_id')
    # end_time = start_time+86400
    if detail_type == 1:
        rework_data = Task_details().get_rework_data(task_id, start_time, label_user)

        if rework_data is None:
            # 将状态改为1
            with db.auto_commit():
                rework_info = Rework().query.filter_by(id=rework_id).first()
                rework_info.status = 1

            return json.dumps({'msg': '该任务已完成', 'status': 666})
        else:
            # 返工点击新的一张时默认修改为已完成
            rework_data.is_complete = 1
    if detail_type == 2:
        rework_data = Task_details().get_last_rework_data(task_id, start_time, label_user, task_details_id)
        if rework_data is None:
            return json.dumps({'msg': '到头了'})

    if detail_type == 3:
        rework_data = Task_details().get_next_rework_data(task_id, start_time, label_user, task_details_id)
        if rework_data is None:
            return json.dumps({'msg': '到头了'})

    # 根据new_quality_data.task_details获取数据详情
    task_detail_id = rework_data.id
    # 判断是否已经质检过，如果是质检过的数据，则在返回数据之前就将完成状态改为1
    if rework_data.quality_lock == 1:
        with db.auto_commit():
            rework_data.is_complete = 1
    url = rework_data.photo_path
    if ':45982' in url:
        url = 'http://192.168.0.196:8282' + str(url).split(':45982')[-1]

    if form.get('label_type') == 2:
        frames = Task_details_cut().get_frames(task_detail_id)
        frames_collection = FramesCollection()
        check_data_info_id = ''
        frames_collection.fill(task_id, task_detail_id, url, detail_type, check_data_info_id, frames)
        return json.dumps(frames_collection, default=lambda o: o.__dict__)
    else:

        prop_ids = rework_data.task.prop_ids
        tuple_prop_ids = eval(prop_ids)
        if type(tuple_prop_ids) is int:
            prop_ids = [tuple_prop_ids]
        else:
            prop_ids = list(tuple_prop_ids)

        # 增加返回该条数据对错
        result_status = Check_data_info().get_result_status(task_detail_id)

        label_detail = LabelTaskDetailCollection()
        mongo_con = None
        is_doubt = rework_data.is_doubt
        label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, rework_data.id, mongo_con, result_status, is_doubt)
        return json.dumps(label_detail, default=lambda o: o.__dict__)
