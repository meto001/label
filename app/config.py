# _*_ coding:utf-8 _*_
__author__ = 'meto'
__date__ = '2019/5/15 11:46'


class APSchedulerJobConfig(object):
    JOBS = [{
        'id': 'make_check_task',
        'func': 'app.web.quality_check:auto_generate_quality_check',
        'args': '',
        'trigger': {
            'type': 'cron',
            'day_of_week': '0-6',
            'hour': '18',
            'minute':'19'
        }
    }]
    SCHEDULER_API_ENABLED = True
    # SQLALCHEMY_ECHO = True

cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '182.61.51.47',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': '',
    'CACHE_REDIS_PASSWORD': ''
}