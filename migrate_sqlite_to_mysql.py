import sqlite3
import pymysql
import os
from dotenv import load_dotenv
import sys
import json
from datetime import datetime

# 加载环境变量
load_dotenv()

# 配置信息
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'instance/links.db')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DB', 'linkmanager')

def connect_sqlite():
    """连接到 SQLite 数据库"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # 使结果以字典形式返回
        print(f"成功连接到 SQLite 数据库: {SQLITE_DB_PATH}")
        return conn
    except sqlite3.Error as e:
        print(f"连接 SQLite 数据库时出错: {e}")
        sys.exit(1)

def connect_mysql():
    """连接到 MySQL 数据库"""
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"成功连接到 MySQL 数据库: {MYSQL_HOST}")
        return conn
    except pymysql.MySQLError as e:
        print(f"连接 MySQL 数据库时出错: {e}")
        sys.exit(1)

def backup_sqlite_data(sqlite_conn):
    """备份 SQLite 数据库中的所有数据"""
    cursor = sqlite_conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    backup = {}
    
    for table_info in tables:
        table_name = table_info['name']
        # 跳过 SQLite 内部表
        if table_name.startswith('sqlite_'):
            continue
            
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # 获取表数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 将表结构和数据保存到字典中
        backup[table_name] = {
            'columns': [dict(col) for col in columns],
            'rows': [dict(row) for row in rows]
        }
    
    return backup

def create_mysql_database(mysql_conn, db_name):
    """在 MySQL 中创建数据库"""
    cursor = mysql_conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        mysql_conn.commit()
        print(f"成功创建/确认 MySQL 数据库: {db_name}")
    except pymysql.MySQLError as e:
        print(f"创建数据库时出错: {e}")
        sys.exit(1)
    
    # 使用创建的数据库
    cursor.execute(f"USE {db_name}")
    mysql_conn.commit()

def sqlite_to_mysql_type(sqlite_type):
    """将 SQLite 数据类型转换为 MySQL 数据类型"""
    sqlite_type = sqlite_type.lower()
    
    if 'int' in sqlite_type:
        return 'INT'
    elif 'char' in sqlite_type or 'text' in sqlite_type or 'clob' in sqlite_type:
        return 'TEXT'
    elif 'real' in sqlite_type or 'floa' in sqlite_type or 'doub' in sqlite_type:
        return 'DOUBLE'
    elif 'blob' in sqlite_type:
        return 'BLOB'
    elif 'bool' in sqlite_type:
        return 'BOOLEAN'
    elif 'date' in sqlite_type:
        return 'DATETIME'
    else:
        return 'TEXT'  # 默认使用 TEXT

def create_tables_in_mysql(mysql_conn, backup_data):
    """在 MySQL 中创建表"""
    cursor = mysql_conn.cursor()
    
    for table_name, table_data in backup_data.items():
        columns = table_data['columns']
        
        # 构建创建表的 SQL 语句
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        primary_keys = []
        
        for col in columns:
            col_name = col['name']
            # 转换数据类型
            col_type = sqlite_to_mysql_type(col['type'])
            
            create_table_sql += f"{col_name} {col_type}"
            
            # 处理 NOT NULL
            if col['notnull'] == 1:
                create_table_sql += " NOT NULL"
            
            # 处理默认值
            if col['dflt_value'] is not None:
                # 对字符串类型加引号
                if col_type in ['TEXT', 'DATETIME']:
                    create_table_sql += f" DEFAULT '{col['dflt_value']}'"
                else:
                    create_table_sql += f" DEFAULT {col['dflt_value']}"
            
            # 处理主键
            if col['pk'] == 1:
                primary_keys.append(col_name)
            
            create_table_sql += ", "
        
        # 添加主键约束
        if primary_keys:
            create_table_sql += f"PRIMARY KEY ({', '.join(primary_keys)})"
        else:
            # 删除最后一个逗号和空格
            create_table_sql = create_table_sql[:-2]
        
        create_table_sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        
        try:
            cursor.execute(create_table_sql)
            mysql_conn.commit()
            print(f"成功创建表: {table_name}")
        except pymysql.MySQLError as e:
            print(f"创建表 {table_name} 时出错: {e}")
            print(f"SQL: {create_table_sql}")
            # 继续执行，不中断程序

def insert_data_into_mysql(mysql_conn, backup_data):
    """将数据插入到 MySQL 表中"""
    cursor = mysql_conn.cursor()
    
    for table_name, table_data in backup_data.items():
        rows = table_data['rows']
        if not rows:
            print(f"表 {table_name} 中没有数据")
            continue
        
        # 获取列名
        columns = [col['name'] for col in table_data['columns']]
        
        for row in rows:
            # 构建插入语句
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # 准备数据
            values = [row[col] for col in columns]
            
            try:
                cursor.execute(insert_sql, values)
            except pymysql.MySQLError as e:
                print(f"向表 {table_name} 插入数据时出错: {e}")
                print(f"数据: {values}")
                # 继续执行，不中断程序
        
        mysql_conn.commit()
        print(f"向表 {table_name} 成功插入 {len(rows)} 条记录")

def main():
    """主函数"""
    print("开始数据库迁移: SQLite -> MySQL")
    
    # 连接到数据库
    sqlite_conn = connect_sqlite()
    mysql_conn = connect_mysql()
    
    # 备份 SQLite 数据
    print("正在从 SQLite 读取数据...")
    backup_data = backup_sqlite_data(sqlite_conn)
    
    # 创建 MySQL 数据库
    create_mysql_database(mysql_conn, MYSQL_DB)
    
    # 在 MySQL 中创建表
    print("正在 MySQL 中创建表结构...")
    create_tables_in_mysql(mysql_conn, backup_data)
    
    # 将数据插入到 MySQL
    print("正在将数据导入到 MySQL...")
    insert_data_into_mysql(mysql_conn, backup_data)
    
    # 完成
    print("数据迁移完成!")
    
    # 关闭连接
    sqlite_conn.close()
    mysql_conn.close()

if __name__ == "__main__":
    # 创建备份时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 记录迁移操作日志
    with open(f"migration_log_{timestamp}.txt", "w") as log_file:
        # 重定向标准输出到日志文件
        original_stdout = sys.stdout
        sys.stdout = log_file
        
        try:
            main()
        finally:
            # 恢复标准输出
            sys.stdout = original_stdout
    
    # 在控制台上显示完成消息
    print(f"数据迁移完成! 详细日志已保存到 migration_log_{timestamp}.txt")
