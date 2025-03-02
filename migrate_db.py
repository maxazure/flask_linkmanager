import sqlite3
import pymysql
from config import Config
import os
import argparse
from dotenv import load_dotenv

def migrate_sqlite_to_mysql(replace_data=False, clear_tables=False):
    load_dotenv()
    
    # SQLite连接
    sqlite_path = os.path.join(os.getcwd(), Config().SQLITE_DB_PATH)
    print(f"连接SQLite数据库: {sqlite_path}")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # MySQL连接
    config = Config()
    mysql_conn = pymysql.connect(
        host=config.MYSQL_HOST,
        port=int(config.MYSQL_PORT),
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB
    )
    mysql_cursor = mysql_conn.cursor()
    
    # 获取所有表
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue
            
        print(f"迁移表: {table_name}")
        
        # 如果需要清空表
        if clear_tables:
            try:
                mysql_cursor.execute(f"TRUNCATE TABLE {table_name};")
                mysql_conn.commit()
                print(f"  已清空表 {table_name}")
            except Exception as e:
                print(f"  清空表 {table_name} 失败: {str(e)}")
        
        # 获取表结构
        sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
        columns = sqlite_cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 获取表数据
        sqlite_cursor.execute(f"SELECT * FROM {table_name};")
        rows = sqlite_cursor.fetchall()
        
        # 准备插入语句
        if rows:
            placeholders = ", ".join(["%s"] * len(column_names))
            columns_str = ", ".join(column_names)
            
            # 根据参数决定是否替换数据
            if replace_data:
                insert_query = f"REPLACE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                print(f"  使用REPLACE模式，将覆盖已存在的数据")
            else:
                insert_query = f"INSERT IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                print(f"  使用INSERT IGNORE模式，将保留已存在的数据")
            
            # 批量插入数据
            try:
                mysql_cursor.executemany(insert_query, rows)
                mysql_conn.commit()
                print(f"  成功插入/更新 {len(rows)} 行数据到表 {table_name}")
            except Exception as e:
                print(f"  插入数据到表 {table_name} 失败: {str(e)}")
    
    # 关闭连接
    sqlite_cursor.close()
    sqlite_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
    
    print("数据库迁移完成!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='从SQLite迁移数据到MySQL')
    parser.add_argument('--replace', action='store_true', help='替换现有数据（如果主键冲突）')
    parser.add_argument('--clear', action='store_true', help='在迁移前清空表')
    args = parser.parse_args()
    
    if args.clear and not args.replace:
        print("警告：您选择了清空表但未选择替换数据。这可能导致数据重复。")
        confirm = input("是否继续? [y/N]: ")
        if confirm.lower() != 'y':
            print("迁移已取消")
            exit(0)
    
    migrate_sqlite_to_mysql(replace_data=args.replace, clear_tables=args.clear)
