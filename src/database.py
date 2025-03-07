import mysql.connector
from config import DB_CONFIG

def connect_to_database():
    """
    连接到 MySQL 数据库并返回一个连接对象。
    """
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection

def close_connection(connection):
    """
    关闭 MySQL 数据库连接。
    """
    connection.close()
