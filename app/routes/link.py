from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.link import Link, Category, Tag, link_tags
from app.forms.link import LinkForm, CategoryForm, TagForm

link_bp = Blueprint('link', __name__)

@link_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘/链接管理首页"""
    # 获取用户的链接总数
    links_count = Link.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户的分类总数
    categories_count = Category.query.filter_by(user_id=current_user.id).count()
    
    # 获取用户使用的标签总数
    tags_count = db.session.query(Tag).join(
        link_tags, Tag.id == link_tags.c.tag_id
    ).join(
        Link, Link.id == link_tags.c.link_id
    ).filter(
        Link.user_id == current_user.id
    ).distinct().count()
    
    # 获取用户最近添加的5个链接
    recent_links = Link.query.filter_by(user_id=current_user.id).order_by(
        Link.created_at.desc()
    ).limit(5).all()
    
    return render_template('link/dashboard.html',
                          links_count=links_count,
                          categories_count=categories_count,
                          tags_count=tags_count,
                          recent_links=recent_links)


@link_bp.route('/all')
@login_required
def list_links():
    """列出用户的所有链接"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    tag_id = request.args.get('tag', type=int)
    query = request.args.get('q', '')
    
    # 基本查询：用户的所有链接
    links_query = Link.query.filter_by(user_id=current_user.id)
    
    # 按分类筛选
    if category_id:
        links_query = links_query.filter_by(category_id=category_id)
    
    # 按标签筛选
    if tag_id:
        links_query = links_query.join(
            link_tags, Link.id == link_tags.c.link_id
        ).filter(
            link_tags.c.tag_id == tag_id
        )
    
    # 搜索
    if query:
        links_query = links_query.filter(
            or_(
                Link.title.ilike(f'%{query}%'),
                Link.url.ilike(f'%{query}%'),
                Link.description.ilike(f'%{query}%')
            )
        )
    
    # 分页
    pagination = links_query.order_by(Link.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    links = pagination.items
    
    # 获取所有分类和标签，用于筛选
    categories = Category.query.filter_by(user_id=current_user.id).all()
    tags = Tag.query.join(
        link_tags, Tag.id == link_tags.c.tag_id
    ).join(
        Link, Link.id == link_tags.c.link_id
    ).filter(
        Link.user_id == current_user.id
    ).distinct().all()
    
    return render_template('link/list.html',
                          links=links,
                          pagination=pagination,
                          categories=categories,
                          tags=tags,
                          current_category=category_id,
                          current_tag=tag_id,
                          query=query)


@link_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_link():
    """添加新链接"""
    form = LinkForm(user_id=current_user.id)
    
    # 检查用户是否有分类，如果没有，提示先创建分类
    if not form.category_id.choices:
        flash('请先创建至少一个分类', 'warning')
        return redirect(url_for('link.add_category'))
    
    if form.validate_on_submit():
        link = Link(
            title=form.title.data,
            url=form.url.data,
            description=form.description.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        
        # 添加标签
        if form.tags.data:
            tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
            link.tags = tags
        
        db.session.add(link)
        db.session.commit()
        
        flash('链接已成功添加', 'success')
        return redirect(url_for('link.list_links'))
    
    return render_template('link/add.html', form=form)


@link_bp.route('/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    """编辑链接"""
    link = Link.query.get_or_404(link_id)
    
    # 确保只能编辑自己的链接
    if link.user_id != current_user.id:
        abort(403)
    
    form = LinkForm(user_id=current_user.id, obj=link)
    
    if form.validate_on_submit():
        link.title = form.title.data
        link.url = form.url.data
        link.description = form.description.data
        link.category_id = form.category_id.data
        
        # 更新标签
        if form.tags.data:
            tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
            link.tags = tags
        else:
            link.tags = []
        
        db.session.commit()
        
        flash('链接已成功更新', 'success')
        return redirect(url_for('link.list_links'))
    elif request.method == 'GET':
        # 设置已选中的标签
        form.tags.data = [tag.id for tag in link.tags]
    
    return render_template('link/edit.html', form=form, link=link)


@link_bp.route('/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    """删除链接"""
    link = Link.query.get_or_404(link_id)
    
    # 确保只能删除自己的链接
    if link.user_id != current_user.id:
        abort(403)
    
    db.session.delete(link)
    db.session.commit()
    
    flash('链接已成功删除', 'success')
    return redirect(url_for('link.list_links'))


# 分类相关路由
@link_bp.route('/categories')
@login_required
def list_categories():
    """列出用户的所有分类"""
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('link/categories.html', categories=categories)


@link_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """添加新分类"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('分类已成功添加', 'success')
        return redirect(url_for('link.list_categories'))
    
    return render_template('link/add_category.html', form=form)


@link_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """编辑分类"""
    category = Category.query.get_or_404(category_id)
    
    # 确保只能编辑自己的分类
    if category.user_id != current_user.id:
        abort(403)
    
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        
        db.session.commit()
        
        flash('分类已成功更新', 'success')
        return redirect(url_for('link.list_categories'))
    
    return render_template('link/edit_category.html', form=form, category=category)


@link_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    
    # 确保只能删除自己的分类
    if category.user_id != current_user.id:
        abort(403)
    
    # 检查分类下是否有链接
    if Link.query.filter_by(category_id=category_id).first():
        flash('无法删除包含链接的分类', 'danger')
        return redirect(url_for('link.list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('分类已成功删除', 'success')
    return redirect(url_for('link.list_categories'))


# 标签相关路由
@link_bp.route('/tags')
@login_required
def list_tags():
    """列出所有标签"""
    # 获取所有被当前用户使用的标签
    tags = db.session.query(Tag).join(
        link_tags, Tag.id == link_tags.c.tag_id
    ).join(
        Link, Link.id == link_tags.c.link_id
    ).filter(
        Link.user_id == current_user.id
    ).distinct().all()
    
    return render_template('link/tags.html', tags=tags)


@link_bp.route('/tags/add', methods=['GET', 'POST'])
@login_required
def add_tag():
    """添加新标签"""
    form = TagForm()
    
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data,
            description=form.description.data
        )
        
        db.session.add(tag)
        db.session.commit()
        
        flash('标签已成功添加', 'success')
        return redirect(url_for('link.list_tags'))
    
    return render_template('link/add_tag.html', form=form)


@link_bp.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    """编辑标签"""
    tag = Tag.query.get_or_404(tag_id)
    
    # 检查当前用户是否使用了此标签
    user_uses_tag = db.session.query(Link).join(
        link_tags, Link.id == link_tags.c.link_id
    ).filter(
        link_tags.c.tag_id == tag_id,
        Link.user_id == current_user.id
    ).first() is not None
    
    if not user_uses_tag and not current_user.is_admin:
        abort(403)
    
    form = TagForm(obj=tag)
    
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.description = form.description.data
        
        db.session.commit()
        
        flash('标签已成功更新', 'success')
        return redirect(url_for('link.list_tags'))
    
    return render_template('link/edit_tag.html', form=form, tag=tag)
