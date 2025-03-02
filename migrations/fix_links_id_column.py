import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app import create_app
from sqlalchemy import text

def fix_links_table():
    app = create_app()
    with app.app_context():
        # 使用原始SQL修改links表的id字段为自增
        with db.engine.connect() as connection:
            connection.execute(text("ALTER TABLE links MODIFY COLUMN id INT AUTO_INCREMENT"))
            connection.commit()
            print("修复完成：links表的id字段已设置为自动增长")

if __name__ == "__main__":
    fix_links_table()
