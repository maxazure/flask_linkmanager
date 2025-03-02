from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页路由"""
    if current_user.is_authenticated:
        return redirect(url_for('link.dashboard'))
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')
