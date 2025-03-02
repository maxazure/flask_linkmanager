from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # 使用 werkzeug 内置的密码哈希功能
from app import db, login_manager

class User(db.Model, UserMixin):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关系
    links = db.relationship('Link', backref='creator', lazy='dynamic')
    categories = db.relationship('Category', backref='creator', lazy='dynamic')
    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        """密码属性不可读"""
        raise AttributeError('密码不可读')
    
    @password.setter
    def password(self, password):
        """设置密码，自动进行哈希处理"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User: {self.username}>'
    
@login_manager.user_loader
def load_user(user_id):
    """加载用户回调函数"""
    return User.query.get(int(user_id))
