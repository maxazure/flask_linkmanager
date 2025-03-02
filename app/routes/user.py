from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.apikey import ApiKey
from app.forms.user import ProfileForm, ChangePasswordForm, ApiKeyForm

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户资料页面"""
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('user/profile.html', form=form)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.current_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            flash('密码已成功修改', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('当前密码不正确', 'danger')
    
    return render_template('user/change_password.html', form=form)


@user_bp.route('/api-keys', methods=['GET', 'POST'])
@login_required
def api_keys():
    """管理API密钥"""
    form = ApiKeyForm()
    if form.validate_on_submit():
        days_valid = form.days_valid.data or 365  # 默认365天
        api_key = ApiKey.generate_key(
            user_id=current_user.id,
            description=form.description.data,
            days_valid=days_valid
        )
        flash('API密钥已成功生成', 'success')
        return redirect(url_for('user.api_keys'))
    
    # 获取用户的所有API密钥
    api_keys = ApiKey.query.filter_by(user_id=current_user.id).order_by(ApiKey.created_at.desc()).all()
    
    return render_template('user/api_keys.html', form=form, api_keys=api_keys)


@user_bp.route('/api-keys/<int:key_id>/revoke', methods=['POST'])
@login_required
def revoke_api_key(key_id):
    """撤销API密钥"""
    api_key = ApiKey.query.get_or_404(key_id)
    
    # 确保只能撤销自己的API密钥
    if api_key.user_id != current_user.id:
        flash('无权执行此操作', 'danger')
        return redirect(url_for('user.api_keys'))
    
    api_key.revoke()
    flash('API密钥已成功撤销', 'success')
    return redirect(url_for('user.api_keys'))
