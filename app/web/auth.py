# _*_ coding:utf-8 _*_
from flask import render_template, request, redirect, url_for, flash
from werkzeug.datastructures import MultiDict

from app.models.base import db
from app.forms.auth import RegisterForm, LoginForm
from app.models.user import User
from flask_login import login_user
import json

__author__ = 'meto'
__date__ = '2019/3/21 11:06'

from .blue_print import web


@web.route('/register', methods=['POST'])
def register():
    # form = {"nickname": "paopa1o", "realname": "(宝1ᴗ宝)", "password": "123456", "email": "18301318212@qq.com",
    #         "groupid": 2}
    form = json.loads(request.data)
    form = RegisterForm(MultiDict(form))
    if request.method == 'POST' and form.validate() and form.data.get("groupid") != 1:
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        return json.dumps({'status': 'success'})
    form.errors
    return json.dumps({'status': 'fail'})


@web.route('/login', methods=['GET', 'POST'])
def login():
    """
    status:
    0:用户名或密码错误


    :return:
    """

    data = json.loads(request.data)
    data = MultiDict(data)
    form = LoginForm(data)
    # print(form.errors)

    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user and user.check_password(form.password.data):
            # 把用户信息写入到cookie中
            login_user(user, remember=True)
            result = {'code': 200, 'user_id': user.id, 'nickname': user.nickname, 'groupid': user.groupid}
        else:
            result = {'code': 250, 'msg': '用户名或密码错误'}
            # flash('用户不存在或密码错误')
    # return render_template('auth/login.html', form=form)
    else:

        result = {'status': 300, 'msg': "格式不符合要求"}
    return json.dumps(result)
    # return render_template('auth/login.html',form=form)


@web.route('/forget_password_request')
def forget_password_request():
    return 'None'
