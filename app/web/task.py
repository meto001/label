# _*_ coding:utf-8 _*_
from flask import request, json
from flask_login import login_required
from sqlalchemy import desc

from app import db
from app.models.property import Property
from app.models.source import Source
from app.models.task import Task
from app.models.task_details import Task_details
from app.view_models.labeler_task import LabelTaskViewModel, LabelTaskCollection
from app.view_models.task import TaskCollection, SourcesAndPorps
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/3/25 17:50'


@web.route('/add_task',methods=['GET','POST'])
# @login_required
def add_task():

    # 判断如果是get方法，则返回对应类型的sources和props
    if request.method == 'GET':
        form = request.args.get('label_type_id')
        props = Property.query.filter_by(label_type_id=form).order_by(
            desc(Property.id)).all()
        sources = Source.query.filter_by(label_type_id=form).order_by(
            desc(Source.id)).all()
        sources_and_props = SourcesAndPorps(sources,props,form)

        return json.dumps(sources_and_props,default=lambda o:o.__dict__)
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


@web.route('/task/admin',methods=['GET','POST'])
def admin_task():

    page = request.args.get('page')
    rows = request.args.get('pagerows')
    tasks = Task.get_task(page, rows)
    task = TaskCollection()
    all_task_count = Task.get_task_count()
    task.fill(all_task_count, tasks)

    return json.dumps(task,default=lambda o:o.__dict__)


@web.route('/task/labeler',methods=['GET','POST'])
def labeler_task():

    """
    展示当前用户任务列表
    :return:
    """
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    user = request.args.get('user')

    # 任务数量
    tasks = Task.get_undone_task(page,rows)
    undone_task_count = Task.get_undone_task_count()
    labeler_task = LabelTaskCollection()
    labeler_task.fill(undone_task_count,tasks,user)

        # task.get('already_count') =Ta a
        # labeltaskviewmodel = LabelTaskViewModel()


    # 此处还差已完成数量、当前用户标注量、当前用户框数三个信息。

    return json.dumps(labeler_task, default=lambda o:o.__dict__)


@web.route('/task/show_task_detail',methods=['GET','POST'])
def show_task_detail():

    form = {'user':'meto','task_id':5,'type':1}
    # 点击开始标注 接收一条已被该用户锁定或未标注的数据
    # Task_details.query.filter_by().order_by()
    dict1 = {'photo_path': 'url','props': [
        {'prop_id': '12','prop_name': '衣服','property_values': [
            {'选项id': '1','选项名字': '黄皮'},{'选项id': '2','选项名字': '黑皮'},{'选项id': '3','选项名字': '绿皮'}]},
        {'prop_id': '13','prop_name': '衣服','property_values': [
            {'选项id': '4','选项名字': '穿衣服'},{'选项id': '2','选项名字': '没穿衣服'},{'选项id': '3','选项名字': '穿了衣服'}]}]}
    return json.dumps(dict1)
