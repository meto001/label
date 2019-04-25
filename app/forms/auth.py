# _*_ coding:utf-8 _*_
from app.models.user import User

__author__ = 'meto'
__date__ = '2019/3/22 11:09'
from wtforms import Form, StringField, IntegerField, PasswordField
from wtforms.validators import Length, NumberRange, DataRequired, Email, ValidationError


class SimpleMultiDict(dict):
    def getlist(self, key):
        return self[key]

    def __repr__(self):
        return type(self).__name__ + '(' + dict.__repr__(self) + ')'


class LoginForm(Form):
    print(type(Form))
    nickname = StringField(validators=[DataRequired(), Length(2,10, message='昵称至少需要2个字符，最多10个字符')])

    password = PasswordField(validators=[DataRequired(message='密码不可以为空， 请输入你的密码')])


class RegisterForm(Form):
    # email = StringField(validators=[DataRequired(), Length(8,64), Email(message='电子邮箱不符合规范')])

    password = PasswordField(validators=[DataRequired(message='密码不可以为空， 请输入你的密码'), Length(6, 32)])

    nickname = StringField(validators=[DataRequired(), Length(2,10, message='昵称至少需要2个字符，最多10个字符')])

    realname = StringField(validators=[DataRequired(), Length(2,10, message='姓名至少需要2个字符，最多10个字符')])

    email = StringField(validators=[DataRequired(), Length(8, 64),Email(message='电子邮箱不符合规范')])

    groupid = IntegerField(DataRequired())

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('昵称已被注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')


