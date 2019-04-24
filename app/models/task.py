# _*_ coding:utf-8 _*_
from app.models.source_image_path import Source_image_path

__author__ = 'meto'
__date__ = '2019/4/17 15:41'

from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc


class Task(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = relationship('Source')
    source_id = Column(Integer, ForeignKey('source.id'))

    # 存放属性值们的字段
    prop_ids = Column(String(300))

    task_name = Column(String(100))

    difficult_num = Column(Float)

    is_complete = Column(Integer)

    @classmethod
    def get_urls(cls,source_id):
        print("taskid:",Task.source_id)
        print(str(Source_image_path.query.filter_by(source_id=source_id)))
        urls = Source_image_path.query.filter_by(source_id=source_id).all()
        return urls

    @classmethod
    def get_task(cls, page, rows):
        if not page or not rows:
            page = 1
            # 默认10条
            rows = 10
        start_num = (int(page) - 1) * int(rows)

        task = Task.query.filter_by().order_by(
            desc(Task.id)).limit(rows).offset(
            start_num).all()

        return task

    @classmethod
    def get_undone_task(cls, page, rows):
        if not page or not rows:
            page = 1
            # 默认10条
            rows = 10
        start_num = (int(page) - 1) * int(rows)

        tasks = Task.query.filter_by(is_complete=0).order_by(
            desc(Task.id)).limit(rows).offset(
            start_num).all()

        return tasks