# 链接管理系统

一个简单高效的链接收藏、整理与分享工具，基于Flask框架开发。

## 功能特点

- **链接管理**：保存、编辑、删除和查看您喜爱的网页链接
- **分类系统**：创建自定义分类，对链接进行组织
- **标签系统**：使用灵活的标签，从多个维度标记链接
- **用户系统**：用户注册、登录、个人资料管理
- **API接口**：与浏览器插件集成，一键保存当前浏览页面
- **管理后台**：全面的后台管理功能

## 技术栈

- **后端**：Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF, Flask-RESTful, Flask-Admin
- **数据库**：SQLite(开发)/PostgreSQL(生产)
- **前端**：Bootstrap, jQuery, Font Awesome, Select2
- **认证**：JWT Token, Flask-Login

## 安装与配置

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/maxazure/flask-linkmanager.git
cd flask-linkmanager
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置环境变量：

```bash
cp .env.example .env
# 编辑.env文件，设置SECRET_KEY和其他配置
```

5. 初始化数据库：

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. 创建管理员用户：

```bash
python create_admin.py
```

7. 运行应用：

```bash
flask run
```

## 使用指南

### 用户功能

- 注册/登录账户
- 添加、编辑、删除链接
- 创建和管理分类与标签
- 生成API密钥用于浏览器插件

### 管理员功能

- 用户管理
- 所有链接、分类、标签的管理
- 系统设置

## API接口

系统提供RESTful API，用于与外部应用（如浏览器插件）集成：

- `/api/v1/links` - 获取和添加链接
- `/api/v1/categories` - 获取分类
- `/api/v1/tags` - 获取标签

所有API请求需要在Header中包含API密钥：

```
X-API-Key: your-api-key-here


curl -X POST \
  http://localhost:5000/api/v1/links \
  -H "X-API-Key: 566193bfeb16a4e64b240d670176efbcd557b42be8652f271932448e01f5b2f3" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Link",
    "url": "https://example.com",
    "category_id": 1,
    "description": "An example link description"
  }'
```


### 获取链接
```
curl -X GET \
  "http://localhost:5000/api/v1/links" \
   -H "X-API-Key: 566193bfeb16a4e64b240d670176efbcd557b42be8652f271932448e01f5b2f3" 

```


## 浏览器插件

计划开发Chrome和Firefox浏览器插件，实现一键保存当前浏览页面功能。

## 数据库迁移指南：从SQLite迁移到MySQL

本项目支持使用SQLite或MySQL作为数据库。以下是从SQLite迁移到MySQL的详细指南。

### 前置条件

1. 已安装MySQL服务器
2. 已安装必要的Python依赖
   ```bash
   pip install -r requirements.txt
   ```
3. 已配置`.env`文件中的MySQL连接参数

### 第一步：创建MySQL数据库和用户

```sql
CREATE DATABASE linkmanager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'linkmanager'@'%' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON linkmanager.* TO 'linkmanager'@'%';
FLUSH PRIVILEGES;
```

### 第二步：配置环境变量

确保您的`.env`文件包含以下配置：

```
DB_TYPE=mysql
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=linkmanager
MYSQL_PASSWORD=your_password
MYSQL_DB=linkmanager
```

### 第三步：创建表结构

启动应用程序创建表结构：

```bash
flask run
```

应用启动时会自动使用SQLAlchemy创建必要的表结构。

### 第四步：数据迁移

使用内置的数据迁移脚本将数据从SQLite迁移到MySQL：

```bash
python migrate_db.py
```

#### 迁移选项

迁移脚本支持以下选项：

1. **默认模式**：保留MySQL中已有数据，仅添加不存在的数据
   ```bash
   python migrate_db.py
   ```

2. **替换模式**：如果主键冲突，使用新数据替换旧数据
   ```bash
   python migrate_db.py --replace
   ```

3. **清空模式**：在迁移前清空目标表
   ```bash
   python migrate_db.py --clear
   ```

4. **清空并替换模式**：先清空表，再导入所有数据
   ```bash
   python migrate_db.py --clear --replace
   ```

### 数据安全说明

- 默认情况下，迁移脚本使用`INSERT IGNORE`语法，确保不会覆盖MySQL中现有的数据
- `--replace`选项将使用`REPLACE INTO`语法，当主键冲突时会覆盖现有数据
- `--clear`选项会在插入前清空表，请谨慎使用

### 验证迁移结果

迁移完成后，您可以通过以下方式验证数据：

1. 登录MySQL客户端查看数据
   ```bash
   mysql -u linkmanager -p linkmanager
   ```

2. 在MySQL中执行查询语句
   ```sql
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM links;
   -- 等其他必要的验证查询
   ```

3. 启动应用程序并验证功能是否正常

### 故障排除

如果遇到数据迁移问题，请检查：

1. MySQL连接参数是否正确
2. MySQL用户是否有适当的权限
3. 表结构是否正确创建
4. 迁移脚本的错误输出

### 回滚到SQLite

如果需要回滚到SQLite，只需在`.env`文件中将`DB_TYPE`设置回`sqlite`：

```
DB_TYPE=sqlite
```

然后重启应用程序，系统将自动使用SQLite数据库。

## 贡献指南

欢迎为项目提供贡献！请遵循以下步骤：

1. Fork项目仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT License
