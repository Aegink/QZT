import sys
import database

try:
    conn = database.connect_to_database()
    conn.close()
    print('数据库连接成功！')
    sys.exit(0)
except Exception as e:
    print('❌ 数据库连接失败！')
    print('错误信息：', e)
    sys.exit(1) 