# 信用卡管理系统架构设计 v2.0

**版本**: v2.0  
**架构师**: LEO  
**邮箱**: leoyfm@gmail.com  
**设计时间**: 2024年12月

## 🏗️ 架构概览

### 设计原则
- **分层架构**: 清晰的层次分离，低耦合高内聚
- **微服务理念**: 模块化设计，独立部署和扩展
- **安全第一**: 三级权限控制，数据完全隔离
- **测试驱动**: 新测试框架v2.0，90%+覆盖率
- **API优先**: RESTful API设计，版本控制
- **可观测性**: 全面监控、日志和追踪

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
├─────────────────────────────────────────────────────────────┤
│ Web Frontend │ Mobile App │ Admin Panel │ Third-party APIs │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                            │
├─────────────────────────────────────────────────────────────┤
│    Rate Limiting │ Load Balancing │ SSL Termination         │
│    Authentication │ Authorization │ Request Routing         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  /api/v1/public/  │  /api/v1/user/  │  /api/v1/admin/      │
│   (Level 1)       │    (Level 2)    │    (Level 3)         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Business Layer                           │
├─────────────────────────────────────────────────────────────┤
│ Auth Service │ User Service │ Card Service │ Admin Service  │
│ Stats Service │ Notification │ Annual Fee │ Recommendation │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL  │    Redis     │   File Storage │  External   │
│  (Primary)   │   (Cache)    │   (Assets)     │   APIs      │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目目录结构

### 新项目结构
```
credit-card-manage/
├── backend/                          # 后端API服务
│   ├── app/                         # 应用核心
│   │   ├── api/                     # API层
│   │   │   ├── v1/                  # API v1版本
│   │   │   │   ├── public/          # 公开接口 (Level 1)
│   │   │   │   │   ├── auth.py      # 认证相关
│   │   │   │   │   └── system.py    # 系统信息
│   │   │   │   ├── user/            # 用户接口 (Level 2)
│   │   │   │   │   ├── profile.py   # 个人资料
│   │   │   │   │   ├── cards.py     # 信用卡管理
│   │   │   │   │   ├── transactions.py # 交易管理
│   │   │   │   │   ├── annual_fees.py # 年费管理
│   │   │   │   │   ├── reminders.py # 还款提醒
│   │   │   │   │   ├── statistics.py # 个人统计
│   │   │   │   │   └── recommendations.py # 推荐
│   │   │   │   └── admin/           # 管理员接口 (Level 3)
│   │   │   │       ├── dashboard.py # 管理面板
│   │   │   │       ├── users.py     # 用户管理
│   │   │   │       ├── system.py    # 系统管理
│   │   │   │       ├── content.py   # 内容管理
│   │   │   │       └── analytics.py # 数据分析
│   │   │   └── dependencies/        # API依赖
│   │   │       ├── auth.py          # 认证依赖
│   │   │       ├── permissions.py   # 权限依赖
│   │   │       └── database.py      # 数据库依赖
│   │   ├── core/                    # 核心组件
│   │   │   ├── config.py            # 配置管理
│   │   │   ├── security.py          # 安全组件
│   │   │   ├── logging/             # 日志服务
│   │   │   │   ├── __init__.py      # 日志初始化
│   │   │   │   ├── logger.py        # 日志记录器
│   │   │   │   ├── formatters.py    # 日志格式化
│   │   │   │   ├── handlers.py      # 日志处理器
│   │   │   │   └── filters.py       # 日志过滤器
│   │   │   ├── exceptions/          # 异常处理
│   │   │   │   ├── __init__.py      # 异常初始化
│   │   │   │   ├── handlers.py      # 全局异常处理器
│   │   │   │   ├── custom.py        # 自定义异常类
│   │   │   │   └── responses.py     # 异常响应格式
│   │   │   └── middleware/          # 中间件
│   │   │       ├── auth.py          # 认证中间件
│   │   │       ├── cors.py          # CORS中间件
│   │   │       ├── rate_limit.py    # 限流中间件
│   │   │       ├── audit.py         # 审计中间件
│   │   │       ├── logging.py       # 日志中间件
│   │   │       └── exception.py     # 异常处理中间件
│   │   ├── services/                # 业务服务层
│   │   │   ├── auth_service.py      # 认证服务
│   │   │   ├── user_service.py      # 用户服务
│   │   │   ├── card_service.py      # 信用卡服务
│   │   │   ├── transaction_service.py # 交易服务
│   │   │   ├── annual_fee_service.py # 年费服务
│   │   │   ├── reminder_service.py  # 提醒服务
│   │   │   ├── statistics_service.py # 统计服务
│   │   │   ├── notification_service.py # 通知服务
│   │   │   └── recommendation_service.py # 推荐服务
│   │   ├── models/                  # 数据模型
│   │   │   ├── database/            # 数据库模型
│   │   │   │   ├── user.py          # 用户模块模型
│   │   │   │   ├── card.py          # 信用卡模块模型
│   │   │   │   ├── transaction.py   # 交易模块模型
│   │   │   │   ├── annual_fee.py    # 年费模块模型
│   │   │   │   ├── reminder.py      # 提醒模块模型
│   │   │   │   ├── statistics.py    # 统计模块模型
│   │   │   │   ├── system.py        # 系统配置模型
│   │   │   │   └── recommendation.py # 推荐模块模型
│   │   │   └── schemas/             # API模型
│   │   │       ├── auth.py          # 认证相关模型
│   │   │       ├── user.py          # 用户相关模型
│   │   │       ├── card.py          # 信用卡相关模型
│   │   │       ├── transaction.py   # 交易相关模型
│   │   │       ├── annual_fee.py    # 年费相关模型
│   │   │       ├── reminder.py      # 提醒相关模型
│   │   │       ├── statistics.py    # 统计相关模型
│   │   │       ├── admin.py         # 管理员相关模型
│   │   │       └── common.py        # 通用模型
│   │   ├── utils/                   # 工具类
│   │   │   ├── response.py          # 统一响应格式
│   │   │   ├── pagination.py        # 分页工具
│   │   │   ├── datetime.py          # 时间工具
│   │   │   ├── security.py          # 安全工具
│   │   │   ├── validators.py        # 验证器
│   │   │   └── constants.py         # 常量定义
│   │   └── db/                      # 数据库相关
│   │       ├── database.py          # 数据库连接
│   │       ├── session.py           # 会话管理
│   │       └── base.py              # 基础模型
│   ├── alembic/                     # 数据库迁移
│   │   ├── versions/                # 迁移版本
│   │   ├── env.py                   # 迁移环境
│   │   └── script.py.mako           # 迁移模板
│   ├── tests/                       # 测试套件
│   │   ├── framework/               # 测试框架v2.0
│   │   │   ├── core/                # 核心组件
│   │   │   │   ├── runner.py        # 智能运行器
│   │   │   │   ├── suite.py         # 测试套件
│   │   │   │   └── assertion.py     # 断言系统
│   │   │   ├── clients/             # 测试客户端
│   │   │   │   ├── api.py           # 流畅API客户端
│   │   │   │   └── database.py      # 数据库客户端
│   │   │   ├── decorators/          # 装饰器系统
│   │   │   │   ├── test.py          # 测试装饰器
│   │   │   │   ├── data.py          # 数据装饰器
│   │   │   │   └── performance.py   # 性能装饰器
│   │   │   ├── factories/           # 数据工厂
│   │   │   │   ├── user_factory.py  # 用户数据工厂
│   │   │   │   ├── card_factory.py  # 信用卡数据工厂
│   │   │   │   └── transaction_factory.py # 交易数据工厂
│   │   │   └── utils/               # 测试工具
│   │   ├── suites/                  # 测试套件
│   │   │   ├── api/                 # API测试套件
│   │   │   ├── integration/         # 集成测试套件
│   │   │   ├── performance/         # 性能测试套件
│   │   │   └── e2e/                # 端到端测试套件
│   │   └── config/                  # 测试配置
│   ├── scripts/                     # 脚本工具
│   │   ├── init_db.py              # 数据库初始化
│   │   ├── seed_data.py            # 种子数据
│   │   └── migration.py            # 迁移脚本
│   ├── docs/                       # 文档
│   │   ├── api/                    # API文档
│   │   ├── architecture/           # 架构文档
│   │   └── deployment/             # 部署文档
│   ├── main.py                     # 应用入口
│   ├── requirements.txt            # 依赖文件
│   ├── alembic.ini                # Alembic配置
│   └── Dockerfile                 # Docker配置
├── mobile/                        # 移动端应用
├── nginx/                         # Nginx配置
├── postgresql/                    # PostgreSQL配置
├── monitoring/                    # 监控配置
│   ├── prometheus/                # Prometheus配置
│   ├── grafana/                   # Grafana配置
│   └── elk/                       # ELK Stack配置
├── deployment/                    # 部署配置
│   ├── docker-compose.yml         # Docker编排
│   ├── k8s/                       # Kubernetes配置
│   └── scripts/                   # 部署脚本
└── docs/                          # 项目文档
    ├── README.md                  # 项目说明
    ├── API_REFERENCE.md           # API参考
    └── USER_GUIDE.md              # 用户指南
```

## 🔐 安全架构设计

### 认证授权架构
```python
# 三级权限控制体系
Permission_Levels = {
    "Level 1 - Public": {
        "access": "无需认证",
        "endpoints": ["/api/v1/public/*"],
        "examples": ["注册", "登录", "系统信息"]
    },
    "Level 2 - User": {
        "access": "用户认证",
        "endpoints": ["/api/v1/user/*"],
        "data_scope": "仅自有数据",
        "examples": ["个人资料", "信用卡管理", "交易记录"]
    },
    "Level 3 - Admin": {
        "access": "管理员认证",
        "endpoints": ["/api/v1/admin/*"],
        "data_scope": "系统级数据（脱敏）",
        "examples": ["用户管理", "系统配置", "数据分析"]
    }
}

# JWT令牌结构
JWT_Structure = {
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "sub": "user_id",
        "username": "username",
        "role": "user|admin",
        "permissions": ["read:own", "write:own"],
        "exp": "过期时间",
        "iat": "签发时间"
    },
    "signature": "安全签名"
}
```

### 数据访问控制
```python
# 数据访问控制矩阵
Data_Access_Matrix = {
    "User_Data": {
        "owner": "CRUD",      # 用户自己：完全控制
        "admin": "R(脱敏)",    # 管理员：只读脱敏数据
        "other_user": "拒绝"   # 其他用户：完全拒绝
    },
    "System_Data": {
        "user": "R(限制)",     # 普通用户：有限只读
        "admin": "CRUD"       # 管理员：完全控制
    },
    "Public_Data": {
        "anonymous": "R",     # 匿名用户：只读
        "user": "R",          # 认证用户：只读
        "admin": "CRUD"       # 管理员：完全控制
    }
}
```

## 📋 日志服务架构设计

### 统一日志系统
```python
# 多层日志架构
Logging_Architecture = {
    "应用日志": {
        "格式": "结构化JSON",
        "级别": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "输出": ["控制台", "文件", "ELK Stack"],
        "轮转": "每日轮转，保留30天"
    },
    "访问日志": {
        "内容": ["请求路径", "响应状态", "耗时", "用户ID", "IP地址"],
        "格式": "Apache Combined + 自定义字段",
        "存储": "Nginx日志 + 应用日志双重记录"
    },
    "审计日志": {
        "触发": ["敏感操作", "权限变更", "数据修改"],
        "字段": ["用户ID", "操作类型", "资源ID", "前后值", "时间戳", "IP"],
        "存储": "独立审计表 + 日志文件"
    },
    "错误日志": {
        "捕获": "全局异常处理器自动捕获",
        "包含": ["异常类型", "调用栈", "请求上下文", "用户信息"],
        "通知": "严重错误自动告警"
    },
    "性能日志": {
        "监控": ["API响应时间", "数据库查询耗时", "外部调用延迟"],
        "阈值": "超过500ms自动记录",
        "分析": "慢查询优化建议"
    }
}

# 日志格式标准
Log_Format = {
    "timestamp": "2024-12-01T10:00:00.123Z",
    "level": "INFO",
    "logger": "api.user.profile",
    "trace_id": "abc123def456",
    "span_id": "789xyz",
    "user_id": "uuid-string",
    "request_id": "req-uuid",
    "method": "GET",
    "path": "/api/v1/user/profile",
    "status_code": 200,
    "duration_ms": 45,
    "ip_address": "192.168.1.100",
    "user_agent": "Mobile App v1.0",
    "message": "用户资料查询成功",
    "extra_data": {
        "module": "用户管理",
        "action": "查询资料",
        "result": "成功"
    }
}
```

### 日志服务组件
```python
# 日志记录器配置
Logger_Configuration = {
    "root": {
        "level": "INFO",
        "handlers": ["console", "file", "elk"]
    },
    "api": {
        "level": "INFO",
        "handlers": ["api_file", "elk"],
        "propagate": False
    },
    "database": {
        "level": "WARNING",
        "handlers": ["db_file", "elk"],
        "propagate": False
    },
    "security": {
        "level": "INFO",
        "handlers": ["security_file", "alert"],
        "propagate": False
    },
    "performance": {
        "level": "INFO",
        "handlers": ["perf_file", "metrics"],
        "propagate": False
    }
}

# 日志处理器
Log_Handlers = {
    "console": {
        "class": "StreamHandler",
        "formatter": "colored",
        "level": "DEBUG"
    },
    "file": {
        "class": "RotatingFileHandler",
        "filename": "logs/app.log",
        "maxBytes": 50*1024*1024,  # 50MB
        "backupCount": 30,
        "formatter": "json"
    },
    "elk": {
        "class": "ELKHandler",
        "endpoint": "http://logstash:5000",
        "formatter": "elk_json"
    },
    "alert": {
        "class": "SlackHandler",
        "webhook_url": "${SLACK_WEBHOOK}",
        "level": "ERROR"
    }
}
```

### 链路追踪集成
```python
# 分布式追踪
Distributed_Tracing = {
    "追踪ID生成": "每个请求生成唯一trace_id",
    "跨服务传递": "HTTP头部传递追踪信息",
    "数据库查询": "自动记录SQL执行时间",
    "外部调用": "HTTP客户端自动追踪",
    "异步任务": "Celery任务追踪支持",
    "存储": "Jaeger后端存储",
    "查询": "Grafana界面查询分析"
}
```

## ⚠️ 全局错误处理架构

### 异常处理层次
```python
# 四层异常处理架构
Exception_Hierarchy = {
    "系统异常": {
        "类型": ["DatabaseError", "ConnectionError", "ConfigError"],
        "处理": "自动重试 + 降级处理 + 告警",
        "响应": "500 Internal Server Error",
        "日志": "CRITICAL级别记录"
    },
    "业务异常": {
        "类型": ["ValidationError", "BusinessRuleError", "StateError"],
        "处理": "业务逻辑处理 + 用户友好提示",
        "响应": "400 Bad Request",
        "日志": "WARNING级别记录"
    },
    "权限异常": {
        "类型": ["AuthenticationError", "AuthorizationError", "PermissionError"],
        "处理": "安全审计 + 限流处理",
        "响应": "401/403错误",
        "日志": "ERROR级别 + 安全日志"
    },
    "客户端异常": {
        "类型": ["InvalidParameter", "MissingField", "FormatError"],
        "处理": "参数校验 + 详细错误信息",
        "响应": "422 Unprocessable Entity",
        "日志": "INFO级别记录"
    }
}

# 自定义异常类设计
Custom_Exceptions = {
    "BaseAPIException": "所有API异常的基类",
    "AuthenticationError": "认证失败异常",
    "AuthorizationError": "授权失败异常", 
    "ValidationError": "数据验证异常",
    "BusinessRuleError": "业务规则异常",
    "ResourceNotFoundError": "资源不存在异常",
    "ResourceConflictError": "资源冲突异常",
    "RateLimitError": "请求限流异常",
    "ExternalServiceError": "外部服务异常",
    "DatabaseError": "数据库操作异常"
}
```

### 错误响应标准化
```python
# 统一错误响应格式
Error_Response_Format = {
    "success": False,
    "code": 400,
    "message": "请求参数错误",
    "error_code": "VALIDATION_ERROR",
    "error_detail": {
        "field": "email",
        "message": "邮箱格式不正确",
        "invalid_value": "invalid-email"
    },
    "trace_id": "abc123def456",
    "timestamp": "2024-12-01T10:00:00Z",
    "request_id": "req-uuid-123",
    "help_url": "https://api-docs.example.com/errors/validation"
}

# 错误码规范
Error_Codes = {
    # 认证授权错误 (1xxx)
    "AUTH_REQUIRED": 1001,          # 需要认证
    "AUTH_INVALID": 1002,           # 认证无效
    "AUTH_EXPIRED": 1003,           # 认证过期
    "PERMISSION_DENIED": 1004,      # 权限不足
    
    # 请求参数错误 (2xxx)
    "VALIDATION_ERROR": 2001,       # 参数验证失败
    "MISSING_PARAMETER": 2002,      # 缺少必需参数
    "INVALID_FORMAT": 2003,         # 格式错误
    "PARAMETER_OUT_OF_RANGE": 2004, # 参数超出范围
    
    # 业务逻辑错误 (3xxx)
    "RESOURCE_NOT_FOUND": 3001,     # 资源不存在
    "RESOURCE_CONFLICT": 3002,      # 资源冲突
    "BUSINESS_RULE_VIOLATION": 3003, # 业务规则违反
    "STATE_ERROR": 3004,            # 状态错误
    
    # 系统错误 (5xxx)
    "INTERNAL_ERROR": 5001,         # 内部错误
    "DATABASE_ERROR": 5002,         # 数据库错误
    "EXTERNAL_SERVICE_ERROR": 5003, # 外部服务错误
    "RATE_LIMIT_EXCEEDED": 5004     # 请求频率超限
}
```

### 异常处理流程
```python
# 全局异常处理器
Exception_Handler_Flow = {
    "1.异常捕获": {
        "位置": "全局异常中间件",
        "覆盖": "所有未处理异常",
        "记录": "完整调用栈 + 请求上下文"
    },
    "2.异常分类": {
        "判断": "异常类型自动识别",
        "映射": "异常类 -> 错误码 -> 响应格式",
        "路由": "不同异常类型的处理策略"
    },
    "3.日志记录": {
        "级别": "根据异常严重程度自动分级",
        "内容": "异常详情 + 用户信息 + 请求信息",
        "存储": "文件日志 + ELK Stack + Sentry"
    },
    "4.用户通知": {
        "脱敏": "隐藏内部实现细节",
        "友好": "用户友好的错误描述",
        "指导": "提供解决方案或帮助链接"
    },
    "5.系统恢复": {
        "重试": "可重试异常自动重试",
        "降级": "服务降级策略",
        "熔断": "防止雪崩效应"
    },
    "6.告警通知": {
        "触发": "严重异常自动触发告警",
        "渠道": "Slack/邮件/短信多渠道",
        "升级": "无人响应自动升级"
    }
}
```

### 异常监控和告警
```python
# 实时异常监控
Exception_Monitoring = {
    "实时统计": {
        "指标": ["异常总数", "异常率", "错误类型分布"],
        "时间窗口": "1分钟/5分钟/1小时",
        "可视化": "Grafana实时仪表板"
    },
    "告警规则": {
        "异常率告警": "1分钟内异常率 > 5%",
        "系统异常告警": "任何500错误立即告警",
        "连续异常告警": "同一接口连续10次异常",
        "新异常告警": "出现新类型异常"
    },
    "自动恢复": {
        "熔断器": "连续异常触发熔断保护",
        "限流降级": "异常峰值时自动限流",
        "服务重启": "严重异常自动重启服务"
    },
    "异常分析": {
        "趋势分析": "异常趋势和周期性分析",
        "根因分析": "自动关联日志分析根因",
        "优化建议": "基于异常模式的优化建议"
    }
}
```

## 🗄️ 数据库架构设计

### 模块化数据库设计
```sql
-- 8大核心模块，17个表，220个字段

-- 1. 用户模块 (4个表)
users (15字段)               -- 用户基础信息
verification_codes (7字段)    -- 验证码管理
login_logs (9字段)           -- 登录日志
wechat_bindings (9字段)      -- 微信绑定

-- 2. 银行信用卡模块 (2个表)
banks (7字段)                -- 银行信息
credit_cards (28字段)        -- 信用卡信息

-- 3. 年费管理模块 (2个表)
fee_waiver_rules (16字段)    -- 年费减免规则
annual_fee_records (17字段)  -- 年费记录

-- 4. 交易管理模块 (2个表)
transaction_categories (8字段) -- 交易分类
transactions (15字段)         -- 交易记录

-- 5. 还款提醒模块 (2个表)
reminder_settings (15字段)    -- 提醒设置
reminder_logs (13字段)        -- 提醒日志

-- 6. 统计分析模块 (1个表)
user_statistics (16字段)      -- 用户统计

-- 7. 系统配置模块 (2个表)
system_configs (8字段)        -- 系统配置
notification_templates (9字段) -- 通知模板

-- 8. 智能推荐模块 (2个表)
recommendation_rules (11字段) -- 推荐规则
recommendation_records (11字段) -- 推荐记录
```

### 数据库连接架构
```python
Database_Architecture = {
    "主数据库": {
        "类型": "PostgreSQL 15+",
        "用途": "业务数据存储",
        "连接池": "50个连接",
        "备份": "每日增量 + 每周全量"
    },
    "缓存层": {
        "类型": "Redis 7+",
        "用途": "Session存储、API缓存",
        "策略": "LRU淘汰",
        "持久化": "RDB + AOF"
    },
    "文件存储": {
        "类型": "MinIO/AWS S3",
        "用途": "头像、附件存储",
        "CDN": "CloudFlare加速"
    }
}
```

## 🧪 测试架构设计

### 新测试框架v2.0架构
```python
# 四层测试架构
Testing_Architecture = {
    "单元测试": {
        "工具": "新测试框架 + FastAPITestClient",
        "覆盖": "API层、Service层",
        "目标": "> 95%覆盖率",
        "装饰器": "@api_test, @with_user, @with_cards"
    },
    "集成测试": {
        "工具": "RequestsTestClient + 真实HTTP",
        "覆盖": "端到端业务流程",
        "目标": "核心业务100%覆盖",
        "装饰器": "@test_scenario, @requires_server"
    },
    "性能测试": {
        "工具": "@performance_test, @stress_test",
        "指标": "响应时间、并发、吞吐量",
        "基准": "< 500ms响应，1000+并发",
        "自动化": "CI/CD集成"
    },
    "安全测试": {
        "工具": "OWASP ZAP + 自定义脚本",
        "覆盖": "权限验证、注入攻击、XSS",
        "目标": "零安全漏洞",
        "频率": "每次发布前"
    }
}

# 测试数据工厂
Test_Data_Factories = {
    "UserFactory": "自动创建测试用户",
    "CardFactory": "自动创建信用卡数据",
    "TransactionFactory": "批量创建交易记录",
    "AnnualFeeFactory": "年费规则和记录",
    "ReminderFactory": "提醒设置数据"
}
```

### 测试执行流程
```python
# 智能测试运行器
Test_Runner_Features = {
    "自动发现": "tests/suites/目录自动扫描",
    "智能执行": "标签过滤、优先级排序、并行执行",
    "数据管理": "自动创建、关联、清理测试数据",
    "报告生成": "控制台、HTML、JSON多格式报告",
    "持续集成": "GitHub Actions集成"
}
```

## 🌐 API架构设计

### RESTful API设计
```python
# API版本控制
API_Versioning = {
    "URL版本": "/api/v1/",
    "向后兼容": "6个月兼容期",
    "版本映射": "自动路由转换",
    "废弃通知": "响应头警告"
}

# 三级路由架构
API_Routes = {
    "/api/v1/public/": {
        "权限": "Level 1 - 无需认证",
        "功能": ["用户注册", "登录", "系统信息"],
        "限流": "100请求/分钟"
    },
    "/api/v1/user/": {
        "权限": "Level 2 - 用户认证",
        "功能": ["个人管理", "信用卡", "交易", "统计"],
        "限流": "500请求/分钟",
        "数据范围": "仅自有数据"
    },
    "/api/v1/admin/": {
        "权限": "Level 3 - 管理员认证",
        "功能": ["用户管理", "系统配置", "数据分析"],
        "限流": "1000请求/分钟",
        "数据范围": "系统级数据（脱敏）"
    }
}
```

### 统一响应格式
```python
# 标准响应结构
Response_Format = {
    "success": True,
    "code": 200,
    "message": "操作成功",
    "data": {},
    "pagination": {  # 分页时
        "current_page": 1,
        "page_size": 20,
        "total": 100,
        "total_pages": 5
    },
    "timestamp": "2024-12-01T10:00:00Z"
}

# 错误响应结构
Error_Response = {
    "success": False,
    "code": 400,
    "message": "参数错误",
    "error_detail": "具体错误描述",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2024-12-01T10:00:00Z"
}
```

## 🚀 部署架构设计

### 容器化部署
```yaml
# Docker容器架构
Services:
  api:
    image: "credit-card-api:latest"
    replicas: 3
    resources:
      memory: "512Mi"
      cpu: "500m"
    
  database:
    image: "postgres:15"
    volumes:
      - "pg_data:/var/lib/postgresql/data"
    
  cache:
    image: "redis:7-alpine"
    volumes:
      - "redis_data:/data"
    
  nginx:
    image: "nginx:alpine"
    ports:
      - "80:80"
      - "443:443"
```

### 监控和日志
```python
# 可观测性架构
Observability = {
    "应用监控": {
        "工具": "Prometheus + Grafana",
        "指标": ["API响应时间", "错误率", "吞吐量", "并发连接数"],
        "告警": "Slack/邮件/短信多渠道通知",
        "仪表板": "实时性能监控面板"
    },
    "日志管理": {
        "工具": "ELK Stack (Elasticsearch + Logstash + Kibana)",
        "格式": "结构化JSON + 链路追踪信息",
        "级别": "DEBUG/INFO/WARNING/ERROR/CRITICAL",
        "存储": "热数据7天，温数据30天，冷数据90天",
        "索引": "按日期和服务分片索引",
        "搜索": "全文搜索 + 字段过滤"
    },
    "链路追踪": {
        "工具": "Jaeger",
        "覆盖": "API请求全链路 + 数据库查询 + 外部调用",
        "采样": "错误100%，正常10%采样率",
        "保留": "7天详细数据，30天聚合数据"
    },
    "错误追踪": {
        "工具": "Sentry",
        "覆盖": "异常自动捕获 + 性能监控",
        "通知": "实时告警 + 日报周报",
        "分析": "错误趋势分析 + 影响评估"
    },
    "业务监控": {
        "工具": "自定义指标 + Grafana",
        "指标": ["用户活跃度", "交易成功率", "核心业务流程"],
        "告警": "业务异常自动告警",
        "报表": "自动生成业务报表"
    }
}
```

## 📈 性能架构设计

### 缓存策略
```python
# 多层缓存架构
Cache_Strategy = {
    "L1_应用缓存": {
        "工具": "functools.lru_cache",
        "用途": "配置数据、静态数据",
        "TTL": "300秒"
    },
    "L2_Redis缓存": {
        "工具": "Redis",
        "用途": "Session、API响应",
        "TTL": "1800秒",
        "策略": "LRU淘汰"
    },
    "L3_CDN缓存": {
        "工具": "CloudFlare",
        "用途": "静态资源、API响应",
        "TTL": "3600秒"
    }
}
```

### 数据库优化
```sql
-- 索引优化策略
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_cards_user_id ON credit_cards(user_id);
CREATE INDEX idx_transactions_card_date ON transactions(card_id, transaction_date);
CREATE INDEX idx_login_logs_user_time ON login_logs(user_id, created_at);

-- 复合索引
CREATE INDEX idx_credit_cards_expiry ON credit_cards(expiry_year, expiry_month);
CREATE INDEX idx_annual_fee_records_card_year ON annual_fee_records(card_id, fee_year);
```

## 🔒 安全强化措施

### 安全中间件栈
```python
Security_Middleware = [
    "RequestLoggingMiddleware",    # 请求日志记录 (最先执行)
    "ExceptionHandlerMiddleware",  # 全局异常处理 (异常捕获)
    "CORSMiddleware",              # 跨域控制
    "SecurityHeadersMiddleware",   # 安全头设置
    "RateLimitMiddleware",         # 请求限流
    "AuthenticationMiddleware",    # 认证验证
    "AuthorizationMiddleware",     # 权限检查
    "AuditLogMiddleware",          # 审计日志
    "PerformanceMiddleware"        # 性能监控 (最后执行)
]

# 中间件执行顺序和职责
Middleware_Pipeline = {
    "请求阶段": [
        "RequestLogging -> 记录请求开始",
        "Security -> 设置安全头",
        "CORS -> 处理跨域",
        "RateLimit -> 检查请求频率",
        "Authentication -> 验证身份",
        "Authorization -> 检查权限",
        "Performance -> 开始计时"
    ],
    "响应阶段": [
        "Performance -> 记录响应时间",
        "AuditLog -> 记录敏感操作",
        "RequestLogging -> 记录请求完成",
        "ExceptionHandler -> 处理任何异常"
    ]
}

# 数据保护措施
Data_Protection = {
    "传输加密": "HTTPS/TLS 1.3",
    "存储加密": "AES-256数据库字段加密",
    "密码保护": "bcrypt + salt",
    "敏感数据脱敏": "信用卡号、身份证号",
    "审计日志": "所有敏感操作记录"
}
```

---

**联系人**: LEO (leoyfm@gmail.com)  
**架构版本**: v2.0  
**最后更新**: 2024年12月 