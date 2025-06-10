# 新一代测试框架 v2.0

**作者**: LEO (leoyfm@gmail.com)  
**版本**: 2.0.0  
**创建时间**: 2024年12月

## 🎯 设计目标

打造一个**更易用、更全面**的测试框架，解决传统测试框架的痛点：

- ❌ **复杂难用**: 需要编写大量样板代码
- ❌ **数据管理困难**: 手动创建和清理测试数据
- ❌ **断言不友好**: 冗长的断言代码
- ❌ **维护成本高**: 测试代码难以维护和扩展

## ✨ 核心特性

### 🚀 极简API设计
```python
@test_suite("用户管理")
class UserTests:
    
    @api_test
    @with_user
    @with_cards(count=3)
    def test_user_cards(self, api, user, cards):
        # 一行装饰器自动创建用户和3张信用卡
        api.get("/api/v1/user/cards/list").should.succeed()
```

### 🎭 声明式测试
```python
@api_test
@with_data({
    "user": {"username": "test_user"},
    "cards": {"count": 5, "bank": "招商银行"},
    "transactions": {"count": 100}
})
def test_complex_scenario(self, api, data):
    # 自动创建复杂的数据关系
    pass
```

### 🌊 流畅断言接口
```python
api.get("/api/v1/user/profile").should.succeed().with_data(
    username="testuser",
    email__contains="@example.com",
    cards__length=3,
    balance__gte=1000
).complete_within(seconds=0.5)
```

### 🔧 智能数据管理
- **自动创建**: 根据装饰器自动创建测试数据
- **关系处理**: 自动处理数据间的依赖关系
- **自动清理**: 测试完成后自动清理所有数据

### 📊 丰富的测试报告
- **实时反馈**: 测试执行过程中的实时状态
- **详细统计**: 成功率、性能指标、错误分析
- **可视化报告**: JSON格式的详细测试报告

## 🏗️ 架构设计

```
tests/framework/
├── __init__.py              # 框架入口
├── clients/
│   └── api.py              # 流畅API客户端
├── core/
│   ├── runner.py           # 智能测试运行器
│   ├── suite.py            # 测试套件核心
│   └── scenario.py         # 测试场景
├── decorators/
│   ├── test.py             # 测试装饰器
│   ├── data.py             # 数据装饰器
│   └── performance.py      # 性能装饰器
├── data/
│   └── factory.py          # 数据工厂
├── utils/
│   ├── env.py              # 环境管理
│   └── timing.py           # 性能测量
└── README.md               # 文档
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install requests
```

### 2. 创建第一个测试
```python
# tests/suites/my_first_test.py
from tests.framework import test_suite, api_test, with_user

@test_suite("我的第一个测试")
class MyFirstTest:
    
    @api_test
    @with_user
    def test_user_profile(self, api, user):
        """测试获取用户资料"""
        api.get("/api/v1/user/profile").should.succeed().with_data(
            username=user.username,
            email=user.email
        )
```

### 3. 运行测试
```bash
# 交互模式
python tests/run_tests.py

# 命令行模式
python tests/run_tests.py --tags smoke
python tests/run_tests.py --suite "我的第一个测试"
python tests/run_tests.py --parallel
```

## 📚 装饰器详解

### @test_suite - 测试套件
```python
@test_suite("套件名称", description="套件描述")
class MyTestSuite:
    pass
```

### @api_test - API测试
```python
@api_test(timeout=30)  # 可选参数
def test_api(self, api):
    # api 客户端自动注入
    pass
```

### @with_user - 自动创建用户
```python
@with_user(username="custom_user")  # 可选自定义
def test_with_user(self, api, user):
    # user 对象自动创建并登录
    assert user.username == "custom_user"
```

### @with_cards - 自动创建信用卡
```python
@with_cards(count=3, bank="招商银行", credit_limit=50000)
def test_with_cards(self, api, user, cards):
    # cards 是信用卡列表
    assert len(cards) == 3
    for card in cards:
        assert card.bank_name == "招商银行"
```

### @with_transactions - 自动创建交易
```python
@with_transactions(count=50, amount_range=(10, 1000))
def test_with_transactions(self, api, user, cards, transactions):
    # transactions 是交易记录列表
    assert len(transactions) == 50
```

### @performance_test - 性能测试
```python
@performance_test
@benchmark(max_time=1.0)
def test_performance(self, api):
    # 自动记录性能指标
    api.get("/api/v1/heavy-operation").should.complete_within(1.0)
```

### @tags - 标签系统
```python
@tags("smoke", "critical", "auth")
def test_login(self, api):
    # 支持按标签筛选运行
    pass
```

### @priority - 优先级
```python
@priority(1)  # 数字越小优先级越高
def test_critical_feature(self, api):
    pass
```

## 🌊 流畅断言API

### 基础断言
```python
response = api.get("/api/v1/user/profile")

# 成功断言
response.should.succeed()  # 200状态码
response.should.succeed(201)  # 指定状态码

# 失败断言
response.should.fail()  # >=400状态码
response.should.fail(404)  # 指定错误状态码
response.should.fail().with_error("USER_NOT_FOUND")
```

### 数据断言
```python
response.should.succeed().with_data(
    # 精确匹配
    username="testuser",
    email="test@example.com",
    
    # 操作符断言
    age__gte=18,              # 大于等于
    balance__gt=1000,         # 大于
    name__contains="张",       # 包含
    email__endswith=".com",   # 结尾
    tags__in=["vip", "gold"], # 在列表中
    items__length=5,          # 长度
    
    # 嵌套字段
    profile__name="张三",
    profile__address__city="北京"
)
```

### 分页断言
```python
response.should.succeed().with_pagination(
    total_items=100,
    page=1,
    page_size=20
)
```

### 性能断言
```python
response.should.succeed().complete_within(seconds=0.5)
```

### 响应头断言
```python
response.should.succeed().have_header("Content-Type", "application/json")
```

## 🎯 复杂场景示例

### 场景1: 用户完整工作流
```python
@test_scenario("用户完整使用流程")
class UserJourneyScenario:
    
    @api_test
    def test_complete_user_journey(self, api):
        # 1. 注册用户
        user_data = {
            "username": "journey_user",
            "email": "journey@example.com",
            "password": "SecurePass123"
        }
        
        register_response = api.post("/api/v1/public/auth/register", data=user_data)
        register_response.should.succeed()
        
        # 2. 登录
        login_response = api.post("/api/v1/public/auth/login/username", data={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        login_response.should.succeed()
        api.set_auth(login_response.data["access_token"])
        
        # 3. 添加信用卡
        card_data = {
            "card_name": "我的信用卡",
            "bank_name": "招商银行",
            "credit_limit": 50000
        }
        card_response = api.post("/api/v1/user/cards/create", data=card_data)
        card_response.should.succeed()
        
        # 4. 验证统计信息
        api.get("/api/v1/user/statistics/overview").should.succeed().with_data(
            total_cards=1,
            total_spending=0
        )
```

### 场景2: 性能压力测试
```python
@test_suite("性能压力测试")
class PerformanceStressTests:
    
    @performance_test
    @benchmark(max_time=2.0)
    @with_user
    @with_cards(count=100)
    @with_transactions(count=10000)
    def test_large_data_performance(self, api, user, cards, transactions):
        """大数据量性能测试"""
        # 测试大量数据下的查询性能
        api.get("/api/v1/user/cards/list", params={
            "page": 1,
            "page_size": 100
        }).should.succeed().complete_within(2.0)
        
        # 测试统计接口性能
        api.get("/api/v1/user/statistics/overview").should.succeed().complete_within(1.0)
```

### 场景3: 错误处理测试
```python
@test_suite("错误处理测试")
class ErrorHandlingTests:
    
    @api_test
    @with_user
    def test_invalid_requests(self, api, user):
        """测试各种无效请求"""
        
        # 无效数据格式
        api.post("/api/v1/user/cards/create", data={
            "card_name": "",  # 空名称
            "credit_limit": -1000  # 负数额度
        }).should.fail(400).with_error("VALIDATION_ERROR")
        
        # 权限不足
        api.delete("/api/v1/admin/users/123").should.fail(403)
        
        # 资源不存在
        api.get("/api/v1/user/cards/999999").should.fail(404)
```

## 🔧 高级功能

### 自定义数据工厂
```python
from tests.framework.data.factory import DataFactory

class CustomDataFactory(DataFactory):
    
    def create_vip_user(self):
        """创建VIP用户"""
        return self.create_user({
            "username": f"vip_{self.unique_id()}",
            "user_type": "vip",
            "credit_score": 850
        })
    
    def create_premium_card(self, user_id):
        """创建高端信用卡"""
        return self.create_card({
            "user_id": user_id,
            "card_type": "platinum",
            "credit_limit": 200000,
            "annual_fee": 3600
        })

# 使用自定义工厂
@with_data_factory(CustomDataFactory)
def test_vip_features(self, api, factory):
    user = factory.create_vip_user()
    card = factory.create_premium_card(user.id)
    # 测试VIP功能
```

### 环境配置
```python
# tests/framework/config.py
TEST_CONFIG = {
    "base_url": "http://127.0.0.1:8000",
    "timeout": 30,
    "retry_times": 3,
    "parallel_workers": 4,
    "data_cleanup": True
}

# 在测试中使用
from tests.framework.utils.env import TestEnvironment

env = TestEnvironment()
if env.is_development():
    # 开发环境特殊处理
    pass
```

### 测试报告定制
```python
# 生成HTML报告
runner = SmartTestRunner({
    "report_format": "html",
    "report_path": "tests/reports/",
    "include_screenshots": True
})
```

## 📊 测试运行器

### 命令行选项
```bash
# 基础用法
python tests/run_tests.py

# 过滤运行
python tests/run_tests.py --tags smoke auth
python tests/run_tests.py --suite "用户管理API"
python tests/run_tests.py --parallel --fail-fast

# 性能测试
python tests/run_tests.py --tags performance

# 列出所有测试
python tests/run_tests.py --list

# 显示框架演示
python tests/run_tests.py --demo
```

### 编程接口
```python
from tests.framework.core.runner import SmartTestRunner

runner = SmartTestRunner({
    "parallel_execution": True,
    "max_workers": 8,
    "fail_fast": False,
    "verbose": True
})

# 发现测试
runner.discover_tests("tests/suites/")

# 运行所有测试
results = runner.run_all()

# 按条件运行
results = runner.run_by_tags(["smoke", "critical"])
results = runner.run_suite("用户管理API")
results = runner.run_with_filters(
    tags=["auth"],
    max_priority=2,
    suites=["用户管理API", "信用卡管理"]
)
```

## 🎨 最佳实践

### 1. 测试组织
```python
# ✅ 好的做法
@test_suite("用户认证功能", description="测试用户注册、登录、权限等功能")
class UserAuthTests:
    
    @api_test
    @tags("smoke", "auth")
    @priority(1)
    def test_user_registration(self, api):
        """测试用户注册功能"""
        pass

# ❌ 避免的做法
class Tests:  # 名称不明确
    def some_test(self, api):  # 没有装饰器，不会被发现
        pass
```

### 2. 数据管理
```python
# ✅ 好的做法 - 使用装饰器自动管理
@with_user
@with_cards(count=3, bank="招商银行")
def test_cards(self, api, user, cards):
    # 数据自动创建和清理
    pass

# ❌ 避免的做法 - 手动管理数据
def test_cards_manual(self, api):
    # 手动创建用户
    user = create_test_user()
    try:
        # 手动创建卡片
        cards = create_test_cards(user.id)
        # 测试逻辑
        pass
    finally:
        # 手动清理
        cleanup_test_data(user.id)
```

### 3. 断言风格
```python
# ✅ 好的做法 - 流畅断言
api.get("/api/v1/user/profile").should.succeed().with_data(
    username="testuser",
    email__contains="@example.com"
)

# ❌ 避免的做法 - 传统断言
response = api.get("/api/v1/user/profile")
assert response.status_code == 200
data = response.json()
assert data["username"] == "testuser"
assert "@example.com" in data["email"]
```

### 4. 测试标签
```python
# 合理使用标签进行测试分类
@tags("smoke")         # 冒烟测试
@tags("integration")   # 集成测试
@tags("performance")   # 性能测试
@tags("critical")      # 关键功能
@tags("slow")          # 慢速测试
@tags("auth", "security")  # 组合标签
```

## 🔍 调试和诊断

### 调试单个测试
```python
@api_test
def test_debug_example(self, api):
    response = api.get("/api/v1/user/profile")
    
    # 调试输出
    response.debug()  # 打印详细响应信息
    
    response.should.succeed()
```

### 日志配置
```python
import logging

# 设置详细日志
logging.getLogger("tests.framework").setLevel(logging.DEBUG)

# 运行器配置
runner = SmartTestRunner({"verbose": True})
```

### 常见问题诊断

#### 问题1: 测试无法发现
```python
# 确保类使用了 @test_suite 装饰器
@test_suite("测试套件名称")
class MyTests:
    
    # 确保方法使用了 @api_test 装饰器
    @api_test
    def test_something(self, api):
        pass
```

#### 问题2: 认证失败
```python
# 确保使用了用户装饰器
@with_user
def test_protected_api(self, api, user):
    # api 已自动设置认证
    pass
```

#### 问题3: 数据创建失败
```python
# 检查API服务器是否运行
# 确保装饰器顺序正确
@api_test
@with_user      # 必须在 @with_cards 之前
@with_cards
def test_user_cards(self, api, user, cards):
    pass
```

## 🚀 迁移指南

### 从旧框架迁移

#### 旧代码
```python
class TestUsers(BaseAPITest):
    def test_user_profile(self):
        # 手动创建用户
        user_data = self.create_test_user()
        token = self.login_user(user_data)
        
        # 手动设置认证
        headers = {"Authorization": f"Bearer {token}"}
        
        # 发送请求
        response = self.client.get("/api/v1/user/profile", headers=headers)
        
        # 传统断言
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], user_data["username"])
        
        # 手动清理
        self.cleanup_user(user_data["id"])
```

#### 新代码
```python
@test_suite("用户管理")
class UserTests:
    
    @api_test
    @with_user
    def test_user_profile(self, api, user):
        api.get("/api/v1/user/profile").should.succeed().with_data(
            username=user.username
        )
```

## 📈 性能优化

### 并行执行
```python
# 启用并行执行
runner = SmartTestRunner({
    "parallel_execution": True,
    "max_workers": 8
})
```

### 数据重用
```python
# 在类级别重用数据
@test_suite("信用卡测试")
class CardTests:
    
    @classmethod
    def setup_class(cls):
        # 创建共享数据
        cls.shared_user = create_test_user()
    
    @api_test
    def test_card_list(self, api):
        # 重用共享数据
        api.set_auth(self.shared_user.token)
        api.get("/api/v1/user/cards/list").should.succeed()
```

### 跳过慢速测试
```python
import os

@tags("slow")
@skip_if(os.getenv("FAST_TESTS"), "跳过慢速测试")
def test_heavy_operation(self, api):
    # 重型操作测试
    pass
```

## 🎯 总结

新一代测试框架v2.0通过以下创新特性，显著提升了测试开发效率：

### ✨ 核心优势
1. **90%代码减少**: 装饰器自动处理样板代码
2. **零配置数据管理**: 自动创建、关联、清理测试数据
3. **流畅断言体验**: 链式调用，代码如文档般清晰
4. **智能测试运行**: 支持标签过滤、优先级、并行执行
5. **丰富测试报告**: 实时反馈和详细统计分析

### 🎪 使用场景
- **快速开发**: 新功能的快速测试验证
- **回归测试**: 自动化的回归测试套件
- **性能监控**: 持续的性能基准测试
- **集成测试**: 端到端的业务流程验证

### 🔮 未来规划
- **可视化报告**: HTML/图表形式的测试报告
- **Mock集成**: 自动化的外部服务Mock
- **数据驱动**: 支持Excel/CSV数据驱动测试
- **CI/CD集成**: 与持续集成系统的深度集成

---

**开始使用新测试框架，让测试变得简单而强大！** 🚀

如有任何问题，请联系 LEO (leoyfm@gmail.com) 