# _*_ coding:utf-8 _*_
from app.libs.error import APIException

__author__ = 'meto'
__date__ = '2019/7/23 15:23'


class Success(APIException):
    code = 201
    msg = 'ok'
    error_code = 0


class RegisterFailed(APIException):
    code = 400
    msg = 'register failed'
    error_code = 1000


class LoginFailed(APIException):
    code = 400
    msg = 'login failed'
    error_code = 1001


class Completed(APIException):
    code = 201
    msg = '该任务已完成'
    status = 666
    error_code = 0
