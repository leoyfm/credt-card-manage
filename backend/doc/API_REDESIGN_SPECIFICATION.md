# 信用卡管理系统 API 重设计规范文档

**文档版本**: v1.0  
**创建日期**: 2024年12月  
**作者**: LEO  
**邮箱**: leoyfm@gmail.com  

## 📋 文档概述

本文档详细描述了信用卡管理系统后端API的重新设计方案，重点关注为普通用户和系统管理员两个不同角色提供差异化的服务。通过清晰的权限分离、数据隔离和功能划分，确保系统的安全性、可维护性和用户体验。

## 🎯 设计目标

### 1. 核心目标
- **角色分离**: 明确区分普通用户和管理员的功能边界
- **数据安全**: 确保用户数据隐私和系统数据安全
- **权限控制**: 实现细粒度的权限管理机制
- **用户体验**: 为不同角色提供最优的API使用体验
- **系统可维护**: 清晰的架构设计便于后续扩展维护

### 2. 设计原则
- **最小权限原则**: 用户只能访问必需的功能和数据
- **数据隔离原则**: 用户数据完全隔离，管理员数据统计化
- **功能分离原则**: 业务功能和管理功能完全分离
- **安全优先原则**: 所有设计都以安全为首要考虑
- **扩展性原则**: 预留足够的扩展空间

## 🏗️ 系统架构设计

### 1. 角色定义

#### 1.1 普通用户 (User)
**角色描述**: 个人信用卡管理者，使用系统管理自己的信用卡相关信息

**核心职责**:
- 管理个人信用卡信息
- 记录和分析个人交易数据
- 设置和管理还款提醒
- 配置个人年费规则
- 查看个人统计分析
- 接收智能推荐服务

**权限范围**:
- 完全控制自己的数据（CRUD）
- 只能查看自己的信息
- 无法访问其他用户数据
- 无法执行系统管理操作

#### 1.2 系统管理员 (Admin)
**角色描述**: 系统运营和管理者，负责用户管理和系统维护

**核心职责**:
- 管理系统用户账户
- 监控系统运行状态
- 维护系统配置参数
- 分析业务数据和趋势
- 管理系统内容和公告
- 处理系统安全事务

**权限范围**:
- 查看和管理所有用户账户
- 访问系统统计和分析数据
- 修改系统配置和参数
- 查看系统日志和监控数据
- 发布系统公告和内容
- 不能查看用户敏感数据详情

### 2. 权限等级设计

#### Level 1: 公开访问
- 无需认证即可访问
- 包括注册、登录、系统信息等
- 数据完全公开或无敏感信息

#### Level 2: 用户认证访问
- 需要有效的用户令牌
- 只能访问自己的数据
- 执行个人数据管理操作

#### Level 3: 管理员权限访问
- 需要管理员角色令牌
- 可以执行系统管理操作
- 访问系统级统计和配置数据

## 🛤️ API路由架构重设计

### 1. 版本控制设计

#### 1.1 版本控制策略
- **版本格式**: 使用语义化版本控制，格式为 `v{major}.{minor}`
- **URL格式**: `/api/v{major}/`，例如 `/api/v1/`、`/api/v2/`
- **版本兼容**: 同一主版本内保持向后兼容，跨主版本可能有破坏性变更
- **版本生命周期**: 新版本发布后，旧版本保持6个月支持期

#### 1.2 版本规划
- **v1.0**: 当前重设计版本，包含完整用户和管理员功能
- **v2.0**: 预留扩展版本，可能包含新的业务模块或重大架构调整

### 2. 路由结构总览

```
/api/v1/
├── public/                    # 公开接口（Level 1）
├── user/                      # 用户功能区（Level 2）
└── admin/                     # 管理员功能区（Level 3）
```

### 3. 版本兼容性处理

#### 3.1 版本头支持
```http
# 方式1: URL路径版本（推荐）
GET /api/v1/user/cards/list

# 方式2: Accept头版本（可选）
GET /api/user/cards/list
Accept: application/vnd.api+json;version=1
```

#### 3.2 版本废弃通知
```json
{
  "success": true,
  "data": {...},
  "warnings": [
    {
      "code": "DEPRECATED_API",
      "message": "此API版本将在2025年6月后停止支持，请升级到v2版本",
      "upgrade_url": "/api/v2/user/cards/list"
    }
  ]
}
```

### 4. 公开接口区 (/api/v1/public/)

#### 4.1 认证相关 (/api/v1/public/auth/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| POST | `/register` | 用户注册 | Level 1 |
| POST | `/login/username` | 用户名登录 | Level 1 |
| POST | `/login/phone` | 手机号登录 | Level 1 |
| POST | `/login/wechat` | 微信登录 | Level 1 |
| POST | `/send-code` | 发送验证码 | Level 1 |
| POST | `/verify-code` | 验证验证码 | Level 1 |
| POST | `/reset-password` | 重置密码 | Level 1 |
| POST | `/refresh-token` | 刷新令牌 | Level 1 |

#### 4.2 系统信息 (/api/v1/public/system/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/health` | 健康检查 | Level 1 |
| GET | `/version` | 版本信息 | Level 1 |
| GET | `/status` | 服务状态 | Level 1 |

### 5. 用户功能区 (/api/v1/user/)

#### 5.1 个人资料 (/api/v1/user/profile/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/info` | 获取个人信息 | Level 2 |
| PUT | `/update` | 更新个人资料 | Level 2 |
| POST | `/change-password` | 修改密码 | Level 2 |
| GET | `/login-logs` | 个人登录日志 | Level 2 |
| POST | `/logout` | 退出登录 | Level 2 |
| DELETE | `/account` | 注销账户 | Level 2 |

#### 5.2 信用卡管理 (/api/v1/user/cards/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/list` | 我的信用卡列表 | Level 2 |
| POST | `/create` | 添加信用卡 | Level 2 |
| GET | `/{card_id}/details` | 信用卡详情 | Level 2 |
| PUT | `/{card_id}/update` | 更新信用卡 | Level 2 |
| DELETE | `/{card_id}/delete` | 删除信用卡 | Level 2 |
| PUT | `/{card_id}/status` | 更新卡片状态 | Level 2 |

#### 5.3 交易管理 (/api/v1/user/transactions/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/list` | 我的交易列表 | Level 2 |
| POST | `/create` | 记录新交易 | Level 2 |
| GET | `/{transaction_id}/details` | 交易详情 | Level 2 |
| PUT | `/{transaction_id}/update` | 更新交易 | Level 2 |
| DELETE | `/{transaction_id}/delete` | 删除交易 | Level 2 |
| GET | `/categories` | 交易分类 | Level 2 |

#### 5.4 年费管理 (/api/v1/user/annual-fees/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/rules` | 我的年费规则 | Level 2 |
| POST | `/rules/create` | 创建年费规则 | Level 2 |
| PUT | `/rules/{rule_id}/update` | 更新年费规则 | Level 2 |
| DELETE | `/rules/{rule_id}/delete` | 删除年费规则 | Level 2 |
| GET | `/records` | 年费记录 | Level 2 |

#### 5.5 还款提醒 (/api/v1/user/reminders/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/list` | 我的提醒列表 | Level 2 |
| POST | `/create` | 创建提醒 | Level 2 |
| PUT | `/{reminder_id}/update` | 更新提醒 | Level 2 |
| DELETE | `/{reminder_id}/delete` | 删除提醒 | Level 2 |
| POST | `/{reminder_id}/snooze` | 延后提醒 | Level 2 |

#### 5.6 个人统计 (/api/v1/user/statistics/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/overview` | 个人数据总览 | Level 2 |
| GET | `/cards` | 个人信用卡统计 | Level 2 |
| GET | `/transactions` | 个人交易统计 | Level 2 |
| GET | `/annual-fees` | 个人年费统计 | Level 2 |
| GET | `/monthly-trends` | 个人月度趋势 | Level 2 |
| GET | `/categories` | 个人分类统计 | Level 2 |

#### 5.7 智能推荐 (/api/v1/user/recommendations/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/cards` | 信用卡推荐 | Level 2 |
| GET | `/offers` | 优惠推荐 | Level 2 |
| POST | `/feedback` | 推荐反馈 | Level 2 |
| GET | `/history` | 推荐历史 | Level 2 |

### 6. 管理员功能区 (/api/v1/admin/)

#### 6.1 管理面板 (/api/v1/admin/dashboard/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/overview` | 系统总览 | Level 3 |
| GET | `/metrics` | 关键指标 | Level 3 |
| GET | `/alerts` | 系统警报 | Level 3 |
| GET | `/activity` | 系统活动 | Level 3 |

#### 6.2 用户管理 (/api/v1/admin/users/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/list` | 用户列表 | Level 3 |
| GET | `/{user_id}/details` | 用户详情 | Level 3 |
| PUT | `/{user_id}/status` | 用户状态管理 | Level 3 |
| PUT | `/{user_id}/permissions` | 权限管理 | Level 3 |
| GET | `/{user_id}/login-logs` | 用户登录日志 | Level 3 |
| DELETE | `/{user_id}/delete` | 删除用户 | Level 3 |
| GET | `/statistics` | 用户统计 | Level 3 |

#### 6.3 系统管理 (/api/v1/admin/system/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/config` | 系统配置 | Level 3 |
| PUT | `/config` | 更新配置 | Level 3 |
| GET | `/logs` | 系统日志 | Level 3 |
| GET | `/monitoring` | 系统监控 | Level 3 |
| POST | `/maintenance` | 系统维护 | Level 3 |

#### 6.4 内容管理 (/api/v1/admin/content/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/cards-database` | 信用卡数据库 | Level 3 |
| POST | `/cards-database` | 添加卡片信息 | Level 3 |
| GET | `/offers` | 优惠活动 | Level 3 |
| POST | `/offers` | 创建优惠活动 | Level 3 |
| GET | `/announcements` | 系统公告 | Level 3 |
| POST | `/announcements` | 发布公告 | Level 3 |

#### 6.5 数据分析 (/api/v1/admin/analytics/)

| 方法 | 路径 | 描述 | 权限等级 |
|------|------|------|----------|
| GET | `/user-behavior` | 用户行为分析 | Level 3 |
| GET | `/transaction-trends` | 交易趋势分析 | Level 3 |
| GET | `/card-performance` | 卡片性能分析 | Level 3 |
| GET | `/system-reports` | 系统报告 | Level 3 |

## 🔐 权限控制详细设计

### 1. 认证机制

#### 1.1 JWT令牌结构

```json
{
  "sub": "user_id",
  "username": "username",
  "role": "user|admin",
  "permissions": ["read:own", "write:own"],
  "exp": 1734567890,
  "iat": 1734567890
}
```

#### 1.2 权限依赖函数

```python
# 基础认证
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """获取当前认证用户"""

# 管理员权限检查
async def require_admin(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """要求管理员权限"""
    if not current_user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return current_user

# 用户或管理员权限检查
async def require_user_or_admin(
    target_user_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """要求是目标用户本人或管理员"""
    if current_user.id != target_user_id and not current_user.is_admin:
        raise HTTPException(403, "权限不足")
    return current_user

# 自有资源访问检查
async def require_resource_owner(
    resource_user_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """要求资源所有者权限"""
    if current_user.id != resource_user_id:
        raise HTTPException(403, "只能访问自己的资源")
    return current_user
```

### 2. 数据访问控制

#### 2.1 用户数据访问策略

```python
class UserDataAccessControl:
    """用户数据访问控制"""
    
    @staticmethod
    def filter_user_data(query, user_id: UUID):
        """过滤用户数据，只返回属于该用户的数据"""
        return query.filter(User.id == user_id)
    
    @staticmethod
    def validate_resource_ownership(resource, user_id: UUID):
        """验证资源所有权"""
        if resource.user_id != user_id:
            raise HTTPException(403, "资源不属于当前用户")
```

#### 2.2 管理员数据访问策略

```python
class AdminDataAccessControl:
    """管理员数据访问控制"""
    
    @staticmethod
    def get_user_summary(user_id: UUID):
        """获取用户摘要信息（不包含敏感详情）"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
            # 不包含具体的交易记录、密码等敏感信息
            "cards_count": user.cards.count(),
            "transactions_count": user.transactions.count()
        }
    
    @staticmethod
    def get_system_statistics():
        """获取系统统计数据"""
        return {
            "total_users": db.query(User).count(),
            "active_users": db.query(User).filter(User.is_active == True).count(),
            "total_transactions": db.query(Transaction).count(),
            # 只统计数量，不涉及具体内容
        }
```

## 📊 数据模型设计

### 1. 响应格式标准化

#### 1.1 成功响应格式

```python
class ApiResponse(BaseModel):
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

#### 1.2 分页响应格式

```python
class ApiPagedResponse(BaseModel):
    success: bool = True
    code: int = 200
    message: str = "查询成功"
    data: List[Any] = []
    pagination: PaginationInfo
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class PaginationInfo(BaseModel):
    current_page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
```

#### 1.3 错误响应格式

```python
class ApiErrorResponse(BaseModel):
    success: bool = False
    code: int
    message: str
    error_detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

### 2. 权限相关模型

#### 2.1 用户权限模型

```python
class UserPermissions(BaseModel):
    can_read_own_data: bool = True
    can_write_own_data: bool = True
    can_delete_own_data: bool = True
    can_view_statistics: bool = True

class AdminPermissions(BaseModel):
    can_manage_users: bool = True
    can_view_system_data: bool = True
    can_modify_system_config: bool = True
    can_access_analytics: bool = True
```

## 🛡️ 安全设计

### 1. 认证安全

#### 1.1 令牌管理
- **访问令牌过期时间**: 2小时
- **刷新令牌过期时间**: 30天
- **令牌黑名单机制**: 支持令牌撤销
- **设备绑定**: 可选的设备ID验证

#### 1.2 密码安全
- **密码强度要求**: 至少8位，包含字母数字
- **密码加密**: 使用bcrypt加密存储
- **登录尝试限制**: 5次失败后临时锁定
- **密码历史**: 防止重复使用最近的密码

### 2. 授权安全

#### 2.1 权限验证
- **令牌有效性检查**: 每次请求验证令牌
- **权限等级检查**: 严格按照等级进行权限验证
- **资源所有权验证**: 确保用户只能访问自己的资源
- **操作审计**: 记录所有重要操作

#### 2.2 数据保护
- **敏感数据脱敏**: 返回数据时隐藏敏感信息
- **传输加密**: 强制使用HTTPS
- **数据完整性**: 防止数据篡改
- **访问日志**: 详细记录数据访问日志

### 3. 系统安全

#### 3.1 防护机制
- **SQL注入防护**: 使用ORM和参数化查询
- **XSS防护**: 输入验证和输出转义
- **CSRF防护**: 使用CSRF令牌
- **DDoS防护**: 请求频率限制

#### 3.2 监控告警
- **异常登录检测**: 检测异常登录行为
- **权限提升检测**: 检测权限提升尝试
- **数据访问监控**: 监控异常数据访问
- **系统健康监控**: 实时监控系统状态

## 🚀 实施计划

### 第一阶段：架构重构（2-3周）

#### 1.1 版本控制和路由重组
- [ ] 创建v1版本路由结构 (/api/v1/)
- [ ] 迁移现有接口到新版本路由
- [ ] 实现版本兼容性检查中间件
- [ ] 实现权限中间件
- [ ] 更新接口文档（包含版本信息）

#### 1.2 权限系统
- [ ] 实现认证依赖函数
- [ ] 添加权限验证逻辑
- [ ] 创建数据访问控制类
- [ ] 测试权限验证

#### 1.3 用户功能区
- [ ] 重构用户个人资料接口
- [ ] 迁移信用卡管理接口
- [ ] 迁移交易管理接口
- [ ] 更新统计接口

### 第二阶段：管理功能（2-3周）

#### 2.1 管理员面板
- [ ] 实现系统总览接口
- [ ] 创建关键指标接口
- [ ] 添加系统警报功能
- [ ] 实现活动监控

#### 2.2 用户管理
- [ ] 重构用户管理接口
- [ ] 添加权限管理功能
- [ ] 实现用户统计分析
- [ ] 创建操作审计日志

#### 2.3 系统管理
- [ ] 实现系统配置管理
- [ ] 添加系统日志查看
- [ ] 创建监控告警系统
- [ ] 实现维护模式

### 第三阶段：优化完善（1-2周）

#### 3.1 性能优化
- [ ] 数据库查询优化
- [ ] 缓存策略实现
- [ ] 接口响应时间优化
- [ ] 并发处理优化

#### 3.2 安全加固
- [ ] 安全测试和修复
- [ ] 权限测试完善
- [ ] 审计日志完善
- [ ] 监控告警调优

#### 3.3 文档和测试
- [ ] 完善API文档
- [ ] 编写用户指南
- [ ] 完善测试用例
- [ ] 性能测试

## 📚 开发规范

### 1. 代码规范

#### 1.1 路由定义规范
```python
# 用户功能路由示例（v1版本）
@router.get(
    "/list",
    response_model=ApiPagedResponse[CardResponse],
    summary="获取我的信用卡列表",
    description="获取当前用户的所有信用卡，支持分页和筛选",
    tags=["v1-用户-信用卡管理"]
)
async def get_my_cards(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的信用卡列表 - API v1"""
```

#### 1.2 权限检查规范
```python
# 每个需要权限的接口都应该明确检查权限
async def update_card(
    card_id: UUID,
    card_data: CardUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 获取资源
    card = cards_service.get_card_by_id(card_id)
    if not card:
        raise HTTPException(404, "信用卡不存在")
    
    # 2. 权限检查
    if card.user_id != current_user.id:
        raise HTTPException(403, "只能修改自己的信用卡")
    
    # 3. 执行操作
    return cards_service.update_card(card_id, card_data)
```

### 2. 测试规范

#### 2.1 用户功能测试
```python
class TestUserCards:
    def test_get_my_cards_success(self):
        """测试获取用户信用卡成功 - v1 API"""
        response = self.client.get("/api/v1/user/cards/list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "pagination" in data

    def test_get_other_user_cards_forbidden(self):
        """测试无法获取其他用户的信用卡 - v1 API"""
        # 尝试访问其他用户的资源应该被拒绝
        other_card_id = "other-user-card-id"
        response = self.client.get(f"/api/v1/user/cards/{other_card_id}/details", 
                                  headers=self.headers)
        assert response.status_code == 403
```

#### 2.2 管理员功能测试
```python
class TestAdminUsers:
    def test_admin_get_users_list(self):
        """测试管理员获取用户列表 - v1 API"""
        response = self.client.get("/api/v1/admin/users/list", headers=self.admin_headers)
        assert response.status_code == 200
        
    def test_user_cannot_access_admin_endpoint(self):
        """测试普通用户无法访问管理员接口 - v1 API"""
        response = self.client.get("/api/v1/admin/users/list", headers=self.user_headers)
        assert response.status_code == 403
```

## 📖 API使用示例

### 1. 用户功能使用示例

#### 1.1 用户注册和登录
```bash
# 用户注册
curl -X POST "http://localhost:8000/api/v1/public/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "nickname": "新用户"
  }'

# 用户登录
curl -X POST "http://localhost:8000/api/v1/public/auth/login/username" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "SecurePass123"
  }'
```

#### 1.2 管理个人信用卡
```bash
# 获取我的信用卡列表
curl -X GET "http://localhost:8000/api/v1/user/cards/list?page=1&page_size=10" \
  -H "Authorization: Bearer <user_token>"

# 添加新信用卡
curl -X POST "http://localhost:8000/api/v1/user/cards/create" \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "4111111111111111",
    "card_name": "我的主卡",
    "bank_name": "招商银行",
    "credit_limit": 50000,
    "expiry_month": 12,
    "expiry_year": 2027
  }'
```

#### 1.3 查看个人统计
```bash
# 获取个人数据总览
curl -X GET "http://localhost:8000/api/v1/user/statistics/overview" \
  -H "Authorization: Bearer <user_token>"

# 获取月度趋势
curl -X GET "http://localhost:8000/api/v1/user/statistics/monthly-trends?months=6" \
  -H "Authorization: Bearer <user_token>"
```

### 2. 管理员功能使用示例

#### 2.1 用户管理
```bash
# 获取用户列表
curl -X GET "http://localhost:8000/api/v1/admin/users/list?page=1&page_size=20" \
  -H "Authorization: Bearer <admin_token>"

# 修改用户状态
curl -X PUT "http://localhost:8000/api/v1/admin/users/{user_id}/status" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

#### 2.2 系统监控
```bash
# 获取系统总览
curl -X GET "http://localhost:8000/api/v1/admin/dashboard/overview" \
  -H "Authorization: Bearer <admin_token>"

# 获取系统配置
curl -X GET "http://localhost:8000/api/v1/admin/system/config" \
  -H "Authorization: Bearer <admin_token>"
```

## 🔧 配置参数

### 1. 认证配置
```python
# JWT配置
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2小时
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30     # 30天

# 密码配置
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_SPECIAL_CHARS = False
LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_MINUTES = 15
```

### 2. 权限配置
```python
# 权限级别
PERMISSION_LEVELS = {
    "PUBLIC": 1,
    "USER": 2,
    "ADMIN": 3
}

# 默认权限
DEFAULT_USER_PERMISSIONS = [
    "read:own_profile",
    "write:own_profile",
    "read:own_cards",
    "write:own_cards"
]

DEFAULT_ADMIN_PERMISSIONS = [
    "read:all_users",
    "write:user_status",
    "read:system_config",
    "write:system_config"
]
```

### 3. 系统配置
```python
# API配置
API_RATE_LIMIT = "100/minute"
API_RESPONSE_TIMEOUT = 30  # 秒
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

# 安全配置
HTTPS_ONLY = True
CORS_ORIGINS = ["http://localhost:3000"]
ENABLE_AUDIT_LOG = True
```

## 📋 检查清单

### 1. 架构实施检查
- [ ] 路由结构是否按照设计实现
- [ ] 权限验证是否在每个接口正确实施
- [ ] 数据访问是否正确隔离
- [ ] 响应格式是否统一标准化

### 2. 安全检查
- [ ] 所有用户数据是否正确隔离
- [ ] 管理员权限是否正确限制
- [ ] 敏感信息是否正确脱敏
- [ ] 认证令牌是否安全管理

### 3. 功能检查
- [ ] 用户功能是否完整迁移
- [ ] 管理员功能是否正确实现
- [ ] 公开接口是否正常工作
- [ ] 错误处理是否完善

### 4. 性能检查
- [ ] 接口响应时间是否满足要求
- [ ] 数据库查询是否优化
- [ ] 缓存策略是否有效
- [ ] 并发处理是否稳定

### 5. 文档检查
- [ ] API文档是否完整更新
- [ ] 使用示例是否正确
- [ ] 权限说明是否清晰
- [ ] 迁移指南是否完善

## 📞 联系信息

**项目负责人**: LEO  
**邮箱**: leoyfm@gmail.com  
**文档版本**: v1.0  
**最后更新**: 2024年12月

---

*本文档将随着项目进展持续更新，请关注最新版本。* 