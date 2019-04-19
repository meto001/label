# _*_ coding:utf-8 _*_
from flask import request, json
from flask_login import login_required

from app import db
from app.models.task import Task
from app.models.task_details import Task_details
from app.view_models.task import TaskCollection
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/3/25 17:50'


@web.route('/add_task',methods=['POST'])
# @login_required
def add_task():
    form = {'task_name': '新建1个任务', 'difficult_num': 0.2, 'source_id': 2, 'prop_ids': '12,13,14,15,16'}

    # 向task表中插入数据
    with db.auto_commit():
        task = Task()
        form['is_complete'] = 0
        task.set_attrs(form)
        db.session.add(task)

    urls = task.get_urls()
    print(urls)
    with db.auto_commit():
        for url in urls:
            task_details = Task_details()
            form['task_id'] = task.id
            form['photo_path'] = url.image_url
            task_details.set_attrs(form)
            db.session.add(task_details)

    return json.dumps({'status' : 'success'})


@web.route('/admin_task',methods=['GET','POST'])
def admin_task():
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    tasks = Task.get_task(page, rows)
    task = TaskCollection()
    task.fill(tasks)

    return json.dumps(task,default=lambda o:o.__dict__)
