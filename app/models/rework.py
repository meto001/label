# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/23 11:29'

from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, desc


class Rework(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)
    task = relationship('Task')
    task_id =Column(Integer, ForeignKey('task.id'))
    rework_date =Column(String(24))
    user = Column(String(24))
    operate_time = Column(Integer)
    all_count = Column(Integer)
    right_rate = Column(String(10))
    status = Column(Integer, default=0,comment='返工数据完成状态：0 未完成，1 已完成')
    # 质检，-1为返工, 0为未质检，1为已生成质检，2为质检完成
    quality_inspection= Column(Integer, default=0)

    @classmethod
    def get_rework_data(cls,nickname):
        rework_datas = Rework.query.filter_by(user=nickname, status=0).all()
        return rework_datas
