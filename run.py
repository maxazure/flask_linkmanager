import os
from app import create_app

# 从环境变量获取配置，默认为生产配置
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # 仅在直接运行此文件时执行，不影响 Gunicorn
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8011)))
