# 新一代测试框架设计文档

**版本**: v2.0  
**作者**: LEO  
**邮箱**: leoyfm@gmail.com  
**创建时间**: 2024年12月

## 🎯 设计目标

### 当前框架问题
1. **复杂性高**: 需要了解多个基类和混入类
2. **配置繁琐**: 测试数据准备代码重复
3. **可读性差**: 测试代码冗长，意图不明确
4. **维护困难**: 修改一个测试可能影响其他测试
5. **缺乏智能**: 没有自动数据清理和依赖管理

### 新框架特性
- ✨ **极简API**: 一行代码完成复杂测试
- 🚀 **自动化**: 自动数据准备、清理和依赖管理
- 🎭 **声明式**: 通过装饰器和配置声明测试需求
- 🔧 **智能感知**: 自动检测测试环境和依赖
- 📊 **可视化**: 丰富的测试报告和错误诊断
- 🌊 **流畅接口**: 链式调用，代码如文档般清晰

## 🏗️ 核心架构

### 1. 测试层次架构

```
TestSuite (测试套件)
├── TestScenario (测试场景)
│   ├── TestStep (测试步骤)
│   └── Assertions (断言集合)
├── TestData (测试数据)
│   ├── Factories (数据工厂)
│   ├── Fixtures (固定数据)
│   └── MockServices (模拟服务)
└── TestRuntime (运行时)
    ├── Environment (环境管理)
    ├── Dependencies (依赖管理)
    └── Reports (报告生成)
```

### 2. 目录结构

```
tests/
├── framework/                    # 新测试框架核心
│   ├── __init__.py
│   ├── core/                    # 核心组件
│   │   ├── suite.py            # 测试套件
│   │   ├── scenario.py         # 测试场景
│   │   ├── step.py             # 测试步骤
│   │   ├── assertion.py        # 断言系统
│   │   └── runner.py           # 运行器
│   ├── data/                   # 数据管理
│   │   ├── factory.py          # 数据工厂
│   │   ├── generator.py        # 数据生成器
│   │   ├── cleaner.py          # 数据清理器
│   │   └── mock.py             # 模拟服务
│   ├── clients/                # 客户端封装
│   │   ├── api.py              # API客户端
│   │   ├── database.py         # 数据库客户端
│   │   └── external.py         # 外部服务客户端
│   ├── decorators/             # 装饰器集合
│   │   ├── test.py             # 测试装饰器
│   │   ├── data.py             # 数据装饰器
│   │   └── performance.py      # 性能装饰器
│   ├── reporters/              # 报告生成器
│   │   ├── console.py          # 控制台报告
│   │   ├── html.py             # HTML报告
│   │   ├── json.py             # JSON报告
│   │   └── coverage.py         # 覆盖率报告
│   └── utils/                  # 工具类
│       ├── env.py              # 环境工具
│       ├── http.py             # HTTP工具
│       └── timing.py           # 时间工具
├── suites/                     # 测试套件（新）
│   ├── api/                    # API测试套件
│   │   ├── user_management.py
│   │   ├── card_management.py
│   │   ├── transaction_management.py
│   │   ├── annual_fee_management.py
│   │   └── statistics_analysis.py
│   ├── integration/            # 集成测试套件
│   │   ├── user_journey.py
│   │   ├── data_consistency.py
│   │   └── workflow_validation.py
│   ├── performance/            # 性能测试套件
│   │   ├── api_benchmarks.py
│   │   ├── stress_tests.py
│   │   └── load_tests.py
│   └── e2e/                   # 端到端测试套件
│       ├── user_scenarios.py
│       └── admin_scenarios.py
├── data/                      # 测试数据（新）
│   ├── fixtures/              # 固定测试数据
│   │   ├── users.json
│   │   ├── cards.json
│   │   └── transactions.json
│   ├── factories/             # 数据工厂配置
│   │   ├── user_factory.py
│   │   ├── card_factory.py
│   │   └── transaction_factory.py
│   └── mocks/                 # 模拟数据
│       ├── external_apis.py
│       └── services.py
├── legacy/                    # 原有测试（向后兼容）
│   ├── unit/
│   ├── integration/
│   └── performance/
└── config/                    # 测试配置
    ├── environments.yaml     # 环境配置
    ├── test_config.yaml      # 测试配置
    └── data_config.yaml      # 数据配置
```

## 🚀 新框架API设计

### 1. 极简测试编写

#### 传统方式 vs 新方式

**传统方式（复杂）**:
```python
class TestUserManagement(BaseAPITest):
    def setup_method(self):
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.user_data = self.api_test.setup_test_user()
        self.headers = self.user_data["headers"]
    
    def test_get_user_profile(self):
        response = self.client.get("/api/user/profile", headers=self.headers)
        self.api_test.assert_api_success(response)
        data = response.json()["data"]
        assert data["username"] == self.user_data["user"]["username"]
        # 还需要清理数据...
```

**新方式（极简）**:
```python
@test_suite("用户管理")
class UserManagementTests:
    
    @api_test
    @with_user
    def test_get_user_profile(self, api, user):
        """测试获取用户资料"""
        api.get("/api/v1/user/profile").should.succeed().with_data(
            username=user.username,
            email=user.email
        )
    
    @api_test  
    @with_user_and_cards(count=3)
    def test_get_user_cards(self, api, user, cards):
        """测试获取用户信用卡列表"""
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=3,
            items_type="card"
        )
```

### 2. 流畅的断言API

```python
# HTTP响应断言
api.get("/api/v1/user/profile").should.succeed()
api.post("/api/v1/cards", data=invalid_data).should.fail().with_error("VALIDATION_ERROR")

# 数据断言
response.should.have_data(
    username="testuser",
    email__contains="@example.com",
    cards_count__gte=1
)

# 性能断言
api.get("/api/v1/statistics/overview").should.complete_within(seconds=2)

# 数据库断言
db.table("users").should.have_count(1)
db.table("cards").where(user_id=user.id).should.exist()
```

### 3. 智能数据管理

```python
# 自动数据工厂
@with_user                           # 自动创建用户
@with_cards(count=5, bank="招商银行")   # 自动创建5张招商银行信用卡
@with_transactions(count=100)        # 自动创建100条交易记录
def test_user_statistics(self, api, user, cards, transactions):
    """数据会自动创建和清理"""
    pass

# 数据关系管理
@with_data({
    "user": UserFactory(username="testuser"),
    "cards": CardFactory.create_batch(3, user=DataRef("user")),
    "transactions": TransactionFactory.create_batch(50, card=DataRef("cards[0]"))
})
def test_complex_scenario(self, api, data):
    """复杂数据关系自动建立"""
    pass
```

### 4. 场景化测试

```python
@test_scenario("用户完整工作流")
class UserCompleteWorkflow:
    
    def scenario_register_and_setup(self):
        """场景：用户注册并设置信用卡"""
        return TestScenario("用户注册并设置").with_steps([
            Step("注册用户").call(self.register_user),
            Step("登录系统").call(self.login_user),
            Step("添加信用卡").call(self.add_credit_card),
            Step("设置年费规则").call(self.setup_annual_fee),
            Step("验证设置").call(self.verify_setup)
        ])
    
    def register_user(self, context):
        response = context.api.post("/api/v1/public/auth/register", data={
            "username": context.data.username,
            "email": context.data.email,
            "password": context.data.password
        })
        response.should.succeed()
        context.user = response.data
    
    def login_user(self, context):
        response = context.api.post("/api/v1/public/auth/login/username", data={
            "username": context.data.username,
            "password": context.data.password  
        })
        response.should.succeed()
        context.api.set_auth(response.data.access_token)
```

### 5. 性能测试简化

```python
@performance_test
class APIPerformanceTests:
    
    @benchmark(max_time=1.0)
    @with_user_and_cards(count=10)
    def test_cards_list_performance(self, api, user, cards):
        """测试卡片列表接口性能"""
        api.get("/api/v1/user/cards/list").should.complete_within(seconds=1)
    
    @stress_test(concurrent_users=50, duration=60)
    def test_login_under_load(self):
        """测试登录接口压力测试"""
        api.post("/api/v1/public/auth/login/username", data=random_user_data())
    
    @load_test(ramp_up="10users/sec", peak="100users", duration="5min")
    def test_api_load_handling(self):
        """测试API负载处理能力"""
        # 自动执行多种API调用
        pass
```

## 🔧 核心组件实现

### 1. 测试套件基类

```python
class TestSuite:
    """测试套件基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.tests = []
        self.setup_hooks = []
        self.teardown_hooks = []
        self.data_factories = {}
        self.environment = TestEnvironment()
    
    def add_test(self, test_func):
        """添加测试方法"""
        self.tests.append(TestCase(test_func, self))
    
    def before_each(self, hook_func):
        """添加每个测试前的钩子"""
        self.setup_hooks.append(hook_func)
    
    def after_each(self, hook_func):
        """添加每个测试后的钩子"""
        self.teardown_hooks.append(hook_func)
    
    def with_data(self, **factories):
        """配置数据工厂"""
        self.data_factories.update(factories)
        return self
```

### 2. API客户端

```python
class FluentAPIClient:
    """流畅的API客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.auth_token = None
        self.last_response = None
    
    def get(self, path: str, **kwargs):
        """GET请求"""
        self.last_response = self.session.get(f"{self.base_url}{path}", **kwargs)
        return ResponseAssertion(self.last_response)
    
    def post(self, path: str, data=None, **kwargs):
        """POST请求"""
        self.last_response = self.session.post(
            f"{self.base_url}{path}", 
            json=data,
            **kwargs
        )
        return ResponseAssertion(self.last_response)
    
    def set_auth(self, token: str):
        """设置认证令牌"""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})


class ResponseAssertion:
    """响应断言"""
    
    def __init__(self, response):
        self.response = response
        self.data = response.json() if response.content else None
    
    @property
    def should(self):
        """流畅断言接口"""
        return self
    
    def succeed(self, status_code: int = 200):
        """断言请求成功"""
        assert self.response.status_code == status_code, \
            f"期望状态码 {status_code}，实际 {self.response.status_code}: {self.response.text}"
        if self.data:
            assert self.data.get("success", True), f"响应失败: {self.data}"
        return self
    
    def fail(self, status_code: int = None):
        """断言请求失败"""
        if status_code:
            assert self.response.status_code == status_code
        else:
            assert self.response.status_code >= 400
        return self
    
    def with_data(self, **expected):
        """断言响应数据"""
        data = self.data.get("data", {}) if self.data else {}
        for key, value in expected.items():
            if "__" in key:
                # 支持复杂断言如 email__contains
                field, operator = key.split("__", 1)
                actual = data.get(field)
                self._assert_with_operator(actual, operator, value)
            else:
                assert data.get(key) == value, \
                    f"字段 {key} 期望值 {value}，实际值 {data.get(key)}"
        return self
    
    def with_pagination(self, total_items: int = None, items_type: str = None):
        """断言分页响应"""
        assert "pagination" in self.data, "响应中缺少分页信息"
        pagination = self.data["pagination"]
        
        if total_items is not None:
            assert pagination["total"] == total_items
        
        if items_type:
            items = self.data.get("data", [])
            assert len(items) > 0, f"没有找到 {items_type} 数据"
        
        return self
    
    def complete_within(self, seconds: float):
        """断言响应时间"""
        # 这里需要在请求时记录时间
        # 实际实现会更复杂
        return self
```

### 3. 数据工厂系统

```python
class DataFactory:
    """数据工厂基类"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.defaults = {}
        self.traits = {}
    
    def create(self, **kwargs):
        """创建单个对象"""
        data = {**self.defaults, **kwargs}
        return self._create_instance(data)
    
    def create_batch(self, count: int, **kwargs):
        """批量创建对象"""
        return [self.create(**kwargs) for _ in range(count)]
    
    def with_trait(self, trait_name: str):
        """应用特征"""
        if trait_name in self.traits:
            return self.__class__({**self.defaults, **self.traits[trait_name]})
        return self


class UserFactory(DataFactory):
    """用户数据工厂"""
    
    defaults = {
        "username": lambda: f"user_{uuid4().hex[:8]}",
        "email": lambda: f"test_{uuid4().hex[:8]}@example.com",
        "password": "TestPass123456",
        "nickname": "测试用户"
    }
    
    traits = {
        "admin": {"is_admin": True},
        "verified": {"is_verified": True},
        "inactive": {"is_active": False}
    }


class CardFactory(DataFactory):
    """信用卡数据工厂"""
    
    defaults = {
        "card_name": "测试信用卡",
        "bank_name": "测试银行", 
        "card_number": lambda: f"6225{random.randint(100000000000, 999999999999)}",
        "credit_limit": 50000.00,
        "expiry_month": 12,
        "expiry_year": 2027
    }
    
    traits = {
        "high_limit": {"credit_limit": 200000.00},
        "cmb": {"bank_name": "招商银行"},
        "icbc": {"bank_name": "工商银行"}
    }
```

### 4. 装饰器系统

```python
def test_suite(name: str):
    """测试套件装饰器"""
    def decorator(cls):
        cls._test_suite_name = name
        cls._suite = TestSuite(name)
        return cls
    return decorator


def api_test(func):
    """API测试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 自动注入api客户端
        if "api" not in kwargs:
            kwargs["api"] = FluentAPIClient()
        return func(*args, **kwargs)
    wrapper._is_api_test = True
    return wrapper


def with_user(username: str = None, **user_kwargs):
    """自动创建用户装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建测试用户
            user_factory = UserFactory()
            if username:
                user_kwargs["username"] = username
            user = user_factory.create(**user_kwargs)
            
            # 注册并登录用户
            api = kwargs.get("api") or FluentAPIClient()
            api.post("/api/v1/public/auth/register", data=user.__dict__)
            login_response = api.post("/api/v1/public/auth/login/username", data={
                "username": user.username,
                "password": user.password
            })
            api.set_auth(login_response.data["access_token"])
            
            kwargs["user"] = user
            kwargs["api"] = api
            
            try:
                return func(*args, **kwargs)
            finally:
                # 自动清理用户数据
                DataCleaner.cleanup_user(user.id)
        
        return wrapper
    return decorator


def with_cards(count: int = 1, **card_kwargs):
    """自动创建信用卡装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api = kwargs["api"]
            user = kwargs["user"]
            
            # 创建信用卡
            card_factory = CardFactory()
            cards = []
            for _ in range(count):
                card_data = card_factory.create(**card_kwargs)
                response = api.post("/api/v1/user/cards/create", data=card_data.__dict__)
                cards.append(response.data)
            
            kwargs["cards"] = cards if count > 1 else cards[0]
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def performance_test(func):
    """性能测试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            # 记录性能指标
            PerformanceRecorder.record(func.__name__, duration)
            return result
        except Exception as e:
            # 记录失败的性能测试
            PerformanceRecorder.record_failure(func.__name__, str(e))
            raise
    
    wrapper._is_performance_test = True
    return wrapper
```

### 5. 智能测试运行器

```python
class SmartTestRunner:
    """智能测试运行器"""
    
    def __init__(self):
        self.environment = TestEnvironment()
        self.data_manager = TestDataManager()
        self.reporter = TestReporter()
        self.discovered_tests = []
    
    def discover_tests(self, path: str = "tests/suites/"):
        """自动发现测试"""
        test_files = Path(path).rglob("*.py")
        for file in test_files:
            module = self._import_module(file)
            for cls in self._find_test_classes(module):
                self.discovered_tests.extend(self._extract_tests(cls))
    
    def run_all(self, filter_pattern: str = None):
        """运行所有测试"""
        tests_to_run = self.discovered_tests
        if filter_pattern:
            tests_to_run = [t for t in tests_to_run if re.match(filter_pattern, t.name)]
        
        results = []
        for test in tests_to_run:
            result = self._run_single_test(test)
            results.append(result)
            self.reporter.report_test_result(result)
        
        self.reporter.generate_final_report(results)
        return results
    
    def _run_single_test(self, test: TestCase):
        """运行单个测试"""
        try:
            # 前置数据准备
            test_context = self.data_manager.prepare_test_data(test)
            
            # 执行测试
            start_time = time.time()
            test.execute(test_context)
            end_time = time.time()
            
            # 后置数据清理
            self.data_manager.cleanup_test_data(test_context)
            
            return TestResult(
                test=test,
                status="PASSED",
                duration=end_time - start_time,
                context=test_context
            )
        
        except Exception as e:
            return TestResult(
                test=test,
                status="FAILED", 
                error=str(e),
                context=test_context
            )
```

## 📊 使用示例

### 1. 简单API测试

```python
@test_suite("用户认证API")
class AuthAPITests:
    
    @api_test
    def test_user_registration(self, api):
        """测试用户注册"""
        user_data = UserFactory.build()
        api.post("/api/v1/public/auth/register", data=user_data).should.succeed()
    
    @api_test
    @with_user
    def test_user_login(self, api, user):
        """测试用户登录"""
        api.post("/api/v1/public/auth/login/username", data={
            "username": user.username,
            "password": user.password
        }).should.succeed().with_data(
            access_token__exists=True,
            user__username=user.username
        )
```

### 2. 复杂业务流程测试

```python
@test_suite("信用卡管理流程")
class CardManagementWorkflow:
    
    @api_test
    @with_user
    @with_cards(count=3, bank="招商银行")
    def test_complete_card_lifecycle(self, api, user, cards):
        """测试信用卡完整生命周期"""
        
        # 获取卡片列表
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=3
        )
        
        # 更新卡片信息
        card = cards[0]
        api.put(f"/api/v1/user/cards/{card.id}/update", data={
            "card_name": "新的卡片名称"
        }).should.succeed()
        
        # 设置年费规则
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card.id,
            "condition_type": "spending_amount",
            "condition_value": 50000
        }).should.succeed()
        
        # 验证规则生效
        api.get(f"/api/v1/user/cards/{card.id}/details").should.succeed().with_data(
            card_name="新的卡片名称",
            fee_waivable=True
        )
```

### 3. 性能基准测试

```python
@test_suite("API性能基准")
class APIPerformanceBenchmarks:
    
    @performance_test
    @benchmark(max_response_time=0.5)
    @with_user
    def test_user_profile_performance(self, api, user):
        """用户资料接口性能基准"""
        api.get("/api/v1/user/profile").should.succeed().complete_within(seconds=0.5)
    
    @stress_test(concurrent_users=20, duration=30)
    @with_user_pool(size=50)  # 创建50个用户供并发测试使用
    def test_cards_list_under_load(self, api, user_pool):
        """卡片列表接口压力测试"""
        user = random.choice(user_pool)
        api.set_auth(user.token)
        api.get("/api/v1/user/cards/list").should.succeed()
```

### 4. 数据一致性测试

```python
@test_suite("数据一致性验证")
class DataConsistencyTests:
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=50)
    def test_statistics_data_consistency(self, api, user, cards, transactions):
        """测试统计数据一致性"""
        
        # 获取统计数据
        stats_response = api.get("/api/v1/user/statistics/overview").should.succeed()
        stats = stats_response.data
        
        # 验证数据库一致性
        db.table("transactions").where(user_id=user.id).should.have_count(50)
        db.table("credit_cards").where(user_id=user.id).should.have_count(2)
        
        # 验证统计计算正确性
        expected_total = sum(t.amount for t in transactions if t.transaction_type == "expense")
        assert stats["total_spending"] == expected_total
```

## 🎯 迁移指南

### 1. 从旧框架迁移

**第一步：安装新框架**
```bash
# 安装新的测试依赖
pip install -r tests/requirements-new.txt

# 初始化新框架配置
python -m tests.framework.init
```

**第二步：转换现有测试**
```python
# 旧的测试代码
class TestUserCards(BaseAPITest):
    def setup_method(self):
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client) 
        self.user_data = self.api_test.setup_test_user()
    
    def test_get_cards_list(self):
        response = self.client.get("/api/user/cards/list", headers=self.user_data["headers"])
        self.api_test.assert_api_success(response)

# 新的测试代码
@test_suite("用户信用卡")
class UserCardTests:
    
    @api_test
    @with_user
    def test_get_cards_list(self, api, user):
        api.get("/api/v1/user/cards/list").should.succeed()
```

**第三步：配置测试环境**
```yaml
# tests/config/environments.yaml
test:
  database_url: "postgresql://test:test@localhost/test_db"
  api_base_url: "http://127.0.0.1:8000"
  cleanup_data: true
  
development:
  database_url: "postgresql://dev:dev@localhost/dev_db"
  api_base_url: "http://127.0.0.1:8000"
  cleanup_data: false
```

### 2. 运行新测试框架

```bash
# 运行所有测试
python -m tests.framework.runner

# 运行特定套件
python -m tests.framework.runner --suite "用户管理"

# 运行性能测试
python -m tests.framework.runner --type performance

# 生成详细报告
python -m tests.framework.runner --report html
```

## 📈 优势对比

| 特性 | 旧框架 | 新框架 |
|------|--------|--------|
| **测试编写** | 20-30行代码 | 5-10行代码 |
| **数据准备** | 手动编写 | 自动生成 |
| **数据清理** | 手动管理 | 自动清理 |
| **可读性** | 复杂难懂 | 语义清晰 |
| **维护性** | 修改困难 | 易于维护 |
| **报告** | 基础报告 | 丰富可视化 |
| **学习成本** | 高 | 低 |
| **扩展性** | 有限 | 高度可扩展 |

## 🚀 实施计划

### 阶段一：核心框架开发（1周）
- [ ] 实现核心组件（TestSuite, APIClient, DataFactory）
- [ ] 开发装饰器系统
- [ ] 创建智能运行器

### 阶段二：功能完善（1周）  
- [ ] 实现性能测试组件
- [ ] 开发报告生成器
- [ ] 创建数据管理系统

### 阶段三：测试迁移（1周）
- [ ] 转换现有测试到新框架
- [ ] 验证功能完整性
- [ ] 性能对比测试

### 阶段四：文档和优化（0.5周）
- [ ] 编写使用文档
- [ ] 性能优化
- [ ] 最终验收测试

---

**联系**: LEO (leoyfm@gmail.com)  
**版本**: v2.0 