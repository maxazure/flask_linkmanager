#!/usr/bin/env python
"""
创建管理员用户的脚本

用法:
    python create_admin.py
"""

import sys
import getpass
from app import create_app, db
from app.models.user import User

def create_admin():
    """创建一个管理员用户"""
    app = create_app()
    
    with app.app_context():
        print("创建管理员账户")
        print("-----------------")
        
        username = input("用户名: ")
        email = input("邮箱: ")
        password = getpass.getpass("密码: ")
        confirm_password = getpass.getpass("确认密码: ")
        
        if password != confirm_password:
            print("错误: 两次密码输入不一致")
            return 1
        
        # 检查用户是否已存在
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("错误: 用户名或邮箱已存在")
            return 1
        
        # 创建管理员用户
        admin = User(
            username=username,
            email=email,
            password=password,
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"管理员用户 '{username}' 创建成功!")
        return 0

if __name__ == "__main__":
    sys.exit(create_admin())
