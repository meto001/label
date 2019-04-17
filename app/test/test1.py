import hashlib
import codecs
user_input = hashlib.pbkdf2_hmac('sha256',b'123456',b'Ur2nXrxI', 150000)
hash1 = codecs.encode(user_input,'hex_codec')
front = 'pbkdf2:sha256:150000$Ur2nXrxI$'
input_pwd = front+hash1.decode()
print(input_pwd)