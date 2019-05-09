# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/4/11 14:42'


class SourceViewModel:
    source = {'source_name': 'wwtest', 'source_type': 1, 'count': 100, 'url': 'F:/数据需求/标注系统测试'}
    def __init__(self,source):
        self.id = source.id
        self.source_name = source.source_name
        self.label_type = source.label_type.name
        self.create_time = source.create_time
        self.count = source.count



class SourceCollection:

    def __init__(self):
        self.total = 0
        self.sources = []

    def fill(self, total, sources):
        self.total = total
        self.sources = [SourceViewModel(source) for source in sources]


class SourceImageViewModel:
    def __init__(self):
        self.source_id = 0
        self.source_image_id = 0
        self.image_url = ''

    def fill(self, source_id, source_image_id, image_url):
        self.source_id = source_id
        self.source_image_id = source_image_id
        self.image_url = image_url
