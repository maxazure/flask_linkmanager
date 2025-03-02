FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制应用代码
COPY . .

# 设置启动脚本权限
RUN chmod +x start.sh

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8011

# 使用启动脚本
CMD ["./start.sh"]
