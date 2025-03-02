from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
# from flask_bcrypt import Bcrypt  # 暂时注释掉，使用 werkzeug 内置功能
from config import config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# bcrypt = Bcrypt()  # 暂时注释掉

def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name or 'default'])
    
    # 根据环境变量选择数据库
    db_type = os.environ.get('DB_TYPE', 'sqlite')
    
    if db_type == 'mysql':
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOST')}:{os.environ.get('MYSQL_PORT')}/{os.environ.get('MYSQL_DB')}"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.environ.get('SQLITE_DB_PATH', 'instance/linkmanager.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # bcrypt.init_app(app)  # 暂时注释掉
    
    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'
    
    # 注册蓝图
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.link import link_bp
    from app.api.routes import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(link_bp, url_prefix='/links')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # 初始化Flask-Admin
    from app.admin import init_admin
    init_admin(app)
    
    # 创建所有数据库表
    with app.app_context():
        db.create_all()
    
    return app
