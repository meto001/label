# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/16 15:08'
import os
list1 = []


for i in range(5):
    list2 = []
    list2.append(i)
    list2.append(i*i)
    list1.append(list2)

print(str(list1))

