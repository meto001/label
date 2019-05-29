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
from app.view_models.task import TaskCollection, SourcesAndPorps, ExportTaskCollection
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
            print(e)
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
    # detail_type 1,新的一页;2,上一张;3,下一张
    if request.data:
        form = json.loads(request.data)
    else:
        form = {'nickname': 'meto', 'group_id': 2, 'task_id': 8, 'detail_type': 1, 'task_detail_id': 6320}
    # 点击开始标注 接收一条已被该用户锁定或未标注的数据

    user = form.get('nickname')
    task_id = form.get('task_id')
    detail_type = form.get('detail_type')

    # 新的一页
    if detail_type == 1:
        # 查询是否有锁定数据
        new_data = Task_details().get_has_locks(user, task_id)
        # 如果没有锁定数据
        if new_data is None:
            new_data = Task_details().get_new_data(task_id)
            if new_data:

                # 更新数据，将该条数据锁定
                with db.auto_commit():
                    new_data.locks = 1
                    new_data.operate_user = user
            else:
                # 查询是否有锁定数据
                label_undone_data = Task_details.check_is_complate(task_id)
                if label_undone_data is None:
                    # 将task表改为已完成
                    with db.auto_commit():
                        task = Task.query.filter_by(id=task_id).first()
                        task.is_complete = 1
                        # status=666 页面需要跳出
                    return json.dumps({'msg': '该任务已完成','status':666})
                else:
                    lock_user = db.session.query(Task_details.operate_user).filter(Task_details.task_id == task_id,
                                                                                   Task_details.locks == 1).all()
                    return json.dumps({'msg': '已没有新数据，请%s尽快将锁定数据完成' % (str(lock_user)), 'status':666})

                return json.dumps({'msg': '该任务已完成','status':666})

        task_detail_id = new_data.id
        url = new_data.photo_path

        # 此方法是直接返回图片流，暂不使用
        # url = return_img_stream(url)

        prop_ids = new_data.task.prop_ids
        tuple_prop_ids = eval(prop_ids)
        prop_option_value = 0
        if type(tuple_prop_ids) is int:
            prop_ids = [tuple_prop_ids]
        else:
            prop_ids = list(tuple_prop_ids)
        label_detail = LabelTaskDetailCollection()
        check_data_info_id = ''
        label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, check_data_info_id)

        return json.dumps(label_detail, default=lambda o: o.__dict__)

    elif detail_type == 2 or detail_type == 3:
        task_detail_id = form.get('task_detail_id')
        # 当前时间
        now_time = int(time.time())
        # 今天凌晨的时间戳
        today_time = now_time - now_time % 86400 + time.timezone
        # 上一页
        if detail_type == 2:
            # form = {'nickname': 'meto', 'task_id': 4, 'detail_type': 2, 'task_detail_id':7657}
            history_data = Task_details().get_last_data(user, task_id, task_detail_id, now_time, today_time)
            if history_data is None:
                return json.dumps({'msg': '已经是今天最早的数据了，想查询更多，请移步历史记录'})
        elif detail_type == 3:
            history_data = Task_details().get_next_data(user, task_id, task_detail_id, now_time, today_time)
            if history_data is None:
                return json.dumps({'msg': '已经是今天做的最后一条数据了，如果想做新的，请点击“新的一张”'})
        task_detail_id = history_data.id
        url = history_data.photo_path

        # 此方法是直接返回图片流，暂不使用
        # url = return_img_stream(url)

        prop_ids = history_data.task.prop_ids
        tuple_prop_ids = eval(prop_ids)
        prop_option_value = 0
        if type(tuple_prop_ids) is int:
            prop_ids = [tuple_prop_ids]
        else:
            prop_ids = list(tuple_prop_ids)
        label_detail = LabelTaskDetailCollection()
        check_data_info_id = ''
        label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, check_data_info_id)

        # select * from task_details WHERE  operate_user = 'meto' AND task_id = 4 and is_complete =1 and
        # operate_create_time >10000 and operate_create_time < 2556709299 and id < 6320 ORDER BY id DESC LIMIT 1
        return json.dumps(label_detail, default=lambda o: o.__dict__)

    else:
        return json.dumps({'msg': '传入的参数不正确，请重新输入'})
    # 下一页
    # elif detail_type == 3:
    #     task_detail_id = form.get('task_detail_id')
    # select * from task_details WHERE  operate_user = 'meto' AND task_id = 4 and is_complete =1 and
    # operate_create_time >10000 and operate_create_time < 2556709299 and id > 6320 ORDER BY id ASC LIMIT 1


@web.route('/task/save_data', methods=['POST'])
def save_data():
    # 如果prop_type=2的话，则prop_option_id 值为坐标值
    if request.data:
        form = json.loads(request.data)
    else:
        form = {
            "photo_path": "C:/Users/Administrator/Pictures/Saved Pictures/微信图片_20180920160858.jpg",
            "detail_type": 2,
            "create_user": "paopao",
            "group_id": 2,
            "quality_lock": "",
            "task_detail_id": 6320,
            "task_id": 4,
            "props": [
                {
                    "prop_id": 11, "prop_name": "衣服", "prop_option_value": 1, "prop_type": 1,
                    "property_values": [
                        {"option_name": "黄皮", "option_value": 1},
                        {"option_name": "黑皮", "option_value": 2},
                        {"option_name": "白皮", "option_value": 3}]
                },
                {"prop_id": 13, "prop_name": "肤色", "prop_option_value": 1, "prop_type": 1,
                 "property_values": [
                     {"option_name": "黑", "option_value": 1},
                     {"option_name": "黄", "option_value": 2}, ]
                 }], }

    props = form.get('props')
    # 判断是否已经保存，此处有bug，如果点击速度过快，仍会有一定概率重复保存
    if Task_details_value.query.filter_by(task_detail_id=form.get('task_detail_id'),
                                          prop_id=props[0].get('prop_id')).first():
        print('task_detail_id:', form.get('task_detail_id'), ' 已经存过了')
        return json.dumps({'mag': '不可重复存入'})
    print('task_detail_id:', form.get('task_detail_id'), ' 还没有存过')
    with db.auto_commit():
        for prop in props:
            # print(prop)
            data = {}
            task_details_value = Task_details_value()
            data['photo_path'] = form.get('photo_path')
            data['task_id'] = form.get('task_id')
            data['task_detail_id'] = form.get('task_detail_id')
            data['create_user'] = form.get('create_user')
            data['prop_id'] = prop.get('prop_id')
            data['prop_option_value'] = prop.get('prop_option_value')
            data['prop_option_value_final'] = prop.get('prop_option_value')
            data['prop_type'] = prop.get('prop_type')
            task_details_value.set_attrs(data)
            db.session.add(task_details_value)

    with db.auto_commit():
        task_detail = Task_details().query.filter_by(id=form.get('task_detail_id')).first()
        task_detail.locks = 0
        task_detail.is_complete = 1
        task_detail.operate_create_time = time.time()
        task_detail.operate_time = time.time()
    return json.dumps({'status': 'success'})


@web.route('/task/modify_data', methods=['POST'])
def modify_data():
    if request.data:
        form = json.loads(request.data)
    else:
        form = {
            "photo_path": "C:/Users/Administrator/Pictures/Saved Pictures/微信图片_20180920160858.jpg",
            "detail_type": 2,
            "create_user": "paopao",
            "group_id": 2,
            "task_detail_id": 6320,
            "quality_lock": "",
            "task_id": 4,
            "props": [
                {
                    "prop_id": 11, "prop_name": "衣服", "prop_option_value": 1, "prop_type": 1,
                    "property_values": [
                        {"option_name": "黄皮", "option_value": 1},
                        {"option_name": "黑皮", "option_value": 2},
                        {"option_name": "白皮", "option_value": 3}]
                },
                {"prop_id": 13, "prop_name": "肤色", "prop_option_value": 1, "prop_type": 1,
                 "property_values": [
                     {"option_name": "黑", "option_value": 1},
                     {"option_name": "黄", "option_value": 2}]
                 }], }

    # 修改时增加判断，quality_lock==1，并且是标注员，则不可以修改。此处在前端也要进行判断
    if form.get('quality_lock') == 1 and form.get('group_id') == 2:
        return json.dumps({'msg': '被质检员确认过的数据不可进行修改'})

    if form.get('detail_type') == 1:
        return json.dumps({'msg': '请点击新的一张进行保存，新数据不可使用此按钮保存'})

    task_detail_id = form.get('task_detail_id')

    # 判断是否已经生成过质检
    boolean = Task_details().is_check(task_detail_id)
    user = Task_details().query.filter_by(id=task_detail_id).first().operate_user
    if boolean:
        return json.dumps({'msg': '该数据已生成质检，无法修改'})
    elif user == form.get('create_user'):
        # 删除task_details_value里面的数据
        with db.auto_commit():
            task_details_value = Task_details_value()
            values = task_details_value.query.filter_by(task_detail_id=task_detail_id).all()
            for value in values:
                db.session.delete(value)
        # 新增数据
        props = form.get('props')
        with db.auto_commit():
            for prop in props:
                # print(prop)
                data = {}
                task_details_value = Task_details_value()
                data['photo_path'] = form.get('photo_path')
                data['task_id'] = form.get('task_id')
                data['task_detail_id'] = form.get('task_detail_id')
                data['create_user'] = form.get('create_user')
                data['prop_id'] = prop.get('prop_id')
                data['prop_option_value'] = prop.get('prop_option_value')
                data['prop_option_value_final'] = prop.get('prop_option_value')
                data['prop_type'] = prop.get('prop_type')
                task_details_value.set_attrs(data)
                db.session.add(task_details_value)
            task_detail = Task_details.query.filter_by(id=task_detail_id).first()
            task_detail.operate_time = time.time()
        return json.dumps({'status': 'success'})
    else:
        return json.dumps({'msg': '这不是您做的数据，无法进行修改！'})


@web.route('/task/export_data', methods=['POST'])
def export_data():

    # 导出数据
    if request.data:
        form = json.loads(request.data)
    else:
        form = {"task_id": 17}

    # 判断该任务所有数据quality_inspection是否都是质检完成状态
    task_id = form.get('task_id')
    quality_status = Task_details.get_quality_status(task_id)
    if quality_status:
        # 执行导出动作
        data = {"task_id": 16, "task_name": "1号任务",
                "details": [
            {
                "path": "http://192.168.3.211:82/static/1/安志杰.jpg",
                "props":
                    [
                        {
                            "prop_id": 18,
                            "prop_name": "衣服",
                            "prop_value": 0,
                            "prop_value_name": "未知"
                        },
                        {
                            "prop_id": 19,
                            "prop_name": "种族",
                            "prop_value": 1,
                            "prop_value_name": "汉族"
                        }
                    ]

            },
            {
                "path": "http://192.168.3.211:82/static/1/安志杰2.jpg",
                "props":
                    [
                        {
                            "prop_id": 18,
                            "prop_name": "衣服",
                            "prop_value": 0,
                            "prop_value_name": "未知"
                        },
                        {
                            "prop_id": 19,
                            "prop_name": "种族",
                            "prop_value": 1,
                            "prop_value_name": "汉族"
                        }
                    ]

            }
        ]}

        task_details = Task_details.get_task_all_data(task_id)

        export_task = ExportTaskCollection()
        export_task.fill(task_details)
        return json.dumps(export_task, default=lambda o: o.__dict__)

    else:
        return json.dumps({"msg": "该任务尚未完成所有流程，不可导出"})
    pass
