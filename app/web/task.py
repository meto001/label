# _*_ coding:utf-8 _*_
import os
import time
from queue import Queue

from flask import request, json
from sqlalchemy import desc

from app import dict1, mongo, redis_client
from app.libs.make_data import caijian_save_data, label_save_data, caijian_modify_data, label_modify_data
from app.models.base import db
from app.models.property import Property
from app.models.source import Source
from app.models.task import Task
from app.models.task_details import Task_details
from app.models.task_details_cut import Task_details_cut
from app.models.task_details_value import Task_details_value
from app.view_models.labeler_task import LabelTaskCollection, LabelTaskDetailCollection, FramesCollection, \
    PreprocessingCollection
from app.view_models.task import TaskCollection, SourcesAndPorps, ExportTaskCollection
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/3/25 17:50'


@web.route('/add_task', methods=['GET', 'POST'])
# @login_required
def add_task():
    """
    添加任务接口，get请求为获取对应类型的数据源和属性

    :return:
    """
    # 判断如果是get方法，则返回对应类型的sources和props
    if request.method == 'GET':
        form = request.args.get('label_type_id')
        props = Property.query.filter_by(label_type_id=form, status=1).order_by(
            desc(Property.id)).all()
        sources = Source.query.filter_by(label_type_id=form, status=1).order_by(
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
    """
    管理员任务界面
    :return:
    """
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
    标注员任务界面
    :return:
    """
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    user = request.args.get('nickname')
    if redis_client.get('task_list_%s_%s_%s' % (user, page, rows)):
        return redis_client.get('task_list_%s_%s_%s' % (user, page, rows))
    print('获取新的任务列表')
    # 任务数量
    tasks = Task.get_undone_task(page, rows)
    undone_task_count = Task.get_undone_task_count()
    labeler_task = LabelTaskCollection()
    now_time = int(time.time())
    today_start_time = now_time - (now_time - time.timezone) % 86400
    labeler_task.fill(undone_task_count, tasks, user, today_start_time)

    # task.get('already_count') =Ta a
    # labeltaskviewmodel = LabelTaskViewModel()

    # 此处还差已完成数量、当前用户标注量、当前用户框数三个信息。
    redis_client.set('task_list_%s_%s_%s' % (user, page, rows), json.dumps(labeler_task, default=lambda o: o.__dict__))
    return json.dumps(labeler_task, default=lambda o: o.__dict__)


@web.route('/task/refresh_task', methods=['GET'])
def refresh_task():
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    user = request.args.get('nickname')
    redis_client.delete('task_list_%s_%s_%s' % (user, page, rows))
    return json.dumps("删除成功")


@web.route('/task/show_task_detail', methods=['GET', 'POST'])
def show_task_detail():
    """
    任务详情界面，包括：新的一张，上一张，下一张。使用队列方式进行发放数据。如任务已完成，则修改任务状态。
    如果任务为预处理，并且是新的一张，则访问mongodb数据库查找数据并处理返回。
    :return:
    """
    # detail_type 1,新的一页;2,上一张;3,下一张;4.回到首页（今天的第一张）
    if request.data:
        form = json.loads(request.data)
    else:
        # 测试数据
        form = {"nickname": "paopao", "group_id": 2, "task_id": 4, "label_type": 1, "detail_type": 1,
                "task_detail_id": 4773, "is_doubt": 0}
    # 点击开始标注 接收一条已被该用户锁定或未标注的数据
    user = form.get('nickname')
    task_id = form.get('task_id')
    detail_type = form.get('detail_type')

    # 新的一页
    if detail_type == 1:

        # 判断是否为存疑数据
        if form.get("is_doubt") and int(form.get("is_doubt")) == 1:
            new_data = Task_details().get_has_doubt_locks(user, task_id)
            # 如果没有锁定的存疑数据，则查找一条新的存疑数据
            if new_data is None:
                new_data = Task_details().get_new_doubt_data(task_id, user)
                if new_data is None:
                    return json.dumps({'msg': '存疑数据已经做完，请退出'})
        else:

            # 查询是否有锁定数据
            new_data = Task_details().get_has_locks(user, task_id)
            # 如果没有锁定数据
            if new_data is None:
                # 如果没有锁定数据，判断字典里是否有该任务的队列，如果有，则获取一个task_detail_id，否则，新建队列，获取task_detail_id
                if redis_client.llen(task_id) == 0:
                    # 查询该任务下未完成的task_detail_id
                    undone_ids = Task_details().get_undone_ids(task_id)
                    for id in undone_ids:
                        redis_client.rpush(task_id, id)
                        print(id)
                if redis_client.llen(task_id):
                    task_detail_id = redis_client.lpop(task_id)
                    if task_detail_id:
                        task_detail_id = task_detail_id.decode()
                    print(task_id, ':', task_detail_id)
                else:
                    task_detail_id = None
                new_data = Task_details().get_new_data(task_id, task_detail_id)

                # 当队列中获取的值查不到时，循环进行查询，直到队列为空
                while new_data is None:
                    if redis_client.llen(task_id):
                        task_detail_id = redis_client.lpop(task_id)
                        print('已经消失了的记录:', task_detail_id)
                    if task_detail_id:
                        task_detail_id = task_detail_id.decode()
                    else:
                        break
                    new_data = Task_details().get_new_data(task_id, task_detail_id)
                if new_data:

                    # 更新数据，将该条数据锁定
                    with db.auto_commit():
                        new_data.locks = 1
                        new_data.operate_user = user
                else:
                    # 查询是否有锁定数据
                    label_undone_data = Task_details.check_is_complete(task_id)
                    if label_undone_data is None:
                        # 将task表改为已完成
                        with db.auto_commit():
                            task = Task.query.filter_by(id=task_id).first()
                            task.is_complete = 1
                            # status=666 页面需要跳出
                        return json.dumps({'msg': '该任务已完成', 'status': 666})
                    else:
                        lock_user = db.session.query(Task_details.operate_user).filter(Task_details.task_id == task_id,
                                                                                       Task_details.locks == 1).all()
                        return json.dumps({'msg': '已没有新数据，请%s尽快将锁定数据完成' % (str(lock_user)), 'status': 666})

                    return json.dumps({'msg': '该任务已完成', 'status': 666})

        task_detail_id = new_data.id

        # 在这里拿到id后，去mongodb中查询此id.获取数据后返回。
        url = new_data.photo_path
        # 这里增加临时解决方案，将旧的ip替换为新的ip
        # if '45982' in url:
        #     url = 'http://192.168.0.196:8282' + str(url).split(':45982')[-1]

        # 判断是裁剪类型
        if form.get('label_type') == 2:
            frames = Task_details_cut().get_frames(task_detail_id)
            frames_collection = FramesCollection()
            check_data_info_id = ''
            frames_collection.fill(task_id, task_detail_id, url, detail_type, check_data_info_id, frames)
            return json.dumps(frames_collection, default=lambda o: o.__dict__)

        else:

            # 查询task_details_value表中的值

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
            if new_data.task.is_preprocess == 1:
                col = mongo.db['%s' % str(task_id)]
                # 查询mongodb数据
                mongo_con = col.find_one({})
            else:
                mongo_con = None
            result_status = None
            is_doubt = new_data.is_doubt
            label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, check_data_info_id, mongo_con,
                              result_status, is_doubt)
            return json.dumps(label_detail, default=lambda o: o.__dict__)

    elif detail_type == 2 or detail_type == 3 or detail_type == 4 or detail_type == 5 :
        task_detail_id = form.get('task_detail_id')
        # print('请求上一张，当前task_detail_id为%s'%task_detail_id)
        # 当前时间
        now_time = int(time.time())
        # 今天凌晨的时间戳
        today_time = now_time - now_time % 86400 + time.timezone
        # 上一页
        if detail_type == 2:
            # form = {'nickname': 'meto', 'task_id': 4, 'detail_type': 2, 'task_detail_id':7657}
            # 判断是否为存疑数据
            if int(form.get("is_doubt")) == 1:
                history_data = Task_details().get_last_doubt_data(user, task_id, task_detail_id, now_time, today_time)
            else:
                history_data = Task_details().get_last_data(user, task_id, task_detail_id, now_time, today_time)
            if history_data is None:
                return json.dumps({'msg': '已经是今天最早的数据了，想查询更多，请移步历史记录'})
        elif detail_type == 3:
            # 判断是否为存疑数据
            if int(form.get('is_doubt')) == 1:
                history_data = Task_details().get_next_doubt_data(user, task_id, task_detail_id, now_time, today_time)
            else:
                history_data = Task_details().get_next_data(user, task_id, task_detail_id, now_time, today_time)
            if history_data is None:
                return json.dumps({'msg': '已经是今天做的最后一条数据了，如果想做新的，请点击“新的一张”'})
        elif detail_type == 4:
            if int(form.get('is_doubt')) == 1:
                return json.dumps({'msg': '存疑不支持跳转首页，如需支持，请联系开发人员'})
            else:
                history_data = Task_details().get_first_data(user, task_id, task_detail_id, now_time, today_time)
            if history_data is None:
                return json.dumps({'msg': '已经是今天最早的数据了，想查询更多，请移步历史记录'})
        elif detail_type == 5:
            page = form.get('page')
            if page:
                try:
                    page = int(page)
                except:
                    return json.dumps({'msg': '传入的参数不正确，请重新输入'})
                history_data = Task_details().get_quick_jump_data(task_id, user, page, today_time)
                if history_data is None:
                    return json.dumps({'msg': '传入的参数不正确，请重新输入'})
            else:
                return json.dumps({'msg': '传入的参数不正确，请重新输入'})
        task_detail_id = history_data.id
        # print('上一张的id为%s'%task_detail_id)
        url = history_data.photo_path
        # 这里增加临时解决方案，将旧的ip替换为新的ip
        if ':45982' in url:
            url = 'http://192.168.0.196:8282' + str(url).split(':45982')[-1]
        if form.get('label_type') == 2:
            frames = Task_details_cut().get_frames(task_detail_id)
            frames_collection = FramesCollection()
            check_data_info_id = ''
            frames_collection.fill(task_id, task_detail_id, url, detail_type, check_data_info_id, frames)
            return json.dumps(frames_collection, default=lambda o: o.__dict__)

        else:

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
            mongo_con = None
            result_status = None
            is_doubt = history_data.is_doubt
            label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, check_data_info_id, mongo_con,
                              result_status, is_doubt)

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
    """
    保存数据
    :return:
    """
    # 如果prop_type=2的话，则prop_option_id 值为坐标值
    if request.data:
        form = json.loads(request.data)
    else:
        # 标注json
        # form = {
        #     "photo_path": "C:/Users/Administrator/Pictures/Saved Pictures/微信图片_20180920160858.jpg",
        #     "detail_type": 2,
        #     "create_user": "paopao",
        #     "group_id": 2,
        #     "quality_lock": "",
        #     "task_detail_id": 6320,
        #     "task_id": 4,
        #     "props": [
        #         {
        #             "prop_id": 11, "prop_name": "衣服", "prop_option_value": 1, "prop_type": 1,
        #             "property_values": [
        #                 {"option_name": "黄皮", "option_value": 1},
        #                 {"option_name": "黑皮", "option_value": 2},
        #                 {"option_name": "白皮", "option_value": 3}]
        #         },
        #         {"prop_id": 13, "prop_name": "肤色", "prop_option_value": 1, "prop_type": 1,
        #          "property_values": [
        #              {"option_name": "黑", "option_value": 1},
        #              {"option_name": "黄", "option_value": 2}, ]
        #          }], }

        # 裁剪json
        form = {
            "photo_path": "C:/Users/Administrator/Pictures/Saved Pictures/微信图片_20180920160858.jpg",
            # 新增类型，判断类型为2
            "label_type": 2,
            "detail_type": 1,
            "create_user": "paopao",
            "group_id": 2,
            "quality_lock": "",
            "task_detail_id": 4773,
            "task_id": 15,
            "frames": [
                {
                    "graph_index": 0,
                    "split_type": 1,
                    "coordinate": "坐标值",
                    "final_coordinate": "坐标值",
                    "pic_type": 1

                }, {
                    "graph_index": 1,
                    "split_type": 1,
                    "coordinate": "坐标值",
                    "final_coordinate": "坐标值",
                    "pic_type": 1
                }
            ]
        }

    # 裁剪任务保存逻辑
    if form.get('label_type') == 2:
        frames = form.get('frames')
        if Task_details_cut.query.filter_by(task_detail_id=form.get('task_detail_id')).first():
            print('task_detail_id:', form.get('task_detail_id'), ' 已经存过了')
            return json.dumps({'msg': '不可重复存入'})
        print('task_detail_id:', form.get('task_detail_id'), ' 还没有存过')
        with db.auto_commit():
            for frame in frames:
                task_details_cut = Task_details_cut()
                data = caijian_save_data(form, frame)

                task_details_cut.set_attrs(data)
                db.session.add(task_details_cut)
    else:
        # 暂时等于1，前端还没有修改，当前端修改后将此处判断为1
        props = form.get('props')
        # 判断是否已经保存，此处有bug，如果点击速度过快，仍会有一定概率重复保存。
        # 通过前端增加loading解决了此问题
        if Task_details_value.query.filter_by(task_detail_id=form.get('task_detail_id'),
                                              prop_id=props[0].get('prop_id')).first():
            print('task_detail_id:', form.get('task_detail_id'), ' 已经存过了')
            return json.dumps({'msg': '不可重复存入'})
        print('task_detail_id:', form.get('task_detail_id'), ' 还没有存过')
        with db.auto_commit():
            for prop in props:
                task_details_value = Task_details_value()
                data = label_save_data(form, prop)
                task_details_value.set_attrs(data)
                db.session.add(task_details_value)

    with db.auto_commit():
        task_detail = Task_details().query.filter_by(id=form.get('task_detail_id')).first()
        task_detail.locks = 0
        # 增加存疑判断，如果doubt为1，则将doubt字段改为1，is_complete为0不变。
        if form.get('doubt') == 1:
            task_detail.is_doubt = 1
        else:
            task_detail.is_complete = 1
        task_detail.operate_create_time = time.time()
        task_detail.operate_time = time.time()

    return json.dumps({'status': 'success'})


@web.route('/task/modify_data', methods=['POST'])
def modify_data():
    """
    修改数据，
    :return:
    """
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
    sdata = Task_details().query.filter_by(id=task_detail_id).first()
    if sdata:
        user = sdata.operate_user

    if boolean:
        return json.dumps({'msg': '该数据已生成质检，无法修改'})
    elif user == form.get('create_user'):

        if form.get('label_type') == 2:
            with db.auto_commit():
                task_detail_cut = Task_details_cut()
                frames = task_detail_cut.query.filter_by(task_detail_id=task_detail_id)
                for frame in frames:
                    db.session.delete(frame)
            with db.auto_commit():
                for frame in frames:
                    task_details_cut = Task_details_cut()
                    data = caijian_modify_data(form, frame)
                    task_details_cut.set_attrs(data)
                    db.session.add(task_details_cut)


        else:
            # 暂时等于1，前端还没有修改，当前端修改后将此处判断为1
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
                    task_details_value = Task_details_value()
                    data = label_modify_data(form, prop)
                    task_details_value.set_attrs(data)
                    db.session.add(task_details_value)
        task_detail = Task_details.query.filter_by(id=task_detail_id).first()
        # 新增修改时将状态改为1，返工和存疑时使用
        with db.auto_commit():
            task_detail.is_complete = 1
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
    # 提前导出测试用代码
    # quality_status =1
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

        # 2019.11.20新增获取属性列表
        prop_ids = task_details[0].task.prop_ids
        tuple_prop_ids = eval(prop_ids)
        prop_option_value = 0
        print('正在获取tuple_prop_ids')
        if type(tuple_prop_ids) is int:
            prop_ids = [tuple_prop_ids]
        else:
            prop_ids = list(tuple_prop_ids)

        export_task = ExportTaskCollection()
        export_task.fill(task_details, prop_ids)

        # 将任务状态改为已导出，则自动质检时不再查询该任务 status=2 为已结束
        with db.auto_commit():
            task = Task().query.filter_by(id=task_id).first()
            task.status = 2
        # print(json.dumps(export_task, default=lambda o: o.__dict__))

        if os.path.exists('app/static/json') == 0:
            os.mkdir('app/static/json')

        with open('app/static/json/%s.exe' % task.task_name, 'w') as f:
            f.write(json.dumps(export_task, default=lambda o: o.__dict__))
        path = '/static/json/%s.exe' % task.task_name
        # return json.dumps(export_task, default=lambda o: o.__dict__)
        return json.dumps({'path': path})
    else:
        return json.dumps({"msg": "该任务尚未完成所有流程，不可导出"})


@web.route('/helloo')
# @cache.cached(timeout=6,key_prefix='meto')
def hello():
    # pao = redis_client.rpush(3,1,2,3,4,5,6)
    pao = redis_client.llen(37)
    print(pao)
    # redis_client.set('kill_total', 50)
    # name = 'hello redis 16'
    return 'yes'


@web.route('/queue_test')
def load():
    id = json.loads(request.data).get('id')
    # if q.empty():
    #     for i in range(10):
    #         q.put(i)
    # a = q.get()
    # print(q)
    # q = dict1.get('5')
    # if q.empty():
    #     print('5null')
    # else:
    #     print(q.get())
    #
    # q = dict1.get('3')
    # if q.empty():
    #     print('3null')
    # else:
    #     print(q.get())
    # return 'a'
    # id = '65333'
    if dict1.get(id) is None:
        q = Queue(10)
        print('none')
        for i in range(5):
            q.put(i)
        dict1[id] = q
    if dict1[id].empty() is False:
        print(id, '--', dict1[id].get())
    return 'success'


@web.route('/task/upload_mongodb', methods=['GET', 'POST'])
def preprocessing_upload_mongodb():
    file = request.files.get('file')
    json_file = file.read()
    con = json.loads(json_file)
    task_id = con['task_id']
    print(task_id)
    col = mongo.db['%s' % str(task_id)]

    # 插入到mongodb中，这里需要将detail值做优化，只保存里面的prop_id和prop_value,prop_id作为键，prop_value作为值

    preprocess = PreprocessingCollection()
    d1 = preprocess.fill(con['details'], task_id)
    # print(d1)
    # 保存格式：task_details_id:{prop_id:prop_value}
    res = col.insert_one(d1)

    # 在task表中增加一个字段，插入完成之后，将值改为1，
    with db.auto_commit():
        task = Task().query.filter_by(id=task_id).first()
        task.is_preprocess = 1
    # print('inserted_id:%s' % (res.inserted_id))
    # find_res = col.find_one({"_id": res.inserted_id})
    #
    # item = find_res['4593']
    # for k,v in item.items():
    #     print('%s:%s' % (k, v))
    # for k, v in item.items():
    #     print('%s:%s'%(k,v))
    return 'success'


