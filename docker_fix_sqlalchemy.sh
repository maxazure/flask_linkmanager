#!/bin/bash

# 修复容器内的 SQLAlchemy 版本兼容问题
CONTAINER_NAME="flask_linkmanager"

echo "在容器 $CONTAINER_NAME 中修复 SQLAlchemy 兼容问题..."

# 在容器中安装兼容版本的 SQLAlchemy
docker exec $CONTAINER_NAME pip install SQLAlchemy==1.4.46 Flask-SQLAlchemy==2.5.1

echo "完成！请重启容器以应用更改:"
echo "docker restart $CONTAINER_NAME"
