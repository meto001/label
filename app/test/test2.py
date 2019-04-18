# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/18 11:12'
import json

dict2 = {"properties": [
    {"id": 12,"label_type_name": "人脸质量标注","prop_name": "肤色"},
    {"id": 13,"label_type_name": "人脸质量标注","prop_name": "肤色"},
    {"id": 14,"label_type_name": "人脸质量标注","prop_name": "肤色"},
    {"id": 15,"label_type_name": "行人","prop_name": "衣服"},
    {"id": 16,"label_type_name": "行人","prop_name": "衣服"},
    {"id": 17,"label_type_name": "行人","prop_name": "衣服"}]}


d3 = {}
a = dict2['properties']
for i in a:
    d3[i['label_type_name']] = ''
print(d3)

d4 = {}
for i in d3:
    pass



dict1 = {"properties":[{"label_type_name": "人脸质量标注", "property_value":[{"id": 12,"prop_name":"肤色"},{"id": 13,"prop_name":"衣服"}]},
                {"label_type_name": "行人", "property_value":[{"id": 14,"prop_name":"帽子"},{"id": 15,"prop_name":"鞋子"}]}
              ]}

# print(json.loads(json1))
# print(json.dumps(dict1))