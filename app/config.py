import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-key')
    
    # 数据库配置
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')
    
    # 根据环境变量选择数据库
    if DB_TYPE == 'mysql':
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOST')}:{os.environ.get('MYSQL_PORT')}/{os.environ.get('MYSQL_DB')}"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.environ.get('SQLITE_DB_PATH')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MySQL配置选项，确保正确处理自增字段
    if DB_TYPE == 'mysql':
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 280,
            'pool_timeout': 20,
            'pool_pre_ping': True
        }
