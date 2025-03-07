import json
import requests
import base64
import database
import sys
import datetime
import os
from config import PUSHPLUS_TOKEN, PUSHPLUS_TOPIC, USER_ID

def print_separator():
    print("-" * 40)

def get_user_info(user_id):
    """获取用户信息"""
    try:
        connection = database.connect_to_database()
        with connection.cursor() as cursor:
            # 先检查用户是否存在
            cursor.execute("SELECT COUNT(*) FROM user WHERE userId = %s", (user_id,))
            count = cursor.fetchone()[0]
            if count == 0:
                return None, "用户不存在"

            # 获取用户信息
            cursor.execute("SELECT token FROM user WHERE userId = %s", (user_id,))
            token_result = cursor.fetchall()
            if not token_result:
                return None, f"未找到用户ID {user_id} 的token"
            token = token_result[0][0]

            cursor.execute("SELECT userName FROM user WHERE userId = %s", (user_id,))
            user_result = cursor.fetchall()
            if not user_result:
                return None, f"未找到用户ID {user_id} 的用户名"
            user_name = user_result[0][0]

            cursor.execute("SELECT address FROM user_info WHERE userId = %s", (user_id,))
            address_result = cursor.fetchall()
            if not address_result:
                return None, f"未找到用户ID {user_id} 的地址信息"
            address_json = address_result[0][0]

            cursor.execute("SELECT address_lite FROM user_info WHERE userId = %s", (user_id,))
            address_result = cursor.fetchall()
            if not address_result:
                return None, f"未找到用户ID {user_id} 的简略地址信息"
            address_lite = address_result[0][0]

            try:
                address_data = json.loads(address_json)
            except json.JSONDecodeError as e:
                return None, f"地址数据JSON解析失败: {str(e)}"

            return {
                "token": token,
                "user_name": user_name,
                "address_data": address_data,
                "address_lite": address_lite
            }, None

    except Exception as e:
        return None, f"数据库操作出错: {str(e)}"
    finally:
        if 'connection' in locals():
            connection.close()

# 如果命令行提供了用户ID，使用命令行的，否则使用配置文件的
if len(sys.argv) > 1:
    user_id = sys.argv[1].strip('"')  # 移除可能的引号
    # 验证用户ID
    connection = database.connect_to_database()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM user WHERE userId = %s", (user_id,))
        if cursor.fetchone()[0] == 0:
            print(f"❌ 错误：用户ID {user_id} 不存在")
            connection.close()
            sys.exit(1)
    connection.close()
else:
    user_id = USER_ID

print_separator()
print(f"开始为用户 {user_id} 执行打卡")
print_separator()

# 获取用户信息
user_info, error = get_user_info(user_id)
if error:
    print(f"❌ {error}")
    sys.exit(1)

print(f"用户名: {user_info['user_name']}")
print(f"打卡地址: {user_info['address_lite']}")
print_separator()

try:
    # 构造打卡数据
    punch_data = {
        "typeId": str(user_info['address_data'].get("typeId", "10")),
        "address": user_info['address_lite'],
        "addressLite": user_info['address_lite'],
        "latitude": str(user_info['address_data'].get("latitude", "25.425473")),
        "latitude2": str(user_info['address_data'].get("latitude2", "25.425473")),
        "longitude": str(user_info['address_data'].get("longitude", "106.751738")),
        "longitud2": str(user_info['address_data'].get("longitud2", "106.751738")),
        "userId": str(user_id),
        "locationName": user_info['address_data'].get("locationName", user_info['address_lite']),
        "cardRemark": user_info['address_data'].get("cardRemark", "打卡"),
        "checkRange": str(user_info['address_data'].get("checkRange", "2000")),
        "enterpriseId": user_info['address_data'].get("enterpriseId", ""),
        "locationCode": user_info['address_data'].get("locationCode", ""),
        "listPhoto": []
    }

    # 构造请求头
    headers = {
        'token': user_info['token'],
        'user-agent': 'Mozilla/5.0 (Linux; Android 14; LGE-AN00 Build/HONORLGE-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.210 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/30.461538)',
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    print("正在发送打卡请求...")
    response0 = requests.request("POST", "http://gwsxapp.gzzjzhy.com/api/workClock/punchClock", 
                               headers=headers, 
                               json=punch_data)
    
    try:
        response_data = response0.json()
        
        # 检查HTTP状态码
        if response0.status_code != 200:
            print(f"❌ HTTP错误: {response0.status_code}")
            raise Exception(f"服务器返回错误状态码: {response0.status_code}")
            
        # 检查业务状态码
        if response_data.get('code') == 500:
            print("❌ 服务器内部错误")
            raise Exception(f"服务器内部错误: {response_data.get('msg', '未知错误')}")
            
        # 保存响应数据
        with open('response_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(response_data, json_file, ensure_ascii=False, indent=2)
            
        # 打卡内容
        msg = response_data.get('msg', '未知状态')
        code = response_data.get('code')
        
        if code == 0:
            code_status = '打卡成功'
            print("\n✅ 打卡成功！")
        else:
            code_status = '打卡失败'
            print(f"\n❌ 打卡失败: {msg}")
            raise Exception(f"打卡失败: {msg}")

        # 获取当前时间
        current_time = datetime.datetime.now()
        timestamp = current_time.timestamp() * 1000000 + current_time.microsecond
        timestamp_str = str(timestamp)

        titles = "{},{}".format(user_info['user_name'], code_status)
        contents = "打卡状态：{}\n打卡地址：{}\n打卡时间：{}\n服务器时间戳：{}".format(
            msg, 
            user_info['address_lite'], 
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
            timestamp_str
        )

        print_separator()
        print("打卡结果：")
        print(f"状态: {msg}")
        print(f"时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print_separator()

        # 如果设置了 PUSHPLUS_TOKEN，则发送通知
        if PUSHPLUS_TOKEN:
            print("正在发送推送通知...")
            url = "https://www.pushplus.plus/send"
            
            payload = {
                "token": PUSHPLUS_TOKEN,
                "title": titles,
                "content": contents,
                "timestamp": timestamp_str,
                "template": "html"
            }
            
            # 如果设置了群组，添加群组参数
            if PUSHPLUS_TOPIC:
                payload["topic"] = PUSHPLUS_TOPIC
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            if '"code":200' in response.text:
                print("✅ 推送通知发送成功")
            else:
                print("❌ 推送通知发送失败")
        else:
            print("ℹ️ 未设置 PUSHPLUS_TOKEN，跳过推送通知")

    except Exception as e:
        print(f"❌ 打卡过程出错: {str(e)}")
        sys.exit(1)

except Exception as e:
    print(f"❌ 打卡过程出错: {str(e)}")
    sys.exit(1)