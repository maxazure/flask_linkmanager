from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms.auth import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # 检查用户是通过用户名还是邮箱登录
        user = User.query.filter((User.username == form.username.data) | 
                               (User.email == form.username.data)).first()
        
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            # 如果请求中有next参数，登录后重定向到该URL
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('link.dashboard'))
        
        flash('用户名或密码不正确', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，现在您可以登录了', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """请求重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # 在实际应用中，这里应该发送重置密码的邮件
            # 简化版，直接显示一条消息
            flash('重置密码的邮件已发送，请检查您的邮箱', 'info')
        else:
            flash('未找到该邮箱对应的账户', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 在实际应用中，这里应该验证token
    # 简化版，直接显示重置密码表单
    form = PasswordResetForm()
    if form.validate_on_submit():
        # 实际应用中，这里应该根据token找到对应用户并更新密码
        flash('密码已重置，请使用新密码登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
