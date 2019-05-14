# _*_ coding:utf-8 _*_
import math
import random

from app.models.task import Task
from app.models.task_details import Task_details
from .blue_print import web

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
    yesterday_time = today_time-86400

    # 假数据
    today_time = 1557504000
    yesterday_time = 1557417600

    # 查询所有未完成的任务
    tasks = Task().check_get_undone_task()
    for task in tasks:
        users = Task_details().get_users(yesterday_time, today_time,task)
        print('任务名字为：',task.task_name)
        for user_tuple in users:
            user = user_tuple[0]
            print('user：', user,end=';')
            task_details = Task_details().get_uncheck_task_details(yesterday_time, today_time, task, user)
            count = len(task_details)
            print('完成的总数为：',count,end=';')

            if count:
                # 抽检率
                sampling_rate = task.source.label_type.sampling_rate
                sampling_rate = 0.1
                print('抽检率为：',sampling_rate,end=';')
                # 抽检张数

                check_count = math.ceil(count * sampling_rate)
                print('抽检数量为：',check_count)
            check_tasks = []
            # 随机到抽检的张数
            for i in range(check_count):
                pass
                randint = random.randint(1, count) - 1
                # print(len(task_details),'  ',randint)
                check_tasks.append(task_details[randint])
                task_details.remove(task_details[randint])
                count -= 1

            # 将随机出来的task_details 生成质检,存到两个表中
            check_tasks

    return "hello"