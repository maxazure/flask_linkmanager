# 数据库迁移指南

本文档详细说明了如何将Flask Link Manager的数据库从SQLite迁移到MySQL。

## 迁移步骤

### 1. 配置MySQL服务器

首先，您需要创建MySQL数据库和用户：

```sql
CREATE DATABASE linkmanager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'linkmanager'@'%' IDENTIFIED BY 'mwhZAW7pWyDBHrWE';
GRANT ALL PRIVILEGES ON linkmanager.* TO 'linkmanager'@'%';
FLUSH PRIVILEGES;
```

### 2. 安装所需依赖

确保安装了所需的Python库：

```bash
pip install pymysql cryptography
```

或者更新所有依赖：

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

修改`.env`文件，设置数据库类型为MySQL：

```properties
DB_TYPE=mysql
MYSQL_HOST=192.168.31.205
MYSQL_PORT=3306
MYSQL_USER=linkmanager
MYSQL_PASSWORD=mwhZAW7pWyDBHrWE
MYSQL_DB=linkmanager
```

### 4. 创建表结构

启动应用程序，让SQLAlchemy创建表结构：

```bash
flask run
```

### 5. 执行数据迁移

使用提供的迁移脚本将数据从SQLite导入到MySQL：

```bash
python migrate_db.py
```

## 迁移脚本选项

迁移脚本支持以下命令行选项：

| 选项 | 说明 |
|------|------|
| `--replace` | 当遇到主键冲突时，使用新数据替换旧数据 |
| `--clear` | 在导入数据前清空目标表 |

### 使用示例

1. 安全迁移（保留现有数据）：
   ```bash
   python migrate_db.py
   ```

2. 替换模式（覆盖冲突数据）：
   ```bash
   python migrate_db.py --replace
   ```

3. 清空表后迁移：
   ```bash
   python migrate_db.py --clear
   ```

4. 清空表并使用替换模式：
   ```bash
   python migrate_db.py --clear --replace
   ```

## 数据迁移原理

迁移脚本执行以下操作：

1. 连接源SQLite数据库和目标MySQL数据库
2. 获取SQLite中的所有表名
3. 对每个表：
   - 获取表结构和数据
   - 根据选项决定是否清空表
   - 使用`INSERT IGNORE`或`REPLACE INTO`将数据导入MySQL
4. 输出迁移状态和结果

## 故障排查

如果您在迁移过程中遇到问题，请检查：

1. MySQL服务器是否可访问
2. 用户名和密码是否正确
3. 用户是否有足够的权限
4. 数据库和表是否正确创建

常见错误信息及解决方法：

- **"Access denied"**：检查MySQL用户名和密码
- **"Table doesn't exist"**：确保应用已启动并创建了表结构
- **"Duplicate entry"**：考虑使用`--replace`选项或解决数据冲突

## 验证迁移成功

迁移完成后，可通过以下方式验证：

1. 检查迁移脚本输出，确认每个表的数据行数
2. 使用MySQL客户端检查数据
3. 启动应用并测试功能

## 回滚计划

如需回滚到SQLite，只需更改`.env`文件：

```properties
DB_TYPE=sqlite
```

然后重启应用程序。
