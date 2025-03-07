## 许可证
本项目现依据 **GNU General Public License v3.0** 发布。详见 [LICENSE](LICENSE)。

# 本项目基于开源项目“https://github.com/Iuleoo/QZT?tab=readme-ov-file”，在此感谢大佬

# 本项目仅供学习交流使用，请勿用于非法用途。

# 本项目不保证打卡成功，请自行承担使用风险

# 黔职通自动打卡系统 - 使用手册

## 一、开始之前

### 1. 下载必要软件
1. **下载并安装 Python**
   - 访问 [Python下载页面](https://www.python.org/downloads/)
   - 点击"Download Python 3.12.1"（或最新版本）
   - 运行下载的安装程序
   - ⚠️ 重要：安装时必须勾选"Add Python to PATH"选项！

2. **下载并安装 MySQL**
   - 访问 [MySQL下载页面](https://dev.mysql.com/downloads/installer/)
   - 下载"Windows (x86, 32-bit), MSI Installer"
   - 运行安装程序，选择"Full"安装
   - 记住设置的 root 密码！

### 2. 下载本程序
- 下载程序压缩包
- 解压到任意位置（路径最好不要有中文）

## 二、首次配置（一次性设置）

### 1. 配置数据库
1. **打开命令提示符(CMD)**
   - 按下 `Win + R` 键
   - 输入 `cmd` 并按回车
   - ⚠️ 如果出现"拒绝访问"，请右键点击CMD以管理员身份运行

2. **登录MySQL**
   ```cmd
   mysql -u root -p
   ```
   - 输入你安装MySQL时设置的密码
   - ✅ 成功标志：显示 "Welcome to the MySQL monitor..."
   - ❌ 如果提示 "Access denied"：
     1. 检查密码是否正确
     2. 如果忘记密码，运行以下命令重置：
        ```cmd
        net stop mysql
        mysqld --skip-grant-tables
        mysql
        ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';
        FLUSH PRIVILEGES;
        EXIT;
        net start mysql
        ```

3. **创建数据库**
   ```sql
   CREATE DATABASE qzt;
   ```
   - ✅ 成功标志：显示 "Query OK, 1 row affected"
   - ❌ 如果提示 "database exists"，先删除旧数据库：
     ```sql
     DROP DATABASE qzt;
     CREATE DATABASE qzt;
     ```
   - 验证数据库创建：
     ```sql
     SHOW DATABASES;
     ```
     应该能看到 `qzt` 在列表中

4. **初始化数据库表**
   ```sql
   USE qzt;
   ```
   - ✅ 成功标志：显示 "Database changed"
   - 检查数据库表：
     ```sql
     SHOW TABLES;
     ```
     - 如果为空，说明正常（首次运行时会自动创建表）
     - 如果显示旧表，可以清理：
       ```sql
       DROP TABLE IF EXISTS users;
       DROP TABLE IF EXISTS punch_records;
       ```

5. **测试数据库连接**
   - 退出 MySQL：
     ```sql
     EXIT;
     ```
   - 运行测试命令：
     ```cmd
     python src/checkDB.py
     ```
   - ✅ 成功标志：显示 "数据库连接成功！"
   - ❌ 如果连接失败：
     1. 检查配置文件 `src/config.py` 中的数据库信息是否正确
     2. 确认MySQL服务是否运行：
        ```cmd
        net start mysql
        ```
     3. 检查防火墙是否允许MySQL（端口3306）

6. **故障排除**
   如果以上步骤都无法解决问题：
   1. 完全卸载MySQL：
      ```cmd
      net stop mysql
      "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld" --remove
      ```
   2. 删除MySQL文件夹：
      - 删除 `C:\Program Files\MySQL`
      - 删除 `C:\ProgramData\MySQL`
   3. 重新安装MySQL：
      - 下载 MySQL 8.0 安装包
      - 选择"Custom"安装
      - 只选择"Server"和"Workbench"组件
      - 设置新的root密码
   4. 重新执行步骤1-5

### 2. 修改配置文件
1. 用记事本打开 `src/config.py` 文件
2. 修改数据库配置：
   ```python
   DB_CONFIG = {
       'host': 'localhost',      # 保持不变
       'user': 'root',          # 数据库用户名（一般是root）
       'password': '你的密码',   # 改成你的MySQL密码
       'database': 'qzt'        # 保持不变
   }
   ```

### 3. 设置手机推送（可选）
1. **获取推送Token**
   - 访问 [PushPlus官网](http://www.pushplus.plus)
   - 使用微信扫码登录
   - 复制你的Token

2. **配置推送**
   - 打开 `src/config.py` 文件（与数据库配置在同一个文件）
   - 找到 `PUSHPLUS_TOKEN` 配置项
   - 修改为：
   ```python
   PUSHPLUS_TOKEN = "你的pushplus令牌"
   ```
   - 保存文件后生效

## 三、使用说明

### 1. 启动程序
- 双击 `menu.bat` 文件
- 首次运行会自动安装必要组件

### 2. 账号管理
1. **添加账号**
   - 选择"账号管理" -> "添加账号"
   - 输入手机号和密码
   - 系统会自动获取实习地点信息

2. **查看账号**
   - 选择"账号管理" -> "查看所有账号"
   - 显示所有账号的详细信息，包括最新的打卡地址

3. **删除账号**
   - 选择"账号管理" -> "删除账号"
   - 输入要删除的用户ID

### 3. 打卡功能
1. **执行打卡**
   - 在主菜单选择"执行打卡"
   - 输入用户ID
   - 系统会自动获取最新的打卡地址

2. **地址更新**
   - 系统会自动从实习企业信息获取地址
   - 支持自动处理医院、药店等特殊地点
   - 地址变更会自动更新到数据库

### 4. 查看结果
- 控制台显示详细信息
- 微信推送打卡结果（如果配置了推送）

## 四、注意事项

### 1. 地址相关
- 系统会自动获取最新的实习地点
- 支持完整的地址显示（省市区+详细地址）
- 地址更新后会立即生效

### 2. 安全提醒
- 定期修改密码
- 不要泄露个人信息
- 保护好数据库配置

### 3. 使用建议
- 建议在正常工作时间打卡
- 定期检查打卡记录
- 特殊情况建议手动打卡

## 五、常见问题

### 1. 打卡地址问题
- 地址未更新：重新登录账号
- 地址显示不全：检查数据库连接
- 地址错误：手动更新企业信息

### 2. 系统问题
- 数据库连接失败：检查配置
- 程序无响应：检查网络
- 推送失败：验证Token

### 3. 获取帮助
- 保存错误信息
- 记录操作步骤
- 提供系统环境信息

## 六、更新日志

### 最新版本 1.3.0
- 优化地址获取逻辑
- 支持特殊地点自动处理
- 改进地址显示格式
- 提升数据库操作稳定性
