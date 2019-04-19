# _*_ coding:utf-8 _*_
from flask import request
from flask_login import login_required
from werkzeug.datastructures import MultiDict

from app.models.base import db
from app.view_models.source import SourceViewModel, SourceCollection
from .blue_print import web

__author__ = 'meto'
__date__ = '2019/4/11 11:41'
import json
from app.models.source import Source
from app.models.source_image_path import Source_image_path
from app.models.user import User


@web.route('/source', methods=['GET', 'POST'])
# @login_required
def source():
    """
        此处要使用view_models ,将testuser转化为对象。然后再进行__dict__操作
    :return:
    """
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    source = Source.get_source(page, rows)
    # source = Source.query.filter_by().all()
    len(source)
    sources = SourceCollection()
    sources.fill(len(source),source)
    sources

    return json.dumps(sources,default=lambda o:o.__dict__)
    # return json.dumps(testuser.__dict__)
    pass
    # return 'source'


@web.route('/add_source', methods=['POST'])
# @login_required
def add_source():
    # 假数据
    # form = {'source_name': 'wwtest2', 'label_type_id': 2, 'file_url': 'F:/数据需求/标注系统测试/1'}
    # form = MultiDict(json.loads(request.data))
    form = json.loads(request.data)
    if request.method == 'POST':
        source_image_path = Source_image_path()
        files = source_image_path.select_files_path(form['file_url'])
        count = len(files)
        with db.auto_commit():
            source = Source()
            form['count'] = count
            source.set_attrs(form)
            db.session.add(source)
        with db.auto_commit():
            for file in files:
                source_image_path = Source_image_path()
                form['source_id'] = source.id
                form['image_url'] = file
                source_image_path.set_attrs(form)
                db.session.add(source_image_path)

    return json.dumps({'status' : 'success'})
