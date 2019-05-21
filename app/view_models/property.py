# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/15 15:12'
dict2 = {"properties": [
    {"id": 12,"label_type_name": "人脸质量标注","prop_name": "肤色"},
    {"id": 13,"label_type_name": "人脸质量标注","prop_name": "肤色"},
    {"id": 15,"label_type_name": "行人","prop_name": "衣服"},
    {"id": 16,"label_type_name": "行人","prop_name": "衣服"},
    {"id": 17,"label_type_name": "行人","prop_name": "衣服"}]}

dict1 = {"properties":[{"label_type_name": "人脸质量标注", "property_value":[{"id": 12,"prop_name":"肤色"},{"id": 13,"prop_name":"衣服"}]},
                {"label_type_name": "行人", "property_value":[{"id": 14,"prop_name":"帽子"},{"id": 15,"prop_name":"鞋子"}]}
              ]}

class PropertyViewModel:

    def __init__(self, label_property):
        self.id = label_property.id
        # 通过外键来取的label_type表中的name值
        self.label_type_name = label_property.label_type.name
        self.prop_name = label_property.prop_name


class PropertyCollection:
    def __init__(self):
        self.all_property_type = []
        self.properties = []



    def value_fill(self,property_value):
        pass


    def fill(self, label_properties):
        # list1 = []
        for label_property in label_properties:
            if label_property.label_type.name not in self.all_property_type:
                self.all_property_type.append(label_property.label_type.name)

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
        self.label_type = prop.property.label_type.name
        self.prop_id = prop.property.id
        self.prop_name = prop.property.prop_name
        if prop.property.prop_type == 1:
            self.prop_type = '单选'
        if prop.property.prop_type == 2:
            self.prop_type = '文本框'
        if prop.property.prop_type == 3:
            self.prop_type = '画框'
        # self.prop_type = prop.value_id
        self.property_values = [self.__map_to_property(label_property) for label_property in property_values]

    # 处理单个数据
    def __map_to_property(self,prop):
        return dict(
            option_id=prop.id,
            option_value=prop.option_value,
            option_name=prop.option_name
        )
