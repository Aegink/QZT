import sys
import database

def delete_user(user_id):
    try:
        connection = database.connect_to_database()
        cursor = connection.cursor()

        # 删除用户信息
        cursor.execute("DELETE FROM user WHERE userId = %s", (user_id,))
        cursor.execute("DELETE FROM user_info WHERE userId = %s", (user_id,))
        
        connection.commit()
        print(f"成功删除用户ID: {user_id}")
        
    except Exception as e:
        print(f"删除用户失败: {str(e)}")
        
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python deleteUser.py <用户ID>")
        sys.exit(1)
        
    user_id = sys.argv[1]
    delete_user(user_id) 