# _*_ coding:utf-8 _*_
import socket

from flask import request
from flask_login import login_required
from werkzeug.datastructures import MultiDict

from app.models.base import db
from app.view_models.source import SourceViewModel, SourceCollection, SourceImageViewModel
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
    print(request.remote_addr)
    page = request.args.get('page')
    rows = request.args.get('pagerows')
    source = Source.get_source(page, rows)
    source_count =Source.get_source_count()
    # source = Source.query.filter_by().all()
    sources = SourceCollection()
    sources.fill(source_count,source)

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
    try:
        addr = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    except:
        addr = '127.0.0.1'
    form = json.loads(request.data)
    if request.method == 'POST':
        source_image_path = Source_image_path()
        files = source_image_path.select_files_path(form['file_url'], addr)
        count = len(files)
        print(count)
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


@web.route('/view_source_image',methods=['POST'])
def view_source_image():
    if request.data:
        form = json.loads(request.data)
    else:
        # source_img_type 1为初始请求，3为下一张，2为上一张
        form = {'source_id': 30, 'source_img_type': 2,'source_image_id':15799}

    source_img_type = form.get('source_img_type')
    source_id = form.get('source_id')
    source_image_id = form.get('source_image_id')
    source_image_path = Source_image_path()
    source_img_data = source_image_path.get_source_img_data(source_id, source_img_type, source_image_id)
    if source_img_data is None:
        return json.dumps({'msg':'已经到头了！'})
    new_source_image_id = source_img_data.id
    image_url = source_img_data.image_url
    source_image = SourceImageViewModel()
    source_image.fill(source_id, new_source_image_id, image_url)

    return json.dumps(source_image,default=lambda o: o.__dict__)