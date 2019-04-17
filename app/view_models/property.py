# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/15 15:12'


class PropertyViewModel:

    def __init__(self, label_property):
        self.id = label_property.id
        # 通过外键来取的label_type表中的name值
        self.label_type_name = label_property.label_type.name
        self.prop_name = label_property.prop_name


class PropertyCollection:
    def __init__(self):
        self.properties = []

    def fill(self, label_properties):
        self.properties =[PropertyViewModel(label_property) for label_property in label_properties]


class PropertyValueViewModel:

    def __init__(self,label_property):
        self.label_type = ''
        self.prop_type = ''
        self.prop_name = ''
        self.prop_id = ''
        self.property_values = []
        self.__parse(label_property)

     # 处理一组数据
    def __parse(self,property_values):
        prop = property_values[0]
        self.label_type = prop.property.label_type_id
        self.prop_id = prop.property.id
        self.prop_name = prop.property.prop_name
        self.prop_type = prop.value_id
        self.property_values = [self.__map_to_property(label_property) for label_property in property_values]

    # 处理单个数据
    def __map_to_property(self,prop):
        return dict(
            id=prop.id,
            value_id=prop.value_id,
            value_name=prop.value_name
        )