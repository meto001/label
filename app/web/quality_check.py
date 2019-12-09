# _*_ coding:utf-8 _*_
import json
import math
import random
from datetime import datetime
from flask import request

from app import db
from app import scheduler
from app.models.check_data_info import Check_data_info
from app.models.check_task import Check_task
from app.models.check_user import Check_user
from app.models.rework import Rework
from app.models.task import Task
from app.models.task_details import Task_details
from app.models.task_details_cut import Task_details_cut
from app.models.task_details_value import Task_details_value
from app.view_models.check_task import CheckTaskCollection, CheckUserCollection
from app.view_models.labeler_task import LabelTaskDetailCollection, FramesCollection
from app.libs.error_code import Success
from app.libs.make_data import check_modify_data
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/5/13 10:46'

import time


# 手动生成质检
# @web.route('generate_quality_check', methods=['GET','POST'])
# def generate_quality_check():
#     """
#         前端传过来一个date日期 例如：20190530
#         得出该日期起始和结束的时间戳
#         进行两个判断，是否是今天，如果不是今天，正常执行，

#     :return:
#     """
#     pass
#

# 生成质检，可自动可手动
@web.route('/generate_quality_check', methods=['GET', 'POST'])
def auto_generate_quality_check():
    """
        前端传过来一个date日期 例如：20190530
        得出该日期起始和结束的时间戳
        进行两个判断，是否是今天，如果不是今天，正常执行，
        如果是今天，得到今天做过的所有数据，得到tasks，找到已完成的tasks，进行质检，其他忽略

    :return:
    """

    if request:
        if request.data:
            form = json.loads(request.data)
            date = form.get('date')
            time_array = time.strptime(date, '%Y-%m-%d')
            day_start_time = time.mktime(time_array)
            day_end_time = day_start_time + 86400

    else:

        # 当前时间
        # now_time = int(time.time())
        # 今天凌晨的时间戳,以下两种方式均可获得
        # day_end_time = now_time - (now_time- time.timezone)%86400
        day_end_time = int(datetime.timestamp(datetime.strptime(datetime.now().strftime('%Y%m%d'), '%Y%m%d')))
        print('今天凌晨的时间戳为%s'%str(day_end_time))
        # 昨天凌晨的时间戳
        day_start_time = day_end_time - 86400

    # 假数据
    # today_time = 1557504000
    # yesterday_time = 1557417600

    # 查询所有未完成的任务
    with scheduler.app.app_context():

        # 判断是否有返工任务完成，有的话生成质检
        rerowk_datas = Rework.query.filter_by(status=1, quality_inspection=0).all()
        if rerowk_datas:
            for rerowk_data in rerowk_datas:
                with db.auto_commit():
                    check_task = Check_task()
                    data = {}
                    date = rerowk_data.rework_date
                    data['check_task_name'] = date + '返工质检任务'
                    check_task.set_attrs(data)
                    db.session.add(check_task)
                    time_array = time.strptime(date, '%Y-%m-%d')
                    start_time = time.mktime(time_array)
                    # 改为已生成质检
                    rerowk_data.quality_inspection = 1
                task = rerowk_data.task
                task_id = task.id
                label_user = rerowk_data.user
                task_details = Task_details().get_rework_check_details(start_time, task_id, label_user)
                count = len(task_details)
                print('完成的总数为：', count, end=';')

                if count:
                    # 将任务详情改为已生成质检状态  测试时暂时屏蔽
                    with db.auto_commit():
                        for task_detail in task_details:
                            task_detail.quality_inspection = 1
                    # 抽检率
                    sampling_rate = task.source.label_type.sampling_rate
                    # sampling_rate = 0.1
                    print('抽检率为：', sampling_rate, end=';')
                    # 抽检张数

                    check_count = math.ceil(count * sampling_rate)
                    print('抽检数量为：', check_count)

                    # 保存信息到check_user表中
                    with db.auto_commit():
                        check_user = Check_user()
                        data = {}
                        data['user'] = label_user
                        data['task_id'] = task.id
                        data['check_num'] = check_count
                        data['total_num'] = count
                        data['check_task_id'] = check_task.id
                        data['check_date'] = date
                        check_user.set_attrs(data)
                        db.session.add(check_user)

                    check_tasks = []
                    # 随机到抽检的张数
                    for i in range(check_count):
                        pass
                        randint = random.randint(1, count) - 1
                        # print(len(task_details),'  ',randint)
                        check_tasks.append(task_details[randint])
                        task_details.remove(task_details[randint])
                        count -= 1

                    # 将随机出来的task_details 生成质检,存到check_data_info表中
                    with db.auto_commit():
                        for one_check_task in check_tasks:
                            check_data_info = Check_data_info()
                            data = {}
                            data['check_user_id'] = check_user.id
                            data['task_details_id'] = one_check_task.id
                            data['task_id'] = task.id
                            data['is_complete'] = 0
                            # 将task_details表中该条数据锁定，不允许标注员修改
                            one_check_task.quality_lock = 1

                            check_data_info.set_attrs(data)
                            db.session.add(check_data_info)

        # 判断是否有新数据
        has_new_data = Task_details().is_have_new_data(day_start_time, day_end_time)

        if has_new_data:

            # 判断是否是今天，如果不是今天，执行后面的语句，如果是今天,只生成已完成的任务
            # 此处逻辑6.3日编写
            now_time1 = int(time.time())
            if day_start_time < now_time1 < day_start_time + 86400:
                # 查找task_details中今天操作已完成的tasks，将其返回
                tasks = Task_details.get_already_task(day_start_time)
            else:
                # 如果不是今天，则查找未完成的
                tasks = Task().check_get_undone_task()
            with db.auto_commit():
                check_task = Check_task()
                data = {}
                timeArray = time.localtime(day_start_time)
                timeData = time.strftime('%Y-%m-%d', timeArray)

                data['check_task_name'] = timeData + '质检任务'
                check_task.set_attrs(data)
                db.session.add(check_task)

            for task in tasks:
                users = Task_details().get_users(day_start_time, day_end_time, task)
                print('任务名字为：', task.task_name, end=';')

                for user_tuple in users:
                    user = user_tuple[0]
                    print('user：', user, end=';')
                    task_details = Task_details().get_uncheck_user_task_details(day_start_time, day_end_time, task,
                                                                                user)
                    count = len(task_details)
                    print('完成的总数为：', count)

                    if count:
                        # 将昨天的任务改为已生成质检状态  测试时暂时屏蔽
                        with db.auto_commit():
                            for task_detail in task_details:
                                task_detail.quality_inspection = 1
                        # 抽检率
                        sampling_rate = task.source.label_type.sampling_rate
                        # sampling_rate = 0.1
                        print('抽检率为：', sampling_rate, end=';')
                        # 抽检张数

                        check_count = math.ceil(count * sampling_rate)
                        print('抽检数量为：', check_count)

                        # 保存信息到check_user表中
                        with db.auto_commit():
                            check_user = Check_user()
                            data = {}
                            data['user'] = user
                            data['task_id'] = task.id
                            data['check_num'] = check_count
                            data['total_num'] = count
                            data['check_task_id'] = check_task.id
                            data['check_date'] = timeData
                            check_user.set_attrs(data)
                            db.session.add(check_user)

                        check_tasks = []
                        # 随机到抽检的张数
                        for i in range(check_count):
                            pass
                            randint = random.randint(1, count) - 1
                            # print(len(task_details),'  ',randint)
                            check_tasks.append(task_details[randint])
                            task_details.remove(task_details[randint])
                            count -= 1

                        # 将随机出来的task_details 生成质检,存到check_data_info表中
                        with db.auto_commit():
                            for one_check_task in check_tasks:
                                check_data_info = Check_data_info()
                                data = {}
                                data['check_user_id'] = check_user.id
                                data['task_details_id'] = one_check_task.id
                                data['task_id'] = task.id
                                data['is_complete'] = 0
                                # 将task_details表中该条数据锁定，不允许标注员修改
                                one_check_task.quality_lock = 1

                                check_data_info.set_attrs(data)
                                db.session.add(check_data_info)

        else:
            print('今日无新数据生成')
            return Success(msg='今日无新数据生成')
    return Success(msg='生成新质检成功')


@web.route('/check_task', methods=['GET', 'POST'])
def check_task():
    form = {
        "quality_data": [
            {
                "date": "2019-05-14",
                "check_task_id": 6,
                "tasks": [
                    {
                        "task_name": "完整的标注测试",
                        "task_id": 8,
                        "task_type": "人脸质量标注"
                    },
                    {
                        "task_name": "文本框",
                        "task_id": 10,
                        "task_type": "人脸质量标注"
                    },
                    {
                        "task_name": "标记年龄",
                        "task_id": 11,
                        "task_type": "人脸质量标注"
                    }
                ]
            },
            {
                "date": "2019-05-15",
                "check_task_id": 7,
                "tasks": [
                    {
                        "task_name": "标记年龄",
                        "task_id": 11,
                        "task_type": "人脸质量标注"
                    }
                ]
            }
        ]
    }

    check_tasks = Check_task().get_check_date()

    check_collection = CheckTaskCollection()
    check_collection.fill(check_tasks)
    return json.dumps(check_collection, default=lambda o: o.__dict__)


@web.route('/check_task_user', methods=['GET', 'POST'])
def check_task_user():
    if request.data:
        form = json.loads(request.data)
    else:
        form = {'check_task_id': 17, 'task_id': 14}

    check_task_id = form.get('check_task_id')
    task_id = form.get('task_id')
    check_users = Check_user.get_check_user(check_task_id, task_id)
    data = {
        'users': [
            {'check_user': 'paopao', 'check_num': 100, 'total_num': 200, 'error_num': 2, 'already_num': 50},
            {'check_user': 'wangwei', 'check_num': 60, 'total_num': 300, 'error_num': 4, 'already_num': 40}
        ]
    }
    check_user_collection = CheckUserCollection()
    check_user_collection.fill(check_users, check_task_id)
    return json.dumps(check_user_collection, default=lambda o: o.__dict__)


@web.route('/check_task_details', methods=['GET', 'POST'])
def check_task_details():
    if request.data:
        form = json.loads(request.data)

    else:
        form = {'task_id': 14, 'date': '2019-05-22', 'check_task_id': 23, 'label_user': 'wangwei',
                'quality_user': 'huahua', 'check_data_info_type': 1, 'task_detail_id': '9392'}

    # 首先通过check_date、user、task_id查询check_user表得到该表的主键id,通过check_user_id查询check_data_info表，
    # 获取task_details_id.接下来的流程同标注流程，没有保存功能，可以修改，修改时修改task_details_value中的prop_option_value_final属性

    check_date = form.get('date')
    label_user = form.get('label_user')
    quality_user = form.get('quality_user')
    task_id = form.get('task_id')
    check_task_id = form.get('check_task_id')
    detail_type = form.get('detail_type')
    check_user_id = Check_user.get_id(check_date, label_user, task_id, check_task_id)
    quality_data = None

    if detail_type == 1:
        # 判断是否有锁定数据
        quality_data = Check_data_info().get_has_locks(check_user_id, quality_user)
        if quality_data is None:
            quality_data = Check_data_info().get_new_quality_data(check_user_id)
            if quality_data:
                # 更新数据，将该数据锁定
                with db.auto_commit():
                    quality_data.locks = 1
                    quality_data.quality_user = quality_user

            # 此处要判断任务是否已经完成，如果完成，计算正确率。判断是否返工,最后将任务状态改为已完成

            # 此处逻辑5.22日编写
            else:
                # 查询是否有未完成的数据
                undone = Check_data_info().check_is_complete(check_user_id)

                if undone is None:
                    # 计算正确率
                    # 正确的数量
                    true_count = Check_data_info().true_count(check_user_id)
                    all_check_count = Check_data_info().all_count(check_user_id)
                    # 正确率
                    correct_rate = round(true_count / all_check_count, 2)

                    # 得到任务的通过率
                    pass_rate = Check_data_info().get_pass_rate(check_user_id)
                    check_user = Check_user().query.filter_by(id=check_user_id).first()

                    with db.auto_commit():

                        # 将正确率写入到check_user表中
                        check_user.right_rate = correct_rate
                        # 计算该质检任务的开始和结束时间
                        date = check_user.check_date
                        time_array = time.strptime(date, '%Y-%m-%d')
                        start_time = time.mktime(time_array)
                        # end_time = start_time+86400

                        all_rework = Task_details.set_rework(start_time, task_id, check_user.user)
                        if correct_rate >= pass_rate:
                            check_user.status = 1
                            for rework in all_rework:
                                rework.quality_inspection = 2
                        else:
                            # 返工
                            check_user.status = 2
                            check_user.rework_status = 0
                            # 将此user此任务当天的所有数据全部返工

                            with db.auto_commit():
                                for rework in all_rework:
                                    if rework.quality_inspection != 2:
                                        rework.quality_inspection = -1
                                    rework.is_complete = -1
                                # 在rework表中写入一条数据
                                rework_table = Rework()
                                data1 = {}
                                data1['task_id'] = task_id
                                data1['rework_date'] = date
                                data1['user'] = label_user
                                data1['operate_time'] = time.time()
                                data1['all_count'] = check_user.total_num
                                data1['right_rate'] = correct_rate

                                rework_table.set_attrs(data1)
                                db.session.add(rework_table)
                    if check_user.status == 1:
                        return json.dumps({'msg': '该任务已完成,正确率为:%s,质检结果为:通过'%str(correct_rate), 'status': 666})
                    else:
                        return json.dumps({'msg': '该任务已完成,正确率为:%s,质检结果为:未通过' % str(correct_rate), 'status': 666})
                    # return Completed()

                else:
                    # 返回锁定数据的用户
                    # locks = Check_data_info().get_lock_user(check_user_id)
                    # lock_user = []
                    # for lock in locks:

                    lock_user = db.session.query(Check_data_info.quality_user).filter(
                        Check_data_info.check_user_id == check_user_id, Check_data_info.locks == 1).all()
                    pass

                    return json.dumps({'msg': '已没有新数据，请%s尽快将锁定数据完成' % (str(lock_user)), 'status': 666})

    elif detail_type == 2:
        task_detail_id = form.get('task_detail_id')
        quality_data = Check_data_info().get_last_quality_data(quality_user, task_detail_id, check_user_id)
        if quality_data is None:
            return json.dumps({'msg': '没有更多了'})

    elif detail_type == 3:
        task_detail_id = form.get('task_detail_id')
        quality_data = Check_data_info().get_next_quality_data(quality_user, task_detail_id, check_user_id)
        if quality_data is None:
            return json.dumps({'msg': '没有更多了'})

    # 根据new_quality_data.task_details获取数据详情
    task_details = quality_data.task_details
    task_detail_id = task_details.id
    url = task_details.photo_path

    if form.get('label_type') == 2:
        frames = Task_details_cut().get_frames(task_detail_id)
        frames_collection = FramesCollection()
        check_data_info_id = ''
        frames_collection.fill(task_id, task_detail_id, url, detail_type, check_data_info_id, frames)
        return json.dumps(frames_collection, default=lambda o: o.__dict__)
    else:
        prop_ids = task_details.task.prop_ids
        tuple_prop_ids = eval(prop_ids)
        if type(tuple_prop_ids) is int:
            prop_ids = [tuple_prop_ids]
        else:
            prop_ids = list(tuple_prop_ids)
        label_detail = LabelTaskDetailCollection()
        mongo_con = None
        label_detail.fill(task_id, task_detail_id, url, prop_ids, detail_type, quality_data.id, mongo_con)
        return json.dumps(label_detail, default=lambda o: o.__dict__)


@web.route('/modify_check_data', methods=['POST'])
def modify_check_data():
    if request.data:
        form = json.loads(request.data)
    else:
        form = {
            "photo_path": "http://192.168.3.211:82/static/明星库/港台/傅颖.jpg",
            "detail_type": 1,
            "create_user": "huahua",
            "group_id": 3,
            "result_status": 0,
            "task_detail_id": 10856,

            "error_count": "",
            "quality_lock": "",
            "check_data_info_id": "46",

            "task_id": 13,
            "props": [
                {
                    "prop_id": 11, "prop_name": "衣服", "prop_option_value": 1, "prop_option_value_final": 1,
                    "prop_type": 1,
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

    # 判断是否是质检员
    if form.get('group_id') != 3:
        return json.dumps({'msg': '用户类型错误'})
    task_detail_id = form.get('task_detail_id')

    with db.auto_commit():

        if form.get('label_type') == 2:
            frames = form.get('frames')
            for frame in frames:
                graph_index = frame.get('graph_index')
                task_details_cut = Task_details_cut().query.filter_by(graph_index=graph_index,
                                                                      task_detail_id=task_detail_id).first()
                # 如果是新增的，则task_details_cut为空
                if task_details_cut is None:
                    # 将该条数据插入
                    task_details_cut = Task_details_cut()
                    data = check_modify_data(form, frame)
                    task_details_cut.set_attrs(data)
                    db.session.add(task_details_cut)
                else:
                    if str(frame.get('final_coordinate')) != str(task_details_cut.final_coordinate):
                        task_details_cut.final_coordinate = frame.get('final_coordinate')

        else:
            props = form.get('props')
            for prop in props:
                prop_id = prop.get('prop_id')
                task_details_value = Task_details_value().query.filter_by(prop_id=prop_id,
                                                                          task_detail_id=task_detail_id).first()
                # 新增了一个属性，导致数据库里缺少值,task_details_value为NoneType，导致报错，临时增加一个try
                try:
                    if str(prop.get('prop_option_value_final')) != str(task_details_value.prop_option_value_final):
                        # 修改task_details_value表中的final值
                        if prop.get('prop_type') == 5:
                            prop_option_value_final = json.dumps(prop.get('prop_option_value'))
                        else:
                            prop_option_value_final = str(prop.get('prop_option_value_final'))
                        task_details_value.prop_option_value_final = prop_option_value_final
                except Exception as e:
                    print(e)

        # 修改check_data_info表里的锁定状态和质检结果
        check_data_info_id = form.get('check_data_info_id')
        check_data_info = Check_data_info().query.filter_by(id=check_data_info_id).first()
        check_data_info.result_status = form.get('result_status')
        check_data_info.error_count = form.get('error_count')
        check_data_info.locks = 0
        check_data_info.is_complete = 1
        check_data_info.quality_time = time.time()
        check_data_info.task_details.quality_inspection = 2
    return json.dumps({'status': 'success'})
