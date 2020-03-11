# _*_ coding:utf-8 _*_

from .blue_print import web


__author__ = 'meto'
__date__ = '2020/2/18 14:33'


@web.route('labeler_history',methods=['POST','GET'])
def labeler_history():
    """
    进入页面后第一时间展示的数据。是一个任务列表，有查看功能，点击进去后有每个人的标注数据记录，
    点进入个人之后，出现时间框，选择时间后，出现记录
    :return:
    """
    pass

