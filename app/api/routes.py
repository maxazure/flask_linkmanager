from flask import Blueprint, jsonify, request, g
from app import db
from app.models.link import Link, Category, Tag
from app.api.auth import api_key_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/test')
def test():
    """测试API是否正常工作"""
    return jsonify({
        'success': True,
        'message': 'API正常工作'
    })


@api_bp.route('/links', methods=['GET'])
@api_key_required
def get_links():
    """获取当前用户的链接列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)  # 限制每页最多100条
    category_id = request.args.get('category_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    
    # 基础查询：当前用户的所有链接
    query = Link.query.filter_by(user_id=g.user.id)
    
    # 按分类筛选
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # 按标签筛选
    if tag_id:
        query = query.join(Link.tags).filter(Tag.id == tag_id)
    
    # 分页
    pagination = query.order_by(Link.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    links = []
    for link in pagination.items:
        links.append({
            'id': link.id,
            'title': link.title,
            'url': link.url,
            'description': link.description,
            'created_at': link.created_at.isoformat(),
            'category': {
                'id': link.category.id,
                'name': link.category.name
            },
            'tags': [{'id': tag.id, 'name': tag.name} for tag in link.tags]
        })
    
    return jsonify({
        'success': True,
        'data': {
            'links': links,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    })


@api_bp.route('/links', methods=['POST'])
@api_key_required
def add_link():
    """添加新链接"""
    data = request.json
    
    # 验证必需字段
    if not all(key in data for key in ['title', 'url', 'category_id']):
        return jsonify({
            'success': False,
            'message': '缺少必需字段',
            'error': 'missing_fields'
        }), 400
    
    # 验证分类是否存在且属于当前用户
    category = Category.query.filter_by(id=data['category_id'], user_id=g.user.id).first()
    if not category:
        return jsonify({
            'success': False,
            'message': '分类不存在或不属于当前用户',
            'error': 'invalid_category'
        }), 400
    
    # 创建新链接
    link = Link(
        title=data['title'],
        url=data['url'],
        description=data.get('description', ''),
        category_id=data['category_id'],
        user_id=g.user.id
    )
    
    # 处理标签
    if 'tags' in data and data['tags']:
        # 获取现有标签
        tag_ids = [tag_id for tag_id in data['tags'] if isinstance(tag_id, int)]
        existing_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        
        # 创建新标签
        new_tag_names = [tag_name for tag_name in data['tags'] if isinstance(tag_name, str)]
        for tag_name in new_tag_names:
            # 检查标签是否已存在
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            existing_tags.append(tag)
        
        link.tags = existing_tags
    
    db.session.add(link)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '链接添加成功',
        'data': {
            'link': {
                'id': link.id,
                'title': link.title,
                'url': link.url,
                'description': link.description,
                'created_at': link.created_at.isoformat(),
                'category': {
                    'id': link.category.id,
                    'name': link.category.name
                },
                'tags': [{'id': tag.id, 'name': tag.name} for tag in link.tags]
            }
        }
    })


@api_bp.route('/links/<int:link_id>', methods=['GET'])
@api_key_required
def get_link(link_id):
    """获取指定链接详情"""
    link = Link.query.filter_by(id=link_id, user_id=g.user.id).first()
    
    if not link:
        return jsonify({
            'success': False,
            'message': '链接不存在或不属于当前用户',
            'error': 'link_not_found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': {
            'link': {
                'id': link.id,
                'title': link.title,
                'url': link.url,
                'description': link.description,
                'created_at': link.created_at.isoformat(),
                'category': {
                    'id': link.category.id,
                    'name': link.category.name
                },
                'tags': [{'id': tag.id, 'name': tag.name} for tag in link.tags]
            }
        }
    })


@api_bp.route('/links/<int:link_id>', methods=['PUT'])
@api_key_required
def update_link(link_id):
    """更新指定链接"""
    link = Link.query.filter_by(id=link_id, user_id=g.user.id).first()
    
    if not link:
        return jsonify({
            'success': False,
            'message': '链接不存在或不属于当前用户',
            'error': 'link_not_found'
        }), 404
    
    data = request.json
    
    # 更新链接字段
    if 'title' in data:
        link.title = data['title']
    if 'url' in data:
        link.url = data['url']
    if 'description' in data:
        link.description = data['description']
    
    # 更新分类
    if 'category_id' in data:
        category = Category.query.filter_by(id=data['category_id'], user_id=g.user.id).first()
        if not category:
            return jsonify({
                'success': False,
                'message': '分类不存在或不属于当前用户',
                'error': 'invalid_category'
            }), 400
        link.category_id = data['category_id']
    
    # 更新标签
    if 'tags' in data:
        # 获取现有标签
        tag_ids = [tag_id for tag_id in data['tags'] if isinstance(tag_id, int)]
        existing_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
        
        # 创建新标签
        new_tag_names = [tag_name for tag_name in data['tags'] if isinstance(tag_name, str)]
        for tag_name in new_tag_names:
            # 检查标签是否已存在
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            existing_tags.append(tag)
        
        link.tags = existing_tags
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '链接更新成功',
        'data': {
            'link': {
                'id': link.id,
                'title': link.title,
                'url': link.url,
                'description': link.description,
                'created_at': link.created_at.isoformat(),
                'category': {
                    'id': link.category.id,
                    'name': link.category.name
                },
                'tags': [{'id': tag.id, 'name': tag.name} for tag in link.tags]
            }
        }
    })


@api_bp.route('/links/<int:link_id>', methods=['DELETE'])
@api_key_required
def delete_link(link_id):
    """删除指定链接"""
    link = Link.query.filter_by(id=link_id, user_id=g.user.id).first()
    
    if not link:
        return jsonify({
            'success': False,
            'message': '链接不存在或不属于当前用户',
            'error': 'link_not_found'
        }), 404
    
    db.session.delete(link)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '链接删除成功'
    })


@api_bp.route('/categories', methods=['GET'])
@api_key_required
def get_categories():
    """获取当前用户的所有分类"""
    categories = Category.query.filter_by(user_id=g.user.id).all()
    
    return jsonify({
        'success': True,
        'data': {
            'categories': [{
                'id': category.id,
                'name': category.name,
                'description': category.description
            } for category in categories]
        }
    })


@api_bp.route('/tags', methods=['GET'])
@api_key_required
def get_tags():
    """获取当前用户使用的所有标签"""
    # 获取用户使用的所有标签
    tags = db.session.query(Tag).join(
        Link.tags
    ).filter(
        Link.user_id == g.user.id
    ).distinct().all()
    
    return jsonify({
        'success': True,
        'data': {
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'description': tag.description
            } for tag in tags]
        }
    })


@api_bp.route('/user', methods=['GET'])
@api_key_required
def get_user_info():
    """获取当前用户信息"""
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': g.user.id,
                'username': g.user.username,
                'email': g.user.email,
                'created_at': g.user.created_at.isoformat()
            }
        }
    })
