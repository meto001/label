# _*_ coding:utf-8 _*_
import json
import time

from flask import request
from app import db
from app.models.rework import Rework
from app.models.task_details import Task_details
from app.view_models.rework import ReworkCollection
from app.view_models.labeler_task import LabelTaskDetailCollection
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

    prop_ids = rework_data.task.prop_ids
    tuple_prop_ids = eval(prop_ids)
    if type(tuple_prop_ids) is int:
        prop_ids = [tuple_prop_ids]
    else:
        prop_ids = list(tuple_prop_ids)
    label_detail = LabelTaskDetailCollection()
    label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, rework_data.id)
    return json.dumps(label_detail, default=lambda o: o.__dict__)
