import login
import json
import database
import sys
import requests

def get_coordinates_from_baidu(address):
    """
    使用API获取地址的经纬度
    提示用户需要手动从坐标拾取器获取经纬度
    """
    print("\n请按以下步骤操作：")
    print(f"1. 打开坐标拾取器（按住Ctrl+鼠标右击一下该连接）：http://jingweidu.757dy.com/")
    print(f"2. 在搜索框中输入获取的地址（Ctrl+C复制）：{address}")
    print("3. 点击搜索结果或在地图上精确定位")
    print("4. 点击显示的经纬度就可以复制")
    print("5. （Ctrl+V）粘贴经度和纬度（用逗号分隔，例如：106.749796,25.429894）：")
    coords = input().strip().split(',')
    if len(coords) != 2:
        print("输入格式错误，将使用默认经纬度")
        return "106.749796", "25.429894"
    return coords[0].strip(), coords[1].strip()

def get_latest_address_from_db(user_id):
    """从数据库获取用户最新的地址信息"""
    connection = database.connect_to_database()
    cursor = connection.cursor()
    try:
        # 查询用户最新的地址信息
        sql = f"SELECT address, address_lite FROM user_info WHERE userId = '{user_id}' ORDER BY id DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result and result[0]:  # 如果找到地址信息
            address_data = json.loads(result[0])
            return address_data, result[1]
        return None, None
    except Exception as e:
        print(f"获取数据库地址信息失败: {str(e)}")
        return None, None
    finally:
        cursor.close()
        connection.close()

def get_user_address(token, user_id):
    """获取用户的打卡地址信息"""
    # 首先尝试从数据库获取最新地址
    saved_address_data, saved_address_lite = get_latest_address_from_db(user_id)
    if saved_address_data:
        print(f"从数据库获取到最新地址：{saved_address_lite}")
        return json.dumps(saved_address_data, ensure_ascii=False), saved_address_lite

    headers = {
        'token': token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 14; LGE-AN00 Build/HONORLGE-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.210 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/30.461538)',
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    
    # 获取学生实习企业信息
    enterprise_url = "http://gwsxapp.gzzjzhy.com/api/user/studentInternshipEnterprise"
    enterprise_response = requests.get(enterprise_url, headers=headers)
    enterprise_address = None
    enterprise_name = None
    enterprise_id = None
    
    if enterprise_response.status_code == 200:
        enterprise_data = enterprise_response.json()
        if enterprise_data.get('code') == 0 and enterprise_data.get('data'):
            enterprise_info = enterprise_data.get('data')
            print(f"获取到实习企业信息：{enterprise_info}")
            # 构建完整地址
            province = enterprise_info.get('province', '')
            city = enterprise_info.get('city', '')
            area = enterprise_info.get('area', '')
            address = enterprise_info.get('address', '')
            enterprise_name = enterprise_info.get('enterpriseName', '')
            enterprise_id = enterprise_info.get('enterpriseId', '')
            
            # 处理特殊情况：如果address为空但有enterpriseName，使用enterpriseName作为地址
            if not address and enterprise_name:
                if '医院' in enterprise_name or '药店' in enterprise_name or '药房' in enterprise_name:
                    address = enterprise_name
            
            # 构建完整地址，确保地址信息完整
            if address:
                # 如果address已经包含了province/city/area的信息，就直接使用address
                if any(part in address for part in [province, city, area]):
                    enterprise_address = address
                else:
                    # 否则拼接完整地址
                    enterprise_address = f"{province}{city}{area}{address}"
            else:
                # 如果没有详细地址，使用企业名称
                enterprise_address = f"{province}{city}{area}{enterprise_name}"
            
            print(f"处理后的完整地址：{enterprise_address}")
    
    # 如果成功获取到企业信息，直接使用企业地址
    if enterprise_address and enterprise_name and enterprise_id:
        # 获取经纬度
        longitude, latitude = get_coordinates_from_baidu(enterprise_address)
        
        address_data = {
            "typeId": "10",
            "latitude": latitude,
            "latitude2": latitude,
            "longitude": longitude,
            "longitud2": longitude,
            "locationName": enterprise_address,
            "cardRemark": "打卡",
            "checkRange": "2000",
            "enterpriseId": enterprise_id,
            "locationCode": "",
            "listPhoto": []
        }
        return json.dumps(address_data, ensure_ascii=False), enterprise_address
    
    # 如果获取企业信息失败，继续使用原有的打卡记录逻辑
    # 获取打卡记录列表
    url = "http://gwsxapp.gzzjzhy.com/api/workClock/getClockList"
    response = requests.post(url, headers=headers, json={"userId": user_id})
    if response.status_code != 200:
        raise Exception("获取打卡记录失败")
        
    data = response.json()
    if data.get('code') != 0:
        raise Exception(f"获取打卡记录失败: {data.get('msg')}")
        
    records = data.get('data', [])
    if not records:
        # 如果没有打卡记录，获取实习地点信息
        url = "http://gwsxapp.gzzjzhy.com/api/practice/getPracticeInfo"
        response = requests.post(url, headers=headers, json={"userId": user_id})
        if response.status_code != 200:
            raise Exception("获取实习信息失败")
            
        data = response.json()
        if data.get('code') != 0:
            raise Exception(f"获取实习信息失败: {data.get('msg')}")
            
        practice_info = data.get('data', {})
        if not practice_info:
            raise Exception("未找到实习信息")
            
        # 构造地址信息
        address_data = {
            "typeId": "10",
            "latitude": str(practice_info.get('latitude', "25.425473")),
            "latitude2": str(practice_info.get('latitude', "25.425473")),
            "longitude": str(practice_info.get('longitude', "106.751738")),
            "longitud2": str(practice_info.get('longitude', "106.751738")),
            "locationName": practice_info.get('practiceAddress', ""),
            "cardRemark": "打卡",
            "checkRange": "2000",
            "enterpriseId": practice_info.get('enterpriseId', ""),
            "locationCode": "",
            "listPhoto": []
        }
        address_lite = practice_info.get('practiceAddress', "")
    else:
        # 使用最近一次打卡记录的地址
        latest_record = records[0]
        address_data = {
            "typeId": "10",
            "latitude": str(latest_record.get('latitude', "25.425473")),
            "latitude2": str(latest_record.get('latitude', "25.425473")),
            "longitude": str(latest_record.get('longitude', "106.751738")),
            "longitud2": str(latest_record.get('longitude', "106.751738")),
            "locationName": latest_record.get('address', ""),
            "cardRemark": "打卡",
            "checkRange": "2000",
            "enterpriseId": latest_record.get('enterpriseId', ""),
            "locationCode": "",
            "listPhoto": []
        }
        address_lite = latest_record.get('address', "")
    
    return json.dumps(address_data, ensure_ascii=False), address_lite

def print_separator():
    print("-" * 40)

# 获取验证码
print("正在获取验证码...")
returnData = login.captchaGget()

secretKeyBytes = returnData["repData"]["secretKey"].encode('utf-8')
token = returnData["repData"]["token"].encode('utf-8')
originalImgBase64 = returnData["repData"]["originalImageBase64"]
jigsawImgBase64 = returnData["repData"]["jigsawImageBase64"]

# 计算偏移量
print("正在处理验证码...")
xOffsetResult = login.calculateOffset(originalImgBase64, jigsawImgBase64)
coordinateBytes = json.dumps({"x": xOffsetResult, "y": 5}, separators=(',', ':'))
tokenCoordinateBytes = (token.decode('utf-8') + "---" + coordinateBytes).encode('utf-8')
encryptedVerification = login.encryptAesEcb(coordinateBytes.encode("utf-8"), secretKeyBytes)
captchaVerification = login.encryptAesEcb(tokenCoordinateBytes, secretKeyBytes)

# 验证码验证
print("正在验证验证码...")
login.checkVerification(encryptedVerification, token.decode('utf-8'))

# 登录
if len(sys.argv) != 3:
    print("使用方法: python main.py <手机号> <密码>")
    sys.exit(1)

phone = sys.argv[1]
passwd = sys.argv[2]

print("正在登录...")
login_data = login.login(phone, passwd, captchaVerification)

if login_data.get('code') != 0:
    print(f"❌ 登录失败: {login_data.get('msg', '未知错误')}")
    sys.exit(1)

print("✅ 登录成功！")
print_separator()

# 保存登录数据
with open('login_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(login_data, json_file, ensure_ascii=False, indent=2)

# 获取用户信息
user_data = login_data['data']
userId = user_data['userId']
userName = user_data['userName']
phonenumber = user_data['phonenumber']
sexName = user_data['sexName']
schoolName = user_data['schoolName']
collegeName = user_data['collegeName']
majorName = user_data['majorName']
className = user_data['className']
teacherName = user_data['teacherName']
enterpriseId = user_data['enterpriseId']
enterpriseName = user_data['enterpriseName']
studentCode = user_data['studentCode']
token = user_data['token']
expTime = user_data['expTime']

print(f"用户名: {userName}")
print(f"学校: {schoolName}")
print(f"学院: {collegeName}")
print(f"专业: {majorName}")
print(f"班级: {className}")
print_separator()

print("正在获取打卡地址信息...")
try:
    address_json, address_lite = get_user_address(token, userId)
    print("✅ 获取地址成功！")
    print(f"打卡地址: {address_lite}")
    address_data = json.loads(address_json)
    print(f"经度: {address_data['longitude']}")
    print(f"纬度: {address_data['latitude']}")
    print_separator()
except Exception as e:
    print(f"❌ 获取地址失败: {str(e)}")
    print("将使用默认地址信息")
    address_json = json.dumps({
        "typeId": "10",
        "latitude": "25.425473",
        "latitude2": "25.425473",
        "longitude": "106.751738",
        "longitud2": "106.751738",
        "locationName": enterpriseName,
        "cardRemark": "打卡",
        "checkRange": "2000",
        "enterpriseId": enterpriseId,
        "locationCode": "",
        "listPhoto": []
    }, ensure_ascii=False)
    address_lite = enterpriseName
    print_separator()

# 连接数据库
print("正在保存用户信息...")
connection = database.connect_to_database()
cursor = connection.cursor()

try:
    # 检查用户是否已存在
    sql = f"SELECT * FROM user WHERE userId = '{userId}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if result:
        # 更新用户信息
        user_sql = f"""
            UPDATE user
            SET token = '{token}',
                userName = '{userName}',
                phonenumber = '{phonenumber}',
                sexName = '{sexName}',
                schoolName = '{schoolName}',
                collegeName = '{collegeName}',
                majorName = '{majorName}',
                className = '{className}',
                teacherName = '{teacherName}',
                enterpriseId = '{enterpriseId}',
                enterpriseName = '{enterpriseName}',
                studentCode = '{studentCode}',
                expTime = '{expTime}'
            WHERE userId = '{userId}'
        """

        user_info_sql = f"""
            UPDATE user_info
            SET userName = '{userName}',
                phonenumber = '{phonenumber}',
                address = '{address_json}',
                address_lite = '{address_lite}'
            WHERE userId = '{userId}'
        """
    else:
        # 插入新用户信息
        user_sql = f"""
        INSERT INTO user (
            userId,
            userName,
            phonenumber,
            sexName,
            schoolName,
            collegeName,
            majorName,
            className,
            teacherName,
            enterpriseId,
            enterpriseName,
            studentCode,
            token,
            expTime
        )
        VALUES (
            '{userId}',
            '{userName}',
            '{phonenumber}',
            '{sexName}',
            '{schoolName}',
            '{collegeName}',
            '{majorName}',
            '{className}',
            '{teacherName}',
            '{enterpriseId}',
            '{enterpriseName}',
            '{studentCode}',
            '{token}',
            '{expTime}'
        );
        """

        user_info_sql = f"""
        INSERT INTO user_info (userId, userName, phonenumber, address, address_lite)
        VALUES (
            '{userId}',
            '{userName}',
            '{phonenumber}',
            '{address_json}',
            '{address_lite}'
        );
        """

    # 执行SQL并立即提交
    cursor.execute(user_sql)
    connection.commit()
    
    cursor.execute(user_info_sql)
    connection.commit()
    
    print("✅ 用户信息保存成功！")

except Exception as e:
    print(f"❌ 保存用户信息失败: {str(e)}")
    connection.rollback()
    sys.exit(1)

finally:
    cursor.close()
    connection.close()