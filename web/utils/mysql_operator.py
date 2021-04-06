import pymysql
import logging
from config import MysqlDB_Params


class GetMysqlData(object):

    def __init__(self, host, user, password, port, db, charset):
        self.connection = {
            "host": host,
            "user": user,
            "password": password,
            "port": port,
            "db": db,
            "charset": charset,
        }

    def fetch_data(self, query, *args):
        """
        执行sql语句, 从数据库中获取数据
        :param query: sql语句
        :return:
            [ (xx,xxx,...), ... ] or []
        """
        cursor = None
        connect = pymysql.connect(**self.connection)
        try:
            cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute(query, args)
            return cursor.fetchall()
        except Exception as e:
            logging.error("查询失败, 原因 %s" % e)
            return None
        finally:
            cursor.close()
            connect.close()


mysql = GetMysqlData(**MysqlDB_Params)
