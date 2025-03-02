#!/usr/bin/env python3

"""
修复 SQLAlchemy 与 Flask-SQLAlchemy 兼容性问题的脚本
当 SQLAlchemy 2.0+ 与 Flask-SQLAlchemy < 3.0 一起使用时会出现兼容性问题
"""

import subprocess
import sys

def fix_sqlalchemy():
    print("开始修复 SQLAlchemy 兼容性问题...")
    
    # 安装兼容版本的 SQLAlchemy
    print("安装兼容版本的 SQLAlchemy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "SQLAlchemy==1.4.46"])
        print("已成功安装 SQLAlchemy 1.4.46")
        
        # 可选：重新安装 Flask-SQLAlchemy 以确保兼容性
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask-SQLAlchemy==2.5.1"])
        print("已成功安装 Flask-SQLAlchemy 2.5.1")
        
        print("\n修复完成！请重新启动应用。")
    except subprocess.CalledProcessError as e:
        print(f"安装过程中出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_sqlalchemy()
