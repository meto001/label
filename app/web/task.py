# _*_ coding:utf-8 _*_
from flask_login import login_required

from app.models.task import Task
from app.models.task_details import Task_details
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/3/25 17:50'


@web.route('/add_task')
@login_required
def add_task():
    task = Task()
    task_details = Task_details()

    form = {'task_name':'新建个任务', 'difficult_num': 0.1, 'source_id':1, 'prop_ids':'12,13,14,15,16'}

    # 向task表中插入数据


    return 'This is task page'
