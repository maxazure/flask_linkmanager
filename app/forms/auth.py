from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名或邮箱', validators=[DataRequired(message='请输入用户名或邮箱')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=64, message='用户名长度必须在3到64个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=8, message='密码长度不能少于8个字符')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')
    
    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')
    
    def validate_email(self, field):
        """验证邮箱是否已存在"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')


class PasswordResetRequestForm(FlaskForm):
    """密码重置请求表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'), 
        Email(message='请输入有效的邮箱地址')
    ])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    """密码重置表单"""
    password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=8, message='密码长度不能少于8个字符')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('重置密码')
