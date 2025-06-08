 # 信用卡管理系统后端 API

智能化信用卡管理系统的后端API服务，基于 FastAPI + PostgreSQL 构建。

## 🚀 功能特色

- 📊 **年费管理**：灵活的年费规则配置和自动化减免条件检查
- 💳 **信用卡管理**：完整的信用卡信息管理和额度监控
- 🔔 **还款提醒**：智能还款提醒和账单管理
- 🎯 **智能推荐**：基于用户行为的个性化信用卡推荐
- 👤 **用户认证**：多种登录方式（用户名密码、手机号密码、手机号验证码、微信登录）
- 📈 **数据统计**：详细的消费分析和年费统计

## 🛠️ 技术架构

- **Web框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **认证**: JWT + bcrypt 密码哈希
- **数据验证**: Pydantic 模型验证
- **数据库迁移**: Alembic
- **异步支持**: uvicorn ASGI 服务器

## 📋 系统要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+ (可选，用于缓存)

## ⚙️ 安装配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd credit-card-manage/backend
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境配置

复制并编辑环境变量文件：

```bash
cp .env.example .env
```

主要配置项：

```bash
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/credit_card_manage

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 微信登录配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 调试模式
DEBUG=true
```

### 4. 数据库配置

确保PostgreSQL服务正在运行，然后创建数据库：

```sql
CREATE DATABASE credit_card_manage;
CREATE USER credit_card_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE credit_card_manage TO credit_card_user;
```

### 5. 初始化数据库

```bash
# 初始化数据库表结构
python start.py init

# 或者使用Alembic迁移
python start.py migrate
```

## 🚀 启动服务

### 开发模式

```bash
# 使用内置启动脚本（推荐）
python start.py dev

# 或者直接使用uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 生产模式

```bash
# 使用启动脚本
python start.py run --host 0.0.0.0 --port 8000 --workers 4

# 或者直接使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API 文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🗃️ 数据库管理

### 创建迁移

```bash
python start.py makemigrations -m "迁移描述"
```

### 执行迁移

```bash
python start.py migrate
```

### 直接使用Alembic

```bash
# 创建迁移
alembic revision --autogenerate -m "迁移描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 📁 项目结构

```
backend/
├── alembic/                # 数据库迁移文件
├── db_models/              # SQLAlchemy ORM 模型
├── models/                 # Pydantic 数据模型
├── routers/                # API 路由模块
├── services/               # 业务逻辑层
├── utils/                  # 工具函数
├── logs/                   # 日志文件
├── docs/                   # 文档
├── main.py                 # FastAPI 应用入口
├── database.py             # 数据库连接配置
├── config.py               # 应用配置
├── start.py                # 启动脚本
├── requirements.txt        # 依赖包列表
└── README.md               # 项目说明
```

## 🔍 开发指南

### 代码规范

- 使用 Pydantic 模型进行数据验证
- 所有 API 接口添加完整的类型注解和文档
- 统一使用 ResponseUtil 工具类返回响应
- 遵循分层架构：路由 -> 服务 -> 数据库
- 使用 logging 模块记录日志，禁用 print

### 新增功能

1. 在 `db_models/` 中定义数据库模型
2. 在 `models/` 中定义 Pydantic 模型
3. 在 `services/` 中实现业务逻辑
4. 在 `routers/` 中定义 API 路由
5. 在 `main.py` 中注册路由

### 测试

```bash
# 运行单元测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=.
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t credit-card-api .
```

### 运行容器

```bash
docker run -d \\
  --name credit-card-api \\
  -p 8000:8000 \\
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \\
  credit-card-api
```

### 使用 Docker Compose

在项目根目录运行：

```bash
docker-compose up -d
```

## 🔧 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证 DATABASE_URL 配置
   - 确认数据库用户权限

2. **JWT 令牌错误**
   - 检查 JWT_SECRET_KEY 配置
   - 确认令牌未过期
   - 验证令牌格式

3. **模块导入错误**
   - 确认项目路径配置
   - 检查依赖包安装
   - 验证 Python 版本

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 📝 更新日志

### v1.0.0 (2024-01-20)

- ✨ 完整的用户认证系统
- ✨ 年费管理功能
- ✨ 信用卡管理功能
- ✨ 还款提醒功能
- ✨ 智能推荐功能
- ✨ 统一的 API 响应格式
- ✨ 完善的 Swagger 文档

## 📞 联系方式

- **开发者**: LEO
- **邮箱**: leoyfm@gmail.com
- **项目仓库**: <repository-url>

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。