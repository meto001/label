# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/3/27 11:03'

from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import codecs

# 数据库密码
password = 'pbkdf2:sha256:50000$H97wNNI0$0ef21c1b446c23eb1787bbf04aeb5a7c4e2840805acad614328e12f008e9be19'
user_input = hashlib.pbkdf2_hmac('sha256', b'123456', b'H97wNNI0', 50000)
hash1 = codecs.encode(user_input, 'hex_codec')
front = 'pbkdf2:sha256:50000$H97wNNI0$'
input_pwd = front+hash1.decode()
print(input_pwd)
if input_pwd == password:
    print('密码正确')