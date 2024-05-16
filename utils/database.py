import pymysql
import config.database


def get_db():
    db = pymysql.connect(host=config.database.host,
                         user=config.database.user,
                         password=config.database.password,
                         database=config.database.database,
                         charset=config.database.charset)
    return db
