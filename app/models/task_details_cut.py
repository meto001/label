# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/6/20 16:07'

from app.models.task_details import Task_details
from sqlalchemy.orm import relationship

from app.models.base import Base, db
from sqlalchemy import Column, String, Integer, ForeignKey, Float, SmallInteger, desc, asc, func


class Task_details_cut(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)

    task_details = relationship('Task_details')
    task_detail_id = Column(Integer, ForeignKey('task_details.id'))

    task_id = Column(Integer)

    split_type = Column(Integer, comment="1:矩形裁剪，2:多边形标记")
    coordinate = Column(String(300), comment='矩形或者多边形坐标')

    # 如果是质检员删除的框，则final_coordinate为空，如果是质检员新增的框，则coordinate为空
    final_coordinate = Column(String(300), comment='最终的矩形或者多边形坐标')
    graph_index = Column(Integer, comment='图形索引')

    pic_type = Column(Integer, comment='1:行人，2：机动车，3：非机动车')

    # operate_role = Column(Integer, comment='1:标注员，2:质检员')

    operate_user = Column(String(24))

    # operate_time = Column(Integer)

    photo_path = Column(String(300))

    @classmethod
    def get_frames(cls, task_detail_id):
        frames = Task_details_cut.query.filter_by(task_detail_id=task_detail_id).all()
        return frames
