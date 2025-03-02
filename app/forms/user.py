from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from flask_login import current_user
from app.models.user import User

class ProfileForm(FlaskForm):
    """用户资料表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=64, message='用户名长度必须在3到64个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    submit = SubmitField('更新资料')
    
    def validate_username(self, field):
        """验证用户名是否已存在（排除当前用户）"""
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')
    
    def validate_email(self, field):
        """验证邮箱是否已存在（排除当前用户）"""
        if field.data != current_user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')


class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    current_password = PasswordField('当前密码', validators=[
        DataRequired(message='请输入当前密码')
    ])
    new_password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=8, message='密码长度不能少于8个字符')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('new_password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('修改密码')


class ApiKeyForm(FlaskForm):
    """API密钥表单"""
    description = StringField('描述', validators=[
        Optional(),
        Length(max=255, message='描述不能超过255个字符')
    ])
    days_valid = IntegerField('有效天数', default=365, validators=[
        Optional()
    ])
    submit = SubmitField('生成API密钥')
