# _*_ coding:utf-8 _*_
import json
import math
import random

from flask import current_app, request

from app import db
from app import create_app
from app.models.task import Task
from app.models.task_details import Task_details
from models.check_data_info import Check_data_info
from models.check_task import Check_task
from models.check_user import Check_user
from view_models.check_task import CheckTaskCollection, CheckUserCollection
from .blue_print import web
from app import scheduler
__author__ = 'meto'
__date__ = '2019/5/13 10:46'

import time


# 自动生成昨天的质检
@web.route('/test3', methods=['GET', 'POST'])
def auto_generate_quality_check():
    # 当前时间
    now_time = int(time.time())
    # 今天凌晨的时间戳
    today_time = now_time - now_time % 86400 + time.timezone

    # 昨天凌晨的时间戳
    yesterday_time = today_time - 86400

    # 假数据
    # today_time = 1557504000
    # yesterday_time = 1557417600

    # 查询所有未完成的任务
    with scheduler.app.app_context():

        # 生成一个质检任务表
        has_new_data = Task_details().is_have_new_data(yesterday_time, today_time)
        # 判断是否有新数据
        if has_new_data:
            with db.auto_commit():
                check_task = Check_task()
                data = {}
                timeArray = time.localtime(yesterday_time)
                timeData = time.strftime('%Y-%m-%d', timeArray)

                data['check_task_name'] = timeData+'质检任务'
                check_task.set_attrs(data)
                db.session.add(check_task)

            tasks = Task().check_get_undone_task()
            for task in tasks:
                users = Task_details().get_users(yesterday_time, today_time, task)
                print('任务名字为：', task.task_name)

                for user_tuple in users:
                    user = user_tuple[0]
                    print('user：', user, end=';')
                    task_details = Task_details().get_uncheck_user_task_details(yesterday_time, today_time, task, user)
                    count = len(task_details)
                    print('完成的总数为：', count, end=';')

                    # 将昨天的任务改为已生成质检状态  测试时暂时屏蔽
                    with db.auto_commit():
                        for task_detail in task_details:
                            task_detail.quality_inspection = 1

                    if count:
                        # 抽检率
                        sampling_rate = task.source.label_type.sampling_rate
                        sampling_rate = 0.1
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
                            data['check_data'] = timeData
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

                                # 将task_details表中该条数据锁定，不允许标注员修改
                                one_check_task.quality_lock = 1

                                check_data_info.set_attrs(data)
                                db.session.add(check_data_info)

        else:
            print('今日无新数据生成')
    return "hello"


@web.route('/view_check_task',methods=['GET','POST'])
def view_check_task():
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
    return json.dumps(check_collection, default=lambda o:o.__dict__)

@web.route('/view_check_task_user',methods=['GET','POST'])
def view_check_task_user():
    if request.data:
        form = json.loads(request.data)
    else:
        form = {'check_task_id': 6, 'task_id':8}

    check_task_id =form.get('check_task_id')
    task_id = form.get('task_id')

    check_users = Check_user.get_check_user(check_task_id, task_id)
    data = {
        'users':[
            {'check_user': 'paopao', 'check_num': 100, 'total_num': 200, 'error_num': 2, 'already_num': 50},
            {'check_user': 'wangwei', 'check_num': 60, 'total_num': 300, 'error_num': 4, 'already_num': 40}
        ]
    }
    check_user_collection = CheckUserCollection()
    check_user_collection.fill(check_users)
    return json.dumps(check_user_collection,default=lambda o: o.__dict__)