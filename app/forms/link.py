from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, URL, Length, Optional
from app.models import Category, Tag

class LinkForm(FlaskForm):
    """链接表单"""
    title = StringField('标题', validators=[
        DataRequired(message='请输入标题'),
        Length(max=200, message='标题不能超过200个字符')
    ])
    url = StringField('URL', validators=[
        DataRequired(message='请输入URL'),
        URL(message='请输入有效的URL'),
        Length(max=500, message='URL不能超过500个字符')
    ])
    description = TextAreaField('描述', validators=[
        Optional(),
        Length(max=1000, message='描述不能超过1000个字符')
    ])
    category_id = SelectField('分类', coerce=int, validators=[
        DataRequired(message='请选择分类')
    ])
    tags = SelectMultipleField('标签', coerce=int)
    submit = SubmitField('保存')
    
    def __init__(self, *args, user_id=None, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        if user_id:
            # 动态加载当前用户的分类
            self.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=user_id).all()]
            # 加载所有标签
            self.tags.choices = [(t.id, t.name) for t in Tag.query.all()]


class CategoryForm(FlaskForm):
    """分类表单"""
    name = StringField('名称', validators=[
        DataRequired(message='请输入分类名称'),
        Length(max=64, message='分类名称不能超过64个字符')
    ])
    description = TextAreaField('描述', validators=[
        Optional(),
        Length(max=500, message='描述不能超过500个字符')
    ])
    submit = SubmitField('保存')


class TagForm(FlaskForm):
    """标签表单"""
    name = StringField('名称', validators=[
        DataRequired(message='请输入标签名称'),
        Length(max=64, message='标签名称不能超过64个字符')
    ])
    description = TextAreaField('描述', validators=[
        Optional(),
        Length(max=500, message='描述不能超过500个字符')
    ])
    submit = SubmitField('保存')
    
    def validate_name(self, field):
        """验证标签名称是否已存在"""
        tag = Tag.query.filter_by(name=field.data).first()
        if tag:
            from wtforms.validators import ValidationError
            raise ValidationError('该标签名称已存在')
