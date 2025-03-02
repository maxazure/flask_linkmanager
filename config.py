import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    
    # 使用MySQL配置
    DB_TYPE = os.environ.get('DB_TYPE', 'mysql')
    
    # MySQL配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'linkmanager')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'linkmanager')
    
    # SQLite配置（保留作为备选）
    SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH', 'instance/linkmanager.db')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DB_TYPE == 'mysql':
            return f'mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}'
        else:
            return f'sqlite:///{self.SQLITE_DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Admin配置
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # API密钥配置
    API_KEY_EXPIRATION_DAYS = 365  # 默认API密钥有效期为1年
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
