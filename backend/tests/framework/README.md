# 信用卡管理系统测试框架 v2.0

新一代智能测试框架，为信用卡管理系统提供全面、高效、易用的测试解决方案。

## ✨ 主要特性

### 🎯 极简API设计
- **一行代码完成复杂测试**: 通过装饰器和流畅接口，减少90%的样板代码
- **声明式测试**: 使用装饰器声明测试需求，代码即文档
- **链式调用**: `api.get("/users").should.succeed().with_data(count__gt=0)`

### 🤖 智能自动化
- **自动数据管理**: 测试数据自动创建、关联和清理
- **智能依赖处理**: 自动解析和满足测试依赖关系
- **环境自感知**: 自动检测测试环境状态

### 🔗 流畅断言接口
- **人性化断言**: `expect(value).should.be_greater_than(100)`
- **响应断言**: `response.should.succeed().with_data(username="test")`
- **性能断言**: `response.should.complete_within(1.0)`

### 🚀 高性能执行
- **并行测试**: 支持多进程并行执行
- **智能调度**: 根据测试类型和依赖优化执行顺序
- **资源管理**: 自动管理测试资源和清理

## 🏗️ 架构设计

```
tests/framework/
├── core/                   # 核心组件
│   ├── suite.py           # 测试套件管理
│   ├── runner.py          # 智能测试运行器
│   └── assertion.py       # 流畅断言系统
├── clients/               # 客户端组件
│   └── api.py            # API客户端
├── decorators/           # 装饰器系统
│   ├── test.py          # 测试装饰器
│   └── data.py          # 数据装饰器
└── utils/               # 工具组件
    ├── http.py         # HTTP工具
    └── helpers.py      # 辅助函数
```

## 🚀 快速开始

### 1. 基础测试示例

```python
from tests.framework import *

@test_suite("用户管理测试")
class UserTests:
    @api_test("用户注册测试")
    @tag("smoke", "auth")
    def test_user_registration(self, api):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123"
        }
        
        response = api.post("/api/v1/public/auth/register", user_data)
        response.should.succeed().with_data(
            username="testuser",
            email="test@example.com"
        )
```

### 2. 数据装饰器使用

```python
@with_user(username="demo_user")
@with_cards(count=3, bank_name="招商银行")
@with_transactions(count=10)
@api_test("用户数据完整性测试")
def test_user_data_integrity(self, api, user, cards, transactions):
    # 数据已自动创建和关联
    
    # 验证用户有3张信用卡
    cards_response = api.get_cards_list()
    cards_response.should.succeed().with_pagination(total_items=3)
    
    # 验证交易记录
    trans_response = api.get_transactions_list()
    trans_response.should.succeed().with_pagination(total_items=10)
    
    # 数据将在测试结束后自动清理
```

### 3. 性能测试

```python
@performance_test("API响应性能", max_duration=2.0)
@tag("performance")
def test_api_performance(self, api):
    # 测试会自动记录执行时间
    response = api.get("/api/v1/user/cards/list")
    response.should.succeed().complete_within(1.0)

@stress_test("并发压力测试", iterations=100)
@tag("stress")
def test_concurrent_load(self, api):
    # 这个测试会并发执行100次
    response = api.health_check()
    response.should.succeed()
```

### 4. 参数化测试

```python
@parametrize("bank_name", ["招商银行", "工商银行", "建设银行"])
@api_test("多银行信用卡测试")
def test_multiple_banks(self, api, bank_name):
    card_data = {
        "card_name": f"{bank_name}信用卡",
        "bank_name": bank_name,
        "credit_limit": 50000
    }
    
    response = api.create_card(card_data)
    response.should.succeed().with_data(bank_name=bank_name)
```

## 🎨 装饰器说明

### 测试定义装饰器

| 装饰器 | 说明 | 示例 |
|--------|------|------|
| `@test_suite` | 定义测试套件 | `@test_suite("API测试套件")` |
| `@api_test` | 标记API测试 | `@api_test("用户登录测试")` |
| `@smoke_test` | 冒烟测试 | `@smoke_test("基础功能验证")` |
| `@performance_test` | 性能测试 | `@performance_test("响应时间测试", max_duration=1.0)` |
| `@stress_test` | 压力测试 | `@stress_test("并发测试", iterations=100)` |

### 数据准备装饰器

| 装饰器 | 说明 | 示例 |
|--------|------|------|
| `@with_user` | 自动创建用户 | `@with_user(username="testuser")` |
| `@with_cards` | 自动创建信用卡 | `@with_cards(count=3, bank_name="招商银行")` |
| `@with_transactions` | 自动创建交易 | `@with_transactions(count=10)` |
| `@with_test_data` | 创建完整数据集 | `@with_test_data(users=2, cards_per_user=3)` |

### 测试控制装饰器

| 装饰器 | 说明 | 示例 |
|--------|------|------|
| `@tag` | 添加标签 | `@tag("smoke", "critical")` |
| `@priority` | 设置优先级 | `@priority(TestPriority.HIGH)` |
| `@timeout` | 设置超时 | `@timeout(30)` |
| `@retry` | 失败重试 | `@retry(count=3, delay=1.0)` |
| `@parametrize` | 参数化测试 | `@parametrize("value", [1, 2, 3])` |

## 🔍 断言系统

### 基础断言

```python
# 基础值断言
expect(value).should.equal(expected)
expect(value).should.not_equal(unexpected)
expect(value).should.be_true()
expect(value).should.be_false()
expect(value).should.be_none()
expect(value).should.not_be_none()

# 字符串断言
expect(text).should.contain("substring")
expect(text).should.start_with("prefix")
expect(text).should.end_with("suffix")
expect(text).should.match_pattern(r"\d{4}-\d{2}-\d{2}")

# 数字断言
expect(number).should.be_greater_than(10)
expect(number).should.be_between(1, 100)
expect(number).should.be_positive()

# 集合断言
expect(collection).should.have_length(5)
expect(collection).should.contain_item("item")
expect(collection).should.not_be_empty()
```

### 响应断言

```python
# HTTP响应断言
response.should.succeed()  # 状态码200且success=true
response.should.fail(404)  # 状态码404
response.should.complete_within(1.0)  # 响应时间小于1秒

# 响应数据断言
response.should.with_data(
    username="testuser",
    email="test@example.com",
    age__gt=18,  # age > 18
    name__contains="test"  # name包含"test"
)

# 分页响应断言
response.should.with_pagination(
    total_items=100,
    page=1,
    page_size=20,
    items_type="users"
)

# 错误响应断言
response.should.with_error(
    error_code="VALIDATION_ERROR",
    error_message="Invalid email format"
)
```

## 🏃‍♂️ 运行测试

### 交互式模式

```bash
python run_tests_v2.py
```

启动交互式菜单，提供以下选项：
- 发现并查看测试套件
- 运行所有测试
- 运行冒烟测试
- 运行性能测试
- 运行压力测试
- 按标签或套件运行
- 服务器状态检查

### 命令行模式

```bash
# 运行所有测试
python run_tests_v2.py --all

# 运行冒烟测试
python run_tests_v2.py --smoke

# 按标签运行
python run_tests_v2.py --tags smoke api

# 按套件运行
python run_tests_v2.py --suites user_management card_management

# 并行执行
python run_tests_v2.py --all --parallel --workers 4

# 生成报告
python run_tests_v2.py --all --output html --output-file report.html

# 详细输出
python run_tests_v2.py --all --verbose

# 快速失败
python run_tests_v2.py --all --fail-fast
```

### 环境要求

```bash
# 检查服务器状态
python run_tests_v2.py --check-server

# 指定服务器地址
python run_tests_v2.py --base-url http://localhost:8080 --all
```

## 📊 报告格式

### 控制台输出
- 实时测试进度
- 彩色状态指示
- 性能指标显示
- 失败详情展示

### JSON报告
```json
{
  "summary": {
    "total": 150,
    "passed": 145,
    "failed": 3,
    "errors": 2,
    "success_rate": 96.7,
    "duration": 125.6
  },
  "suites": [...],
  "performance": {...}
}
```

### HTML报告
- 交互式Web界面
- 测试结果可视化
- 性能图表
- 错误详情展示

## 🔧 配置选项

### 测试运行配置

```python
config = TestRunConfig(
    # 过滤选项
    filter_tags=["smoke", "api"],
    filter_suites=["user_management"],
    filter_pattern="test_login*",
    
    # 执行选项
    parallel=True,
    max_workers=4,
    timeout=30,
    fail_fast=False,
    
    # 输出选项
    output_format="console",  # console, json, html
    output_file="report.html",
    verbose=True,
    
    # 环境选项
    base_url="http://127.0.0.1:8000"
)
```

### API客户端配置

```python
api = FluentAPIClient("http://127.0.0.1:8000")
api.set_header("X-Custom-Header", "value")
api.set_auth("Bearer token")

# 或使用构建器模式
api = (api_client_builder()
       .with_base_url("http://127.0.0.1:8000")
       .with_auth("Bearer token")
       .with_header("X-App-Version", "2.0")
       .build())
```

## 🧪 测试套件示例

### 完整的测试套件

```python
@test_suite("信用卡管理API测试", "测试信用卡相关的所有API功能")
class CardManagementTests:
    
    @before_suite
    def setup_suite(self):
        """套件启动前的初始化"""
        print("🚀 初始化信用卡测试套件...")
    
    @after_suite
    def teardown_suite(self):
        """套件结束后的清理"""
        print("🧹 清理信用卡测试套件...")
    
    @smoke_test("信用卡列表获取")
    @tag("smoke", "critical")
    @with_user()
    def test_get_cards_list(self, api, user):
        """测试获取信用卡列表"""
        response = api.get_cards_list()
        response.should.succeed().with_pagination(items_type="cards")
    
    @api_test("信用卡创建")
    @tag("crud", "cards")
    @with_user()
    @priority(TestPriority.HIGH)
    def test_create_card(self, api, user):
        """测试创建信用卡"""
        card_data = {
            "card_name": "测试信用卡",
            "bank_name": "测试银行",
            "credit_limit": 50000
        }
        
        response = api.create_card(card_data)
        response.should.succeed().with_data(
            card_name=card_data["card_name"],
            bank_name=card_data["bank_name"],
            credit_limit=card_data["credit_limit"]
        )
    
    @performance_test("信用卡列表性能", max_duration=1.0)
    @tag("performance")
    @with_user()
    @with_cards(count=50)  # 创建50张卡片测试性能
    def test_cards_list_performance(self, api, user, cards):
        """测试信用卡列表的性能"""
        response = api.get_cards_list(page_size=100)
        response.should.succeed().complete_within(1.0)
    
    @stress_test("信用卡创建压力测试", iterations=50)
    @tag("stress", "cards")
    @with_user()
    def test_card_creation_stress(self, api, user):
        """测试信用卡创建的并发性能"""
        card_data = {
            "card_name": f"压力测试卡片{random.randint(1000, 9999)}",
            "bank_name": "压力测试银行",
            "credit_limit": 10000
        }
        
        response = api.create_card(card_data)
        response.should.succeed()
    
    @parametrize("bank_name", ["招商银行", "工商银行", "建设银行", "农业银行"])
    @api_test("多银行支持测试")
    @tag("banks", "compatibility")
    @with_user()
    def test_multiple_banks(self, api, user, bank_name):
        """测试不同银行的信用卡创建"""
        card_data = {
            "card_name": f"{bank_name}信用卡",
            "bank_name": bank_name,
            "credit_limit": 30000
        }
        
        response = api.create_card(card_data)
        response.should.succeed().with_data(bank_name=bank_name)
    
    @retry(count=3, delay=1.0)
    @api_test("网络重试测试")
    @tag("reliability", "network")
    def test_network_reliability(self, api):
        """测试网络异常时的重试机制"""
        # 模拟可能的网络异常
        response = api.health_check()
        response.should.succeed()
    
    @expect_failure("已知的API限制")
    @api_test("预期失败测试")
    @tag("known_issues")
    def test_known_limitation(self, api):
        """测试已知的系统限制"""
        # 这个测试预期会失败
        response = api.get("/api/v1/cards/invalid-endpoint")
        response.should.succeed()  # 这会失败，但被标记为预期失败
```

## 🔍 调试和故障排除

### 常见问题

1. **服务器连接失败**
   ```bash
   python run_tests_v2.py --check-server
   python start.py dev  # 启动服务器
   ```

2. **测试数据冲突**
   - 测试框架会自动清理数据
   - 使用独特的测试数据标识符
   - 检查数据库状态

3. **性能测试失败**
   - 调整性能阈值
   - 检查系统负载
   - 使用 `--verbose` 查看详细信息

### 调试模式

```bash
# 详细输出模式
python run_tests_v2.py --all --verbose

# 调试单个测试
python run_tests_v2.py --tags debug --verbose

# 检查测试发现
python run_tests_v2.py --discover
```

## 🤝 扩展和自定义

### 自定义断言

```python
class CustomAssertion(BaseAssertion):
    def be_valid_credit_card(self):
        """自定义信用卡号验证断言"""
        card_number = str(self.value).replace(" ", "")
        # Luhn算法验证
        valid = self._luhn_check(card_number)
        self._assert(valid, "期望有效的信用卡号", expected="有效卡号", actual=self.value)
        return self
```

### 自定义装饰器

```python
def with_admin_user(func):
    """创建管理员用户装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 创建管理员用户逻辑
        admin_user = create_admin_user()
        kwargs['admin'] = admin_user
        return func(*args, **kwargs)
    return wrapper
```

### 自定义数据工厂

```python
class CustomCardFactory(CardFactory):
    @classmethod
    def create_platinum_card(cls, **kwargs):
        """创建白金卡"""
        kwargs.update({
            "card_name": "白金信用卡",
            "credit_limit": 100000,
            "annual_fee": 500
        })
        return cls.create(**kwargs)
```

## 📈 最佳实践

### 1. 测试组织
- 按功能模块组织测试套件
- 使用有意义的测试名称
- 添加清晰的标签分类
- 设置合理的优先级

### 2. 数据管理
- 优先使用数据装饰器
- 避免硬编码测试数据
- 确保测试数据隔离
- 及时清理测试数据

### 3. 断言编写
- 使用流畅的断言接口
- 提供清晰的错误消息
- 验证关键业务逻辑
- 避免过度断言

### 4. 性能测试
- 设置合理的性能阈值
- 监控资源使用情况
- 在稳定环境中执行
- 记录性能基线

### 5. 持续集成
- 集成到CI/CD流水线
- 设置测试覆盖率目标
- 定期执行完整测试套件
- 监控测试结果趋势

## 📝 更新日志

### v2.0.0 (当前版本)
- 🎯 全新的极简API设计
- 🤖 智能自动化数据管理
- 🔗 流畅的断言接口
- 🚀 高性能并行执行
- 📊 丰富的报告格式
- 🔧 灵活的配置选项

### 升级指南
从v1.x升级到v2.0的详细步骤请参考 `UPGRADE_GUIDE.md`

## 🆘 支持和反馈

- 📧 邮箱: support@creditcard-system.com
- 💬 问题反馈: 创建GitHub Issue
- 📖 文档: 访问项目Wiki
- 🎥 视频教程: 查看演示视频

---

**让测试变得简单而强大！** 🚀 