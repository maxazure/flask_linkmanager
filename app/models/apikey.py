import secrets
from datetime import datetime, timedelta
from app import db
from app.models.user import User

class ApiKey(db.Model):
    """API密钥模型"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    @classmethod
    def generate_key(cls, user_id, description=None, days_valid=365):
        """
        为指定用户生成新的API密钥
        
        Args:
            user_id: 用户ID
            description: 密钥描述
            days_valid: 有效天数，默认365天
            
        Returns:
            ApiKey: 新创建的API密钥对象
        """
        # 生成64字符的随机字符串
        key = secrets.token_hex(32)
        
        # 计算过期时间
        expires_at = datetime.utcnow() + timedelta(days=days_valid)
        
        # 创建并保存新密钥
        api_key = cls(
            key=key,
            user_id=user_id,
            description=description,
            expires_at=expires_at
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        return api_key
    
    @classmethod
    def validate_key(cls, key):
        """
        验证API密钥
        
        Args:
            key: API密钥字符串
            
        Returns:
            User or None: 如果密钥有效返回关联的用户，否则返回None
        """
        api_key = cls.query.filter_by(key=key, is_active=True).first()
        
        # 如果密钥不存在或已过期，返回None
        if not api_key or (api_key.expires_at and api_key.expires_at < datetime.utcnow()):
            return None
        
        return User.query.get(api_key.user_id)
    
    def revoke(self):
        """撤销此API密钥"""
        self.is_active = False
        db.session.commit()
        
    def __repr__(self):
        return f'<ApiKey: {self.key[:8]}... User: {self.user_id}>'
