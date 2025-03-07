@echo off
chcp 65001 > nul
title 黔职通自动打卡系统

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo 创建虚拟环境失败！
        echo 请确保已安装 Python 3.7+
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功！
)

REM 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 激活虚拟环境失败！
    pause
    exit /b 1
)

REM 更新pip
python -m pip install --upgrade pip

REM 检查依赖是否已安装
python -c "import requests" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    REM 网络请求相关
    pip install requests==2.32.0
    pip install urllib3==2.2.2
    pip install certifi==2024.2.2
    pip install charset-normalizer==3.3.2
    pip install idna==3.7
    
    REM 数据库相关
    pip install mysql-connector-python==8.3.0
    
    REM 加密相关
    pip install pycryptodome==3.20.0
    
    REM 验证码处理相关
    pip install opencv-python==4.9.0.80
    pip install numpy==1.26.3
    
    if errorlevel 1 (
        echo 安装依赖失败！
        pause
        exit /b 1
    )
    echo 依赖安装成功！
)

REM 检查数据库连接
echo 正在检查数据库连接...
python src/checkDB.py
if errorlevel 1 (
    echo.
    echo 请检查数据库配置是否正确
    pause
    exit /b 1
)
echo.

:menu
cls
echo ====================================
echo        黔职通自动打卡系统
echo ====================================
echo.
echo   1. 执行打卡
echo   2. 查看配置
echo   3. 账号管理
echo   4. 恢复默认配置
echo   5. 重置数据库
echo   6. 退出程序
echo.
echo ====================================
echo.

set /p "choice=请输入选项（1-6）: "

if "%choice%"=="1" goto punch_in
if "%choice%"=="2" goto view_config
if "%choice%"=="3" goto account_management
if "%choice%"=="4" goto restore_defaults
if "%choice%"=="5" goto reset_database
if "%choice%"=="6" goto exit_program

echo.
echo 无效的选项，请重试...
timeout /t 2 > nul
goto menu

:punch_in
echo.
echo 当前账户列表：
echo ------------------------------------
python src/listUsers.py
echo ------------------------------------
echo.
set /p "userid=请输入要打卡的用户ID（输入0返回菜单）: "
if "%userid%"=="0" goto menu

REM 验证用户ID是否存在
python -c "import sys; sys.path.append('src'); import database; conn=database.connect_to_database(); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM user WHERE userId = %%s', ('%userid%',)); print(cur.fetchone()[0]); conn.close()" > temp.txt
set /p user_exists=<temp.txt
del temp.txt

if "%user_exists%"=="0" (
    echo.
    echo ❌ 错误：用户ID %userid% 不存在
    echo 按任意键返回...
    pause > nul
    goto punch_in
)

echo.
echo 正在为用户 %userid% 执行打卡...
python src/punchClock.py "%userid%"
echo.
echo 打卡完成！按任意键返回菜单...
pause > nul
goto menu

:view_config
echo.
echo 当前配置信息：
echo ------------------------------------
python -c "from src.config import *; print(f'用户ID: {USER_ID}\nPushPlus Token: {PUSHPLUS_TOKEN}\n数据库配置: {DB_CONFIG}')"
echo ------------------------------------
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:account_management
cls
echo ====================================
echo           账号管理菜单
echo ====================================
echo.
echo   1. 添加账号
echo   2. 删除账号
echo   3. 查看所有账号
echo   4. 返回主菜单
echo.
echo ====================================
echo.

set /p "account_choice=请输入选项（1-4）: "

if "%account_choice%"=="1" goto add_account
if "%account_choice%"=="2" goto delete_account
if "%account_choice%"=="3" goto list_accounts
if "%account_choice%"=="4" goto menu

echo.
echo 无效的选项，请重试...
timeout /t 2 > nul
goto account_management

:add_account
echo.
set /p "phone=请输入手机号: "
set /p "password=请输入密码: "
python src/main.py "%phone%" "%password%"
echo.
echo 账号添加完成！按任意键返回...
pause > nul
goto account_management

:delete_account
echo.
echo 当前账户列表：
echo ------------------------------------
python src/listUsers.py
echo ------------------------------------
echo.
set /p "userid=请输入要删除的用户ID: "
python src/deleteUser.py "%userid%"
echo.
echo 账号删除完成！按任意键返回...
pause > nul
goto account_management

:list_accounts
echo.
echo 所有账号信息：
echo ------------------------------------
python src/listUsers.py
echo ------------------------------------
echo.
echo 按任意键返回...
pause > nul
goto account_management

:restore_defaults
echo.
echo 正在恢复默认配置...
python src/restoreDefaults.py
echo.
echo 配置已恢复！按任意键返回菜单...
pause > nul
goto menu

:reset_database
echo.
echo ⚠️警告：此操作将清空数据库中的所有数据！
set /p "confirm=确定要继续吗？(Y/N): "
if /i not "%confirm%"=="Y" goto menu

echo.
echo 正在重置数据库...
python -c "import sys; sys.path.append('src'); import database; conn=database.connect_to_database(); cur=conn.cursor(); cur.execute('SET NAMES utf8mb4'); cur.execute('SET FOREIGN_KEY_CHECKS = 0'); cur.execute('DROP TABLE IF EXISTS `user`'); cur.execute('DROP TABLE IF EXISTS `user_info`'); cur.execute('CREATE TABLE `user` (`userId` int NOT NULL,`userName` varchar(255) NOT NULL,`phonenumber` varchar(255) NOT NULL,`sexName` varchar(255) NOT NULL,`schoolName` varchar(255) NOT NULL,`collegeName` varchar(255) NOT NULL,`majorName` varchar(255) NOT NULL,`className` varchar(255) NOT NULL,`teacherName` varchar(255) NOT NULL,`enterpriseId` varchar(255) NOT NULL,`enterpriseName` varchar(255) NOT NULL,`studentCode` varchar(255) NULL DEFAULT NULL,`token` longtext NOT NULL,`expTime` varchar(255) NOT NULL,`updateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,PRIMARY KEY (`userId`)) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic'); cur.execute('CREATE TABLE `user_info` (`userId` int NOT NULL COMMENT \"id\",`userName` varchar(255) NOT NULL COMMENT \"名字\",`phonenumber` varchar(255) NOT NULL COMMENT \"手机号\",`address` json NULL COMMENT \"完整打卡地址：10为正常打卡，9为外勤打卡\",`address_lite` varchar(255) NULL DEFAULT NULL,`updateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,PRIMARY KEY (`userId`)) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic'); cur.execute('SET FOREIGN_KEY_CHECKS = 1'); conn.commit(); conn.close(); print('数据库已重置成功！所有表已按原始结构重新创建。')"
echo.
echo 按任意键返回菜单...
pause > nul
goto menu

:exit_program
echo.
echo 正在退出虚拟环境...
call venv\Scripts\deactivate.bat
echo 感谢使用！
timeout /t 2 > nul
exit /b 0 