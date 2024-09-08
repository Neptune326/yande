import pymysql


class MySqlTool:
    # 构造对象，创建数据库连接对象，并创建数据库操作对象
    def __init__(self, *, host=None, port=None, user=None, password=None, database=None):
        self.db = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        self.cur = self.db.cursor()

    # 执行DML、DDL操作
    def execute(self, sql, params=None):
        n = 0
        try:
            n = self.cur.execute(sql, params)
            self.db.commit()
            print("execute: ", sql, params)
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            return n

    # 执行DQL操作
    def query(self, sql, params=None):
        n = self.cur.execute(sql, params)
        return self.cur.fetchmany(n)

    def __del__(self):
        self.cur.close()
        self.db.close()
