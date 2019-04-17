# _*_ coding:utf-8 _*_
from sqlalchemy import Column, Integer, String, desc, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base

__author__ = 'meto'
__date__ = '2019/4/11 11:00'


class Source(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(256), nullable=False)
    label_type = relationship('Label_type')

    label_type_id = Column(Integer, ForeignKey('label_type.id'))
    # source_type = Column(Integer, nullable=False)
    count = Column(Integer)

    @classmethod
    def get_source(cls, page, rows):
        if not page or not rows:
            page = 1
            # 默认10条
            rows = 10
        start_num = (int(page)-1)*int(rows)

        # 全部查询出来做切片
        # source = Source.query.filter_by().order_by(desc(Source.id)).slice(start_num, start_num+int(rows)).all()

        # 直接查询指定数量 ，这两种方式等数据量大了之后再进行比较速度;;事实证明，这个速度快
        source = Source.query.filter_by().order_by(
            desc(Source.id)).limit(rows).offset(
            start_num).all()

        return source