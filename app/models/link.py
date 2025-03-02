from datetime import datetime
from app import db

# 链接-标签多对多关系表
link_tags = db.Table(
    'link_tags',
    db.Column('link_id', db.Integer, db.ForeignKey('links.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Link(db.Model):
    """链接模型"""
    __tablename__ = 'links'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # 关系
    category = db.relationship('Category', backref='links')
    tags = db.relationship('Tag', secondary=link_tags, backref=db.backref('links', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Link: {self.title}>'


class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Category: {self.name}>'


class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Tag: {self.name}>'
