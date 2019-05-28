# _*_ coding:utf-8 _*_
from app import create_app

__author__ = 'meto'
__date__ = '2019/5/20 15:33'

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import make_url



def get_mysql_conn_url(config):
    """
    :description: 生成sqlalchemy使用的连接url
    :param hy_config: hy_config
    :return: url
    """
    mysql_conn_map = dict(
        dialect="mysql",
        driver="pymysql",
        host='127.0.0.1',
        port=3306,
        database='label',
        user='facesysuser',
        password='faceagv10086',
    )
    # s = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8".format(**mysql_conn_map)
    s =  'mysql+cymysql://facesysuser:faceagv10086@localhost:3306/fisher'
    # s = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}".format(**mysql_conn_map)
    url = make_url(s)
    return url

def create_mysql_ORM(app):
    """
    创建MySQL的ORM对象并反射数据库中已存在的表，获取所有存在的表对象
    :param app: app:flask实例
    :return: (db:orm-obj, all_table:数据库中所有已存在的表的对象(dict))
    """
    # 创建mysql连接对象
    url = get_mysql_conn_url(config=app.config)
    app.config["SQLALCHEMY_DATABASE_URI"] = url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True  # 每次请求结束时自动commit数据库修改
    app.config["SQLALCHEMY_ECHO"] = False   # 如果设置成 True，SQLAlchemy将会记录所有发到标准输出(stderr)的语句,这对调试很有帮助.
    app.config["SQLALCHEMY_RECORD_QUERIES"] = None  # 可以用于显式地禁用或者启用查询记录。查询记录 在调试或者测试模式下自动启用。
    app.config["SQLALCHEMY_POOL_SIZE"] = 5  # 数据库连接池的大小。默认是数据库引擎的默认值(通常是 5)。
    app.config["SQLALCHEMY_POOL_TIMEOUT"] = 10  # 指定数据库连接池的超时时间。默认是 10。
    """
    自动回收连接的秒数。
    这对 MySQL 是必须的，默认 情况下 MySQL 会自动移除闲置 8 小时或者以上的连接。 
    需要注意地是如果使用 MySQL 的话， Flask-SQLAlchemy 会自动地设置这个值为 2 小时。
    """
    app.config["SQLALCHEMY_POOL_RECYCLE"] = None
    """
    控制在连接池达到最大值后可以创建的连接数。
    当这些额外的 连接回收到连接池后将会被断开和抛弃。
    """
    app.config["SQLALCHEMY_MAX_OVERFLOW"] = None
    # 获取SQLAlchemy实例对象
    db = SQLAlchemy(app)

    # 反射数据库中已存在的表，并获取所有存在的表对象。
    db.reflect()


    all_table = {table_obj.name: table_obj for table_obj in db.get_tables_for_bind()}

    return db, all_table

# app = create_app()
# db, all_table = create_mysql_ORM(app=app)
# print(all_table['user'])
# print(type(all_table['user'].))
# print(db.session.query(all_table['user']).filter(all_table['user'].key.id>=1).first())
# pag = db.session.query(all_table["user"]).paginate(page=1,per_page=2)
# print(pag.items)

from sqlalchemy import MetaData, create_engine, join

s =  'mysql+cymysql://facesysuser:faceagv10086@localhost:3306/fisher'
metadata = MetaData()
engine = create_engine(s)
from sqlalchemy import Table
metadata.reflect(bind=engine)
users = metadata.tables['user']
from sqlalchemy import select
a = users.get_children('id') == 1
print(a)
s = select([users]).where(users.get_children('id') == 1)

result = engine.execute(s).fetchall()
print(result)