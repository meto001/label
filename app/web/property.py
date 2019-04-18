# _*_ coding:utf-8 _*_
import json
import time

from flask import request
from flask_login import login_required
from app import db
from app.models.label_type import Label_type
from app.models.property import Property
from app.models.property_value import Property_value
from app.view_models.property import PropertyCollection, PropertyValueViewModel

__author__ = 'meto'
__date__ = '2019/4/12 16:05'
from .blue_print import web


@web.route('/show_property', methods=['GET', 'POST'])
# @login_required
def show_property():

    # 展示属性
    label_properties = Property.get_property()
    property_values = PropertyCollection()
    property_values.fill(label_properties)
    # dict1 = json.loads(json.dumps(property_values, default=lambda o:o.__dict__))
    return json.dumps(property_values, default=lambda o:o.__dict__)


@web.route('/show_property_value', methods=['GET', 'POST'])
# @login_required
def show_property_value():
    form = {'prop_id':12}
    property_value_tb = Property_value()

    # 查询数据库符合条件的数据
    property_values = property_value_tb.get_property_value(form['prop_id'])

    properties = PropertyValueViewModel(property_values)
    return json.dumps(properties, default=lambda o:o.__dict__)


@web.route('/add_property', methods=['POST'])
# @login_required
def add_property():

    # 新增传进来的form
    form = {'prop_name': '衣服', 'label_type_id': 2, 'prop_type': 1, 'property_value':
        [{'value_id': 1, 'value_name': '黄皮'},
         {'value_id': 2, 'value_name': '黑皮'},
         {'value_id': 3, 'value_name': '白皮'}]}

    # 修改传进来的form
    form = {'prop_id':12, 'property_value':
        [{'id': 16, 'value_id': 4, 'value_name': '吧lue皮'},
         {'value_id': 5, 'value_name': '花皮'},
         {'id':30,'delete':1}]}

    if request.method == 'POST':
        label_type = Label_type()

        # 1.将prop_name、label_type、prop_type 插入到property表中
        with db.auto_commit():
            property = Property()

            # 如果是修改,form['prop_id']值不为空，则不执行下面的语句
            if form.get('prop_id') == None:
                property.set_attrs(form)
                db.session.add(property)

        # 将propery_value中的值插入到property_value表中
        with db.auto_commit():
            for value in form['property_value']:
                property_value = Property_value()
                prop_id = ''

                # 如果是修改，property.id为空，需要使用传进来的prop_id
                if property.id is None:
                    prop_id = form['prop_id']
                else:
                    prop_id = property.id
                value['prop_id'] = prop_id

                # 修改property_value
                if value.get('id'):
                    id = value['id']
                    already_exist = property_value.query.filter_by(id=id).first()
                    # 判断是否要删除
                    if value.get('delete'):
                        db.session.delete(already_exist)
                    else:
                        already_exist.value_id = value['value_id']
                        already_exist.value_name = value['value_name']

                else:
                    property_value.set_attrs(value)
                    db.session.add(property_value)

    print('继续执行')
    # return json.dumps(form)
    return '成功'
