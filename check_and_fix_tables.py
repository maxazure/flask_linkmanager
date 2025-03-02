import os
import sys
from app import db, create_app
from sqlalchemy import text, inspect

def check_and_fix_tables():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # 获取所有表名
        table_names = inspector.get_table_names()
        print(f"发现数据库中共有 {len(table_names)} 个表：{', '.join(table_names)}")
        
        with db.engine.connect() as connection:
            # 禁用外键检查
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            connection.commit()
            print("已临时禁用外键检查")
            
            try:
                # 检查每个表
                for table_name in table_names:
                    # 获取表的主键
                    pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
                    
                    if not pk_columns:
                        print(f"警告：表 {table_name} 没有主键！")
                        continue
                        
                    # 获取每个主键列的详细信息
                    for pk_column in pk_columns:
                        column_info = None
                        for column in inspector.get_columns(table_name):
                            if column['name'] == pk_column:
                                column_info = column
                                break
                        
                        if not column_info:
                            print(f"警告：无法获取表 {table_name} 的主键列 {pk_column} 的信息")
                            continue
                        
                        # 检查是否为整数类型 (通常用于自增)
                        is_integer = any(t in str(column_info['type']).lower() for t in ['int', 'integer'])
                        
                        # MySQL特定检查：使用show columns命令检查是否为自增
                        result = connection.execute(text(f"SHOW COLUMNS FROM {table_name} WHERE Field='{pk_column}'"))
                        column_details = result.fetchone()
                        is_auto_increment = column_details is not None and "auto_increment" in str(column_details[5]).lower()
                        
                        print(f"表 {table_name}：主键列 {pk_column} 是整数类型：{is_integer}，自增：{is_auto_increment}")
                        
                        # 如果是整数主键但不是自增的，修复它
                        if is_integer and not is_auto_increment:
                            print(f"修复表 {table_name} 的主键列 {pk_column}...")
                            connection.execute(text(f"ALTER TABLE {table_name} MODIFY COLUMN {pk_column} INT AUTO_INCREMENT"))
                            connection.commit()
                            print(f"✅ 表 {table_name} 已修复")
            finally:
                # 重新启用外键检查
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                connection.commit()
                print("已重新启用外键检查")

if __name__ == "__main__":
    check_and_fix_tables()
