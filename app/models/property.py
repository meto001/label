# _*_ coding:utf-8 _*_
from sqlalchemy.orm import relationship

from app.models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, desc

__author__ = 'meto'
__date__ = '2019/4/12 14:41'



class Property(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)

    label_type = relationship('Label_type')

    label_type_id = Column(Integer, ForeignKey('label_type.id'))

    prop_name = Column(String(30), nullable= False)

    # 1 单选， 2 文本框
    prop_type = Column(Integer, nullable=False)

    @classmethod
    def get_property(cls):
        label_property = Property.query.filter_by().order_by(
            desc(Property.id)).all()
        return label_property

