# 测试数据工厂使用指南

## 概述

测试数据工厂提供了一套简洁的API来生成各种测试数据，支持信用卡管理系统的所有核心实体。每个工厂都遵循相同的设计模式，提供灵活的数据生成能力。

## 设计原则

1. **简洁易用**: 提供合理的默认值，只需要覆盖必要的字段
2. **灵活定制**: 支持通过参数覆盖任何字段
3. **类型安全**: 使用类型注解，提供良好的IDE支持
4. **模板支持**: 预定义常用的数据模板
5. **批量生成**: 支持批量生成测试数据

## 可用的数据工厂

### 1. 用户工厂 (`user_factory.py`)

#### 基础函数
- `build_user(**kwargs)` - 构建完整的用户数据
- `build_simple_user(**kwargs)` - 构建简化的用户数据（仅必需字段）
- `build_admin_user(**kwargs)` - 构建管理员用户数据
- `build_verified_user(**kwargs)` - 构建已验证的用户数据
- `build_inactive_user(**kwargs)` - 构建未激活的用户数据

#### 批量和模板函数
- `build_users_batch(count=3, **kwargs)` - 批量生成用户
- `build_template_user(template_name, **kwargs)` - 使用模板生成用户

#### 使用示例
```python
from tests.factories.user_factory import build_user, build_simple_user, build_template_user

# 基础用户
user = build_user()

# 简单用户（仅必需字段）
simple_user = build_simple_user()

# 自定义用户
custom_user = build_user(
    username="testuser123",
    email="test@example.com",
    nickname="测试用户"
)

# 使用模板
admin = build_template_user("管理员")
normal_user = build_template_user("普通用户")
```

### 2. 信用卡工厂 (`card_factory.py`)

#### 基础函数
- `build_card(**kwargs)` - 构建完整的信用卡数据
- `build_simple_card(**kwargs)` - 构建简化的信用卡数据
- `build_premium_card(**kwargs)` - 构建高端信用卡数据
- `build_expired_card(**kwargs)` - 构建已过期的信用卡数据

#### 批量和模板函数
- `build_cards_batch(count=3, **kwargs)` - 批量生成信用卡
- `build_template_card(template_name, **kwargs)` - 使用模板生成信用卡

#### 可用模板
- "招商经典白金" - 招商银行经典白金卡
- "建行龙卡" - 建设银行龙卡信用卡
- "浦发AE白" - 浦发银行AE白金卡

#### 使用示例
```python
from tests.factories.card_factory import build_card, build_template_card, build_cards_batch

# 基础信用卡
card = build_card()

# 自定义信用卡
custom_card = build_card(
    card_name="我的测试卡",
    bank_name="招商银行",
    credit_limit=Decimal("100000.00")
)

# 使用模板
cmb_card = build_template_card("招商经典白金")

# 批量生成
cards = build_cards_batch(count=5)
```

### 3. 交易工厂 (`transaction_factory.py`)

#### 基础函数
- `build_transaction(**kwargs)` - 构建完整的交易数据
- `build_simple_transaction(**kwargs)` - 构建简化的交易数据
- `build_large_transaction(**kwargs)` - 构建大额交易数据
- `build_refund_transaction(**kwargs)` - 构建退款交易数据
- `build_pending_transaction(**kwargs)` - 构建待处理交易数据

#### 批量和时间函数
- `build_transactions_batch(count=5, **kwargs)` - 批量生成交易
- `build_monthly_transactions(year, month, count=10, **kwargs)` - 生成指定月份的交易
- `build_template_transaction(template_name, **kwargs)` - 使用模板生成交易

#### 可用模板
- "餐饮" - 餐饮消费交易
- "加油" - 加油站消费交易
- "购物" - 购物消费交易
- "旅行" - 旅行相关交易

#### 使用示例
```python
from tests.factories.transaction_factory import build_transaction, build_template_transaction

# 基础交易
transaction = build_transaction()

# 自定义交易
custom_transaction = build_transaction(
    amount=Decimal("500.00"),
    merchant_name="星巴克",
    merchant_category="餐饮美食"
)

# 使用模板
dining_transaction = build_template_transaction("餐饮")

# 生成指定月份的交易
monthly_transactions = build_monthly_transactions(2024, 12, count=20)
```

### 4. 年费工厂 (`annual_fee_factory.py`)

#### 规则函数
- `build_fee_waiver_rule(**kwargs)` - 构建年费减免规则
- `build_spending_rule(**kwargs)` - 构建消费金额减免规则
- `build_transaction_count_rule(**kwargs)` - 构建交易次数减免规则
- `build_points_redeem_rule(**kwargs)` - 构建积分兑换减免规则

#### 记录函数
- `build_annual_fee_record(**kwargs)` - 构建年费记录
- `build_paid_fee_record(**kwargs)` - 构建已缴费记录
- `build_waived_fee_record(**kwargs)` - 构建已减免记录
- `build_overdue_fee_record(**kwargs)` - 构建逾期记录

#### 批量和模板函数
- `build_fee_rules_batch(count=3, **kwargs)` - 批量生成规则
- `build_fee_records_batch(count=3, **kwargs)` - 批量生成记录
- `build_template_fee_rule(template_name, **kwargs)` - 使用模板生成规则
- `build_template_fee_record(template_name, **kwargs)` - 使用模板生成记录

#### 使用示例
```python
from tests.factories.annual_fee_factory import (
    build_spending_rule, build_template_fee_record
)

# 消费减免规则
rule = build_spending_rule(
    condition_value=Decimal("50000.00"),
    description="年消费满5万免年费"
)

# 使用模板生成年费记录
fee_record = build_template_fee_record("白金卡年费")
```

## 在测试中的使用

### 1. API测试示例

```python
def test_create_card(self, user_and_api):
    """测试创建信用卡"""
    api, user = user_and_api
    
    # 使用工厂生成测试数据
    card_data = build_simple_card(
        card_name="测试卡",
        bank_name="测试银行"
    )
    
    resp = api.post("/api/v1/user/cards/create", card_data)
    assert_response(resp).success()
```

### 2. 单元测试示例

```python
def test_card_service_create(self, db_session):
    """测试信用卡服务创建功能"""
    # 创建测试用户
    user_data = build_simple_user()
    user = create_user_in_db(db_session, user_data)
    
    # 创建测试卡片
    card_data = build_simple_card()
    card = card_service.create_card(user.id, card_data)
    
    assert card.card_name == card_data["card_name"]
```

### 3. 复杂场景测试

```python
def test_annual_fee_calculation(self, user_and_api):
    """测试年费计算"""
    api, user = user_and_api
    
    # 创建信用卡
    card_data = build_template_card("招商经典白金")
    card_resp = api.post("/api/v1/user/cards/create", card_data)
    card_id = card_resp.json()["data"]["id"]
    
    # 创建年费减免规则
    rule_data = build_spending_rule(
        condition_value=Decimal("50000.00")
    )
    api.post(f"/api/v1/user/cards/{card_id}/fee-rules", rule_data)
    
    # 创建足够的交易记录
    transactions = build_monthly_transactions(2024, 12, count=20)
    for transaction in transactions:
        transaction["card_id"] = card_id
        api.post("/api/v1/user/transactions/create", transaction)
    
    # 验证年费计算结果
    resp = api.get(f"/api/v1/user/cards/{card_id}/annual-fee/2024")
    assert_response(resp).success()
```

## 最佳实践

### 1. 数据隔离
- 每个测试使用独立的数据
- 使用随机生成的用户名和邮箱避免冲突
- 测试完成后自动清理数据

### 2. 合理使用模板
- 对于常见场景使用预定义模板
- 对于特殊测试需求使用自定义参数
- 保持模板的简洁和实用性

### 3. 批量数据生成
- 对于需要大量数据的测试使用批量函数
- 注意控制数据量，避免测试运行时间过长
- 使用有意义的数据分布

### 4. 参数覆盖
- 只覆盖测试关注的字段
- 保持其他字段使用默认值
- 使用描述性的参数名

## 扩展指南

### 添加新的数据工厂

1. 创建新的工厂文件，如 `reminder_factory.py`
2. 遵循现有的命名约定：`build_*`, `build_simple_*`, `build_template_*`
3. 提供合理的默认值和类型注解
4. 添加相应的模板和批量生成函数
5. 更新本文档

### 添加新的模板

1. 在相应工厂文件中的 `*_TEMPLATES` 字典中添加新模板
2. 确保模板数据的真实性和实用性
3. 在文档中更新可用模板列表

## 注意事项

1. **数据一致性**: 确保生成的数据符合业务规则
2. **性能考虑**: 避免在工厂中执行耗时操作
3. **随机性**: 使用随机数据避免测试间的依赖
4. **可读性**: 生成的数据应该便于调试和理解
5. **维护性**: 定期更新模板数据以反映业务变化 