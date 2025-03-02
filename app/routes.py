import json
from flask import jsonify, send_file
from datetime import datetime
import io
import os

# ...existing code...

@app.route('/api/export', methods=['GET'])
@jwt_required()
def export_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # 获取用户的所有链接
    links = Link.query.filter_by(user_id=current_user_id).all()
    
    # 获取用户的所有分类
    categories = Category.query.filter_by(user_id=current_user_id).all()
    
    # 准备导出数据
    export_data = {
        "categories": [],
        "links": []
    }
    
    for category in categories:
        export_data["categories"].append({
            "name": category.name,
            "description": category.description
        })
    
    for link in links:
        export_data["links"].append({
            "url": link.url,
            "title": link.title,
            "description": link.description,
            "category_id": link.category_id,
            "category_name": Category.query.get(link.category_id).name if link.category_id else None
        })
    
    # 创建内存文件
    mem_file = io.BytesIO()
    mem_file.write(json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8'))
    mem_file.seek(0)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"linkmanager_backup_{timestamp}.json"
    
    # 发送文件
    return send_file(
        mem_file,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/import', methods=['POST'])
@jwt_required()
def import_data():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({"msg": "File must be JSON format"}), 400
    
    try:
        # 读取上传的JSON文件
        import_data = json.loads(file.read().decode('utf-8'))
        
        # 添加分类
        category_map = {}  # 用于存储旧分类名到新分类ID的映射
        for category_data in import_data.get("categories", []):
            # 检查分类是否已存在
            existing_category = Category.query.filter_by(
                name=category_data["name"], 
                user_id=current_user_id
            ).first()
            
            if existing_category:
                category_map[category_data["name"]] = existing_category.id
            else:
                new_category = Category(
                    name=category_data["name"],
                    description=category_data.get("description", ""),
                    user_id=current_user_id
                )
                db.session.add(new_category)
                db.session.flush()  # 获取新插入记录的ID
                category_map[category_data["name"]] = new_category.id
        
        # 添加链接
        for link_data in import_data.get("links", []):
            category_id = None
            if link_data.get("category_name") and link_data["category_name"] in category_map:
                category_id = category_map[link_data["category_name"]]
            elif link_data.get("category_id"):
                # 检查该分类ID是否属于当前用户
                category = Category.query.filter_by(
                    id=link_data["category_id"], 
                    user_id=current_user_id
                ).first()
                if category:
                    category_id = category.id
            
            # 检查链接是否已存在
            existing_link = Link.query.filter_by(
                url=link_data["url"], 
                user_id=current_user_id
            ).first()
            
            if not existing_link:
                new_link = Link(
                    url=link_data["url"],
                    title=link_data.get("title", ""),
                    description=link_data.get("description", ""),
                    category_id=category_id,
                    user_id=current_user_id
                )
                db.session.add(new_link)
        
        db.session.commit()
        return jsonify({"msg": "Data imported successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error importing data: {str(e)}"}), 500

# ...existing code...
