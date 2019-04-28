# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/12 15:22'

from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey
from app.models.base import Base


class Property_value(Base):

    id = Column(Integer, primary_key=True, autoincrement=True)
    property = relationship('Property')
    prop_id =Column(Integer, ForeignKey('property.id'), nullable=False)

    option_value = Column(Integer, nullable=False)

    option_name = Column(String(30), nullable=ForeignKey)

    @classmethod
    def get_property_value(cls,id):
        property_value = Property_value.query.filter_by(prop_id=id).all()
        return property_value