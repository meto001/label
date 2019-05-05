# _*_ coding:utf-8 _*_
import time

from flask import request, json
from flask_login import login_required
from sqlalchemy import desc

from app import db
from app.models.property import Property
from app.models.source import Source
from app.models.task import Task
from app.models.task_details import Task_details
from app.models.task_details_value import Task_details_value
from app.view_models.labeler_task import LabelTaskViewModel, LabelTaskCollection, LabelTaskDetailViewModel, \
    LabelTaskDetailCollection
from app.view_models.task import TaskCollection, SourcesAndPorps
from .blue_print import web
from app.libs.img_stream import return_img_stream
__author__ = 'meto'
__date__ = '2019/3/25 17:50'


@web.route('/add_task', methods=['GET', 'POST'])
# @login_required
def add_task():
    # 判断如果是get方法，则返回对应类型的sources和props
    if request.method == 'GET':
        form = request.args.get('label_type_id')
        props = Property.query.filter_by(label_type_id=form).order_by(
            desc(Property.id)).all()
        sources = Source.query.filter_by(label_type_id=form).order_by(
            desc(Source.id)).all()
        sources_and_props = SourcesAndPorps(sources, props, form)

        return json.dumps(sources_and_props, default=lambda o: o.__dict__)
    else:
        # form = {'task_name': '新建1个任务', 'difficult_num': 0.2, 'source_id': 2, 'prop_ids': '12,13,14,15,16'}
        form = json.loads(request.data)
        # 向task表中插入数据
        try:
            with db.auto_commit():
                task = Task()
                form['is_complete'] = 0
                task.set_attrs(form)
                db.session.add(task)
            urls = task.get_urls(form.get('source_id'))
            # print(urls)
            with db.auto_commit():
                for url in urls:
                    task_details = Task_details()
                    form['task_id'] = task.id
                    form['photo_path'] = url.image_url
                    task_details.set_attrs(form)
                    db.session.add(task_details)
        except Exception as e:
            return json.dumps({'status': 'error'})
        return json.dumps({'status': 'success'})


@web.route('/task/admin', methods=['GET', 'POST'])
def admin_task():
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    tasks = Task.get_task(page, rows)
    task = TaskCollection()
    all_task_count = Task.get_task_count()
    task.fill(all_task_count, tasks)

    return json.dumps(task, default=lambda o: o.__dict__)


@web.route('/task/labeler', methods=['GET', 'POST'])
def labeler_task():
    """
    展示当前用户任务列表
    :return:
    """
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    user = request.args.get('nickname')

    # 任务数量
    tasks = Task.get_undone_task(page, rows)
    undone_task_count = Task.get_undone_task_count()
    labeler_task = LabelTaskCollection()
    labeler_task.fill(undone_task_count, tasks, user)

    # task.get('already_count') =Ta a
    # labeltaskviewmodel = LabelTaskViewModel()

    # 此处还差已完成数量、当前用户标注量、当前用户框数三个信息。

    return json.dumps(labeler_task, default=lambda o: o.__dict__)


@web.route('/task/show_task_detail', methods=['GET', 'POST'])
def show_task_detail():
    # type类型暂时定为是下一张还是上一张
    # form = {'nickname': 'meto', 'task_id': 4, 'type': 1}
    # 点击开始标注 接收一条已被该用户锁定或未标注的数据
    form = json.loads(request.data)
    user = form.get('nickname')
    task_id = form.get('task_id')
    # 查询是否有锁定数据
    new_data = Task_details().get_has_locks(user, task_id)
    # 如果没有锁定数据
    if new_data is None:
        new_data = Task_details().get_new_data(task_id)
    if new_data:
        task_detail_id = new_data.id
        url = new_data.photo_path

        url = return_img_stream(url)

        prop_ids = new_data.task.prop_ids
        tuple_prop_ids = eval(prop_ids)
        if type(tuple_prop_ids) is int:
            prop_ids = [tuple_prop_ids]
        else:
            prop_ids = list(tuple_prop_ids)
        label_detail = LabelTaskDetailCollection()
        label_detail.fill(task_id, task_detail_id, url, prop_ids)

        # 更新数据，将该条数据锁定
        with db.auto_commit():
            new_data.locks = 1
            new_data.operate_user = user
        return json.dumps(label_detail, default=lambda o: o.__dict__)
    else:
        return json.dumps({'status':'该任务已结束'})

@web.route('/task/save_data', methods=['POST'])
def save_data():
    pass

    # 如果prop_type=2的话，则prop_option_id 值为坐标值
    form = {'create_user': 'meto',
            'photo_path': 'C:/Users/Administrator/Pictures/Saved Pictures/微信图片_20180920160854.jpg',
            'task_id': 4, 'task_detail_id': 6320,
            'props': [{'prop_id': 11, 'prop_option_value': 3, 'prop_type': 1},
                      {'prop_id': 13, 'prop_option_value': 2, 'prop_type': 2}]}

    props = form.get('props')
    for prop in props:
        print(prop)
        data = {}
        with db.auto_commit():
            task_details_value = Task_details_value()
            data['photo_path'] = form.get('photo_path')
            data['task_id'] = form.get('task_id')
            data['task_detail_id'] = form.get('task_detail_id')
            data['create_user'] = form.get('create_user')
            data['prop_id'] = prop.get('prop_id')
            data['prop_option_value'] = prop.get('prop_option_value')
            data['prop_type'] = prop.get('prop_type')
            task_details_value.set_attrs(data)
            db.session.add(task_details_value)

    with db.auto_commit():
        task_detail = Task_details().query.filter_by(id=form.get('task_detail_id')).first()
        task_detail.locks = 0
        task_detail.is_complete = 1
        task_detail.operate_create_time = time.time()
    return json.dumps({'status': 'success'})
