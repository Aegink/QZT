import database

def list_users():
    try:
        connection = database.connect_to_database()
        cursor = connection.cursor()

        # 获取所有用户信息，使用子查询获取最新的地址信息
        cursor.execute("""
            SELECT u.userId, u.userName, u.phonenumber, u.schoolName, u.collegeName, 
                   u.majorName, u.className, 
                   (SELECT ui2.address_lite 
                    FROM user_info ui2 
                    WHERE ui2.userId = u.userId 
                    ORDER BY ui2.updateTime DESC 
                    LIMIT 1) as address_lite
            FROM user u
            ORDER BY u.userId
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("暂无用户信息")
            return
            
        print("用户ID\t姓名\t手机号\t\t学校\t\t学院\t\t专业\t\t班级\t\t打卡地址")
        print("-" * 120)
        
        for user in users:
            user_id, name, phone, school, college, major, class_name, address = user
            # 处理None值和过长的字符串
            fields = [
                str(user_id),
                (name or "")[:8],
                (phone or "")[:11],
                (school or "")[:8],
                (college or "")[:8],
                (major or "")[:8],
                (class_name or "")[:8],
                (address or "")[:40]  # 增加地址显示长度
            ]
            print("\t".join(fields))
            
    except Exception as e:
        print(f"获取用户列表失败: {str(e)}")
        
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    list_users() 