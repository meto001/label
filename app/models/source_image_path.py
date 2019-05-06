# _*_ coding:utf-8 _*_
import socket

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
import imghdr
from app.models.base import Base
import os
__author__ = 'meto'
__date__ = '2019/4/11 11:14'


class Source_image_path(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = relationship('Source')
    source_id = Column(Integer, ForeignKey('source.id'))
    image_url = Column(String(1024), nullable=False)

    def select_files_path(self,url, addr):
        file_list = []
        imgType_list = {'jpg', 'bmp', 'png', 'jpeg', 'rgb', 'tif'}
        for root, b, files in os.walk(url):
            for file in files:
                # if file.endswith()
                # file_path = root + '/' + file
                file_path = 'http://'+addr+':82/static' +root.split('static')[-1]+'/'+file
                # 判断文件类型
                # if imghdr.what(file_path) in imgType_list and file.split('.')[-1] in imgType_list:
                if file.split('.')[-1] in imgType_list:
                    file_path = file_path.replace('\\','/')
                    file_list.append(file_path)
        print('file_list Length:',len(file_list))
        return file_list
