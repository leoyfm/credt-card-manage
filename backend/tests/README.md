# 新一代pytest友好型测试框架设计文档（2024修正版）

## 1. 设计目标
- 只保留两类测试：API测试（集成/接口）和功能测试（单元/服务/数据库直连）
- 100%兼容pytest生态，支持一键批量运行、分组、报告、覆盖率等
- 极简、声明式、可读性强，保留数据工厂/fixture/链式断言风格
- 支持自动化、CI/CD、数据库隔离、环境切换

## 2. 目录结构
```
tests/
├── api/                    # API集成测试（HTTP请求开发服务器）
│   └── test_auth_api.py
├── unit/                   # 功能/服务/模型单元测试（直连测试数据库）
│   └── test_auth_service.py
├── factories/              # 数据工厂
│   └── user_factory.py
├── conftest.py             # 全局fixture
├── utils/                  # 断言工具等
│   └── assert_utils.py
└── README.md               # 测试说明
```

## 3. 测试类型说明

### 3.1 API测试（集成/接口测试）
- 通过requests等HTTP客户端，直接请求开发服务器（如 http://127.0.0.1:8000）
- 只测接口输入输出、权限、响应结构、异常处理，不关心内部实现
- 数据准备通过API注册/登录/创建，或用fixture自动准备
- 适合接口联调、回归测试、权限/安全/异常分支验证

### 3.2 功能测试（单元/服务/数据库直连）
- 直接连接测试数据库（如 postgresql://credit_user:credit_password@localhost:5432/test）
- 直接调用后端内部方法（如service、repository、model等），验证业务逻辑、数据一致性、边界和异常
- 数据准备用工厂/fixture直接插入测试数据，或用事务/回滚保证隔离
- 适合业务逻辑验证、复杂数据流、数据库操作、事务一致性、边界条件

## 4. 数据工厂与fixture
- 数据工厂只负责生成数据（如build_user），不负责注册/登录等副作用
- pytest fixture负责注册用户、登录、清理等，返回api、user等对象

## 5. 链式断言工具
- 提供assert_utils.py，定义如`assert_response(resp).success().with_data(...)`等链式断言

## 6. 用例风格
- 文件、类、方法全部以`test_`/`Test`开头
- 依赖数据/用户/环境全部用fixture注入
- 不使用自定义装饰器

## 7. 运行方式
- 运行所有API测试：
  ```bash
  pytest tests/api/
  ```
- 运行所有功能/单元测试：
  ```bash
  pytest tests/unit/
  ```
- 运行特定测试文件：
  ```bash
  pytest tests/api/test_auth_api.py -v
  pytest tests/unit/test_auth_service.py -v
  ```
- 支持pytest-xdist并行、pytest-cov覆盖率、pytest-html报告等

## 8. 数据库环境
- 开发数据库：postgresql://credit_user:credit_password@localhost:5432/credit_card_db
- 测试数据库：postgresql://credit_user:credit_password@localhost:5432/test
- 功能测试/单元测试必须直连测试数据库，不能污染开发库

## 9. 示例代码

### 9.1 factories/user_factory.py
```python
import uuid

def build_user(**kwargs):
    username = kwargs.get("username") or f"user_{uuid.uuid4().hex[:8]}"
    email = kwargs.get("email") or f"{username}@example.com"
    password = kwargs.get("password") or "TestPass123456"
    return {"username": username, "email": email, "password": password}
```

### 9.2 conftest.py
```python
import pytest
from tests.factories.user_factory import build_user
from tests.framework.clients.api import APIClient

@pytest.fixture
def user_and_api():
    user = build_user()
    api = APIClient()
    api.post("/api/v1/public/auth/register", user)
    resp = api.post("/api/v1/public/auth/login/username", {
        "username": user["username"],
        "password": user["password"]
    })
    token = None
    try:
        token = resp.json().get("data", {}).get("access_token")
    except Exception:
        pass
    if token:
        api.set_auth(token)
    return api, user
```

### 9.3 utils/assert_utils.py
```python
class AssertResponse:
    def __init__(self, resp):
        self.resp = resp
        try:
            self.data = resp.json()
        except Exception:
            self.data = None

    def success(self):
        assert self.resp.status_code == 200, f"期望200，实际{self.resp.status_code}"
        assert self.data and self.data.get("success", True), f"响应体: {self.data}"
        return self

    def fail(self, status_code=None, code=None):
        if status_code:
            assert self.resp.status_code == status_code, f"期望失败码{status_code}，实际{self.resp.status_code}"
        else:
            assert self.resp.status_code >= 400, f"期望失败，实际{self.resp.status_code}"
        if code:
            assert self.data and self.data.get("code") == code, f"错误码不符: {self.data}"
        return self

    def with_data(self, **expected):
        actual = self.data.get("data", {}) if self.data else {}
        for k, v in expected.items():
            assert actual.get(k) == v, f"字段{k}期望{v}，实际{actual.get(k)}"
        return self

def assert_response(resp):
    return AssertResponse(resp)
```

### 9.4 api/test_auth_api.py
```python
from tests.framework.clients.api import APIClient
from tests.utils.assert_utils import assert_response
from tests.factories.user_factory import build_user
import pytest

BASE = "/api/v1/public/auth"

class TestAuthAPI:
    def test_register_success(self):
        user = build_user()
        api = APIClient()
        resp = api.post(f"{BASE}/register", user)
        assert_response(resp).success().with_data(username=user["username"])

    def test_register_duplicate(self):
        user = build_user()
        api = APIClient()
        api.post(f"{BASE}/register", user)
        resp = api.post(f"{BASE}/register", user)
        assert_response(resp).fail()

    def test_login_success(self, user_and_api):
        api, user = user_and_api
        resp = api.post(f"{BASE}/login/username", {
            "username": user["username"],
            "password": user["password"]
        })
        assert_response(resp).success().with_data(username=user["username"])

    def test_login_wrong_password(self, user_and_api):
        api, user = user_and_api
        resp = api.post(f"{BASE}/login/username", {
            "username": user["username"],
            "password": "WrongPass123"
        })
        assert_response(resp).fail()

    def test_login_user_not_exist(self):
        api = APIClient()
        resp = api.post(f"{BASE}/login/username", {
            "username": "not_exist_user",
            "password": "AnyPass123"
        })
        assert_response(resp).fail()
```

### 9.5 unit/test_auth_service.py
```python
import pytest
from app.services.auth_service import AuthService
from app.models.schemas.auth import UserRegister, UserLogin
from app.db.session import get_db
from sqlalchemy.orm import Session

@pytest.fixture
def db():
    # 这里假设有一个测试数据库连接工厂
    from app.db.session import create_test_session
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def auth_service(db: Session):
    return AuthService(db)

class TestAuthService:
    def test_register_and_login(self, auth_service: AuthService):
        user_in = UserRegister(username="testuser", email="testuser@example.com", password="TestPass123456")
        user = auth_service.register(user_in)
        assert user.username == "testuser"
        login_in = UserLogin(username="testuser", password="TestPass123456")
        token = auth_service.login(login_in)
        assert token is not None

    def test_register_duplicate(self, auth_service: AuthService):
        user_in = UserRegister(username="dupuser", email="dupuser@example.com", password="TestPass123456")
        auth_service.register(user_in)
        with pytest.raises(Exception):
            auth_service.register(user_in)
```

---

如需扩展其他模块测试，建议严格遵循上述风格和目录结构。 