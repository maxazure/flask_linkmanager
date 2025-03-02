from functools import wraps
from flask import request, jsonify, g
from app.models.apikey import ApiKey

def api_key_required(f):
    """
    用于API路由的装饰器，验证请求中的API密钥
    
    使用方法:
    @api_blueprint.route('/endpoint')
    @api_key_required
    def protected_endpoint():
        # 此时g.user已经被设置为API密钥对应的用户
        pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取API密钥
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': 'API密钥缺失',
                'error': 'api_key_missing'
            }), 401
        
        # 验证API密钥
        user = ApiKey.validate_key(api_key)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'API密钥无效或已过期',
                'error': 'invalid_api_key'
            }), 401
        
        # 将用户对象存储在g中，以便在视图函数中访问
        g.user = user
        
        return f(*args, **kwargs)
    
    return decorated
