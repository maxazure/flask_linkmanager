import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, create_app
from sqlalchemy import text

def fix_all_tables_pk():
    app = create_app()
    with app.app_context():
        # 查询所有表并检查主键配置
        with db.engine.connect() as connection:
            # 临时禁用外键检查
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            connection.commit()
            print("已临时禁用外键检查")
            
            try:
                # 获取数据库中的所有表
                result = connection.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                
                for table in tables:
                    # 查询表的主键信息
                    result = connection.execute(text(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'"))
                    primary_key = result.fetchone()
                    
                    if primary_key:
                        pk_column = primary_key[4]  # 主键列名称
                        
                        # 检查该列是否为AUTO_INCREMENT
                        result = connection.execute(text(f"SHOW COLUMNS FROM {table} WHERE Field = '{pk_column}'"))
                        column_info = result.fetchone()
                        
                        # 如果主键是整数类型且不是AUTO_INCREMENT，则修复
                        if column_info and ('int' in column_info[1].lower() or 'integer' in column_info[1].lower()):
                            if 'auto_increment' not in str(column_info[5]).lower():
                                print(f"表 {table} 的主键 {pk_column} 不是AUTO_INCREMENT，正在修复...")
                                connection.execute(text(f"ALTER TABLE {table} MODIFY COLUMN {pk_column} INT AUTO_INCREMENT"))
                                connection.commit()
                                print(f"✅ 表 {table} 已修复")
                            else:
                                print(f"表 {table} 的主键 {pk_column} 已正确设置为AUTO_INCREMENT")
                    else:
                        print(f"警告：表 {table} 没有主键，请手动检查")
            finally:
                # 重新启用外键检查
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                connection.commit()
                print("已重新启用外键检查")

if __name__ == "__main__":
    fix_all_tables_pk()
