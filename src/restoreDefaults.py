import os
import json

# 默认配置
DEFAULT_CONFIG = {
    "PUSHPLUS_TOKEN": "bdbe981febc743d2bf847cbcc4562308",
    "PUSHPLUS_TOPIC": "",
    "DB_CONFIG": {
        "host": "localhost",
        "user": "root",
        "password": "123456",
        "database": "qzt",
        "port": 3306
    },
    "USER_ID": "716515"
}

def restore_defaults():
    try:
        # 确保src目录存在
        if not os.path.exists('src'):
            os.makedirs('src')
            
        # 写入默认配置
        config_content = f'''"""
配置文件
"""

# PushPlus 配置
PUSHPLUS_TOKEN = "{DEFAULT_CONFIG['PUSHPLUS_TOKEN']}"  # PushPlus 的 token
PUSHPLUS_TOPIC = "{DEFAULT_CONFIG['PUSHPLUS_TOPIC']}"  # 群组编码，不需要可以留空

# 数据库配置
DB_CONFIG = {json.dumps(DEFAULT_CONFIG['DB_CONFIG'], indent=4)}

# 用户配置
USER_ID = "{DEFAULT_CONFIG['USER_ID']}"
'''
        
        with open('src/config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        print("已恢复默认配置")
        print("默认配置信息：")
        print("-" * 40)
        print(f"PushPlus Token: {DEFAULT_CONFIG['PUSHPLUS_TOKEN']}")
        print(f"数据库配置: {DEFAULT_CONFIG['DB_CONFIG']}")
        print(f"用户ID: {DEFAULT_CONFIG['USER_ID']}")
        print("-" * 40)
        
    except Exception as e:
        print(f"恢复默认配置失败: {str(e)}")

if __name__ == "__main__":
    restore_defaults() 