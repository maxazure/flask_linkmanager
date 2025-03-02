#!/bin/bash
# 简化的启动脚本 - 仅启动应用，不执行数据库测试和迁移

set -e

echo "准备启动 Flask LinkManager 应用..."

# 根据环境启动应用
if [ "$FLASK_ENV" = "development" ]; then
    echo "启动开发环境服务器..."
    flask run --host=0.0.0.0 --port=8011
else
    echo "启动生产环境服务器 (Gunicorn)..."
    # 增加访问日志和错误日志输出
    gunicorn --bind 0.0.0.0:8011 \
             --workers 4 \
             --timeout 120 \
             --access-logfile - \
             --error-logfile - \
             --log-level info \
             run:app
fi
