import os
import sys
import time
import pymysql
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 获取MySQL连接信息
host = os.environ.get('MYSQL_HOST', '192.168.31.205')
port = int(os.environ.get('MYSQL_PORT', 3306))
user = os.environ.get('MYSQL_USER', 'linkmanager')
password = os.environ.get('MYSQL_PASSWORD', 'mwhZAW7pWyDBHrWE')
db = os.environ.get('MYSQL_DB', 'linkmanager')

print(f'MySQL连接信息:')
print(f'主机: {host}')
print(f'端口: {port}')
print(f'用户: {user}')
print(f'密码: {"*" * len(password)}')
print(f'数据库: {db}')
print('-' * 50)

try:
    print('尝试连接到MySQL服务器(不指定数据库)...')
    connection = pymysql.connect(host=host, port=port, user=user, password=password)
    print('连接成功!')
    
    # 检查用户权限
    with connection.cursor() as cursor:
        print('\n检查用户权限:')
        cursor.execute('SHOW GRANTS')
        grants = cursor.fetchall()
        for grant in grants:
            print(f'- {grant[0]}')
    
    # 列出所有数据库
    with connection.cursor() as cursor:
        print('\n可用的数据库:')
        cursor.execute('SHOW DATABASES')
        databases = cursor.fetchall()
        for database in databases:
            print(f'- {database[0]}')
    
    # 尝试创建数据库
    try:
        print(f'\n尝试创建数据库 {db}:')
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS `{db}`')
        print('创建数据库成功或已存在')
    except Exception as e:
        print(f'创建数据库时出错: {e}')
    
    # 尝试设置字符集
    try:
        print(f'\n尝试设置数据库 {db} 字符集:')
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        print('设置字符集成功')
    except Exception as e:
        print(f'设置字符集时出错: {e}')
    
    connection.close()
    
    # 尝试连接到指定数据库
    print(f'\n尝试连接到数据库 {db}:')
    connection = pymysql.connect(host=host, port=port, user=user, password=password, database=db)
    print(f'成功连接到数据库 {db}')
    
    # 检查数据库版本
    with connection.cursor() as cursor:
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()
        print(f'MySQL版本: {version[0]}')
    
    connection.close()
    print('\n所有测试通过!')
    
except Exception as e:
    print(f'\n连接测试失败: {e}')
    print('请检查连接参数和网络设置')
    sys.exit(1)
