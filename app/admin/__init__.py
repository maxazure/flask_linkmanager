from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, abort
from app import db
from app.models.user import User
from app.models.link import Link, Category, Tag
from app.models.apikey import ApiKey

class AdminBaseView:
    """基础管理视图的访问控制"""
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        # 如果没有权限访问，重定向到首页
        return redirect(url_for('main.index'))

class AdminIndexView(AdminBaseView, AdminIndexView):
    """管理后台首页视图"""
    pass

class AdminModelView(AdminBaseView, ModelView):
    """基础模型管理视图"""
    pass


class UserModelView(AdminModelView):
    """用户管理视图"""
    column_list = ('id', 'username', 'email', 'is_admin', 'created_at', 'last_login')
    column_searchable_list = ('username', 'email')
    column_filters = ('is_admin', 'created_at', 'last_login')
    form_excluded_columns = ('password_hash', 'links', 'categories', 'api_keys')
    column_labels = {
        'username': '用户名',
        'email': '邮箱',
        'is_admin': '管理员',
        'created_at': '创建时间',
        'last_login': '最后登录'
    }


class LinkModelView(AdminModelView):
    """链接管理视图"""
    column_list = ('id', 'title', 'url', 'creator', 'category', 'created_at')
    column_searchable_list = ('title', 'url', 'description')
    column_filters = ('creator', 'category', 'created_at')
    column_labels = {
        'title': '标题',
        'url': 'URL',
        'description': '描述',
        'creator': '创建者',
        'category': '分类',
        'created_at': '创建时间',
        'tags': '标签'
    }


class CategoryModelView(AdminModelView):
    """分类管理视图"""
    column_list = ('id', 'name', 'creator', 'description')
    column_searchable_list = ('name', 'description')
    column_filters = ('creator',)
    column_labels = {
        'name': '名称',
        'description': '描述',
        'creator': '创建者',
        'links': '链接'
    }


class TagModelView(AdminModelView):
    """标签管理视图"""
    column_list = ('id', 'name', 'description')
    column_searchable_list = ('name', 'description')
    column_labels = {
        'name': '名称',
        'description': '描述',
        'links': '链接'
    }


class ApiKeyModelView(AdminModelView):
    """API密钥管理视图"""
    column_list = ('id', 'user', 'description', 'created_at', 'expires_at', 'is_active')
    column_searchable_list = ('description',)
    column_filters = ('user', 'created_at', 'expires_at', 'is_active')
    column_labels = {
        'user': '用户',
        'key': '密钥',
        'description': '描述',
        'created_at': '创建时间',
        'expires_at': '过期时间',
        'is_active': '是否激活'
    }


def init_admin(app):
    """初始化Flask-Admin"""
    admin = Admin(
        app,
        name='链接管理系统',
        template_mode='bootstrap3',
        index_view=AdminIndexView(endpoint='admin', url='/admin')
    )
    
    # 添加模型视图
    admin.add_view(UserModelView(User, db.session, name='用户管理', endpoint='admin_user'))
    admin.add_view(LinkModelView(Link, db.session, name='链接管理', endpoint='admin_link'))
    admin.add_view(CategoryModelView(Category, db.session, name='分类管理', endpoint='admin_category'))
    admin.add_view(TagModelView(Tag, db.session, name='标签管理', endpoint='admin_tag'))
    admin.add_view(ApiKeyModelView(ApiKey, db.session, name='API密钥管理', endpoint='admin_apikey'))
    
    return admin
