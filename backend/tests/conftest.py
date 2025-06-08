"""
Pytest配置文件

提供测试所需的fixture和工具函数。
"""

import os
import pytest
from typing import Dict, Any, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from uuid import uuid4

# 设置测试环境变量 - 如果没有设置则使用默认值
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://credit_user:credit_password@localhost:5432/test"
os.environ["DEBUG"] = "true"

from main import app
from database import get_db, Base
from config import settings


# 测试数据库设置 - 使用环境变量中的数据库URL
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://credit_user:credit_password@localhost:5432/test")
# SQLite需要特殊配置
if TEST_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖，使用测试数据库"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆盖应用的数据库依赖
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def test_db():
    """创建测试数据库表"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """创建测试数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """测试用户数据"""
    unique_id = uuid4().hex[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "TestPass123456",
        "nickname": "测试用户",
        "phone": f"138{int(unique_id[:7], 16) % 100000000:08d}"  # 使用唯一的11位数字手机号
    }


@pytest.fixture
def test_card_data() -> Dict[str, Any]:
    """测试信用卡数据"""
    unique_id = uuid4().hex[:8]
    return {
        "card_name": "测试信用卡",
        "bank_name": "测试银行",
        "card_number": f"123456789{int(unique_id[:7], 16) % 1000000:06d}",  # 使用纯数字的唯一信用卡号
        "card_type": "visa",
        "credit_limit": 50000.00,
        "expiry_month": 12,
        "expiry_year": 2027,
        "billing_day": 5,  # 修复：使用正确的字段名
        "due_day": 25,     # 修复：使用正确的字段名
        "used_amount": 0.0,  # 添加必需的字段
        "points_per_yuan": 1.0,
        "currency": "CNY",
        "annual_fee_enabled": False
    }


@pytest.fixture
def test_transaction_data() -> Dict[str, Any]:
    """测试交易数据"""
    return {
        "transaction_type": "expense",
        "amount": 199.50,
        "transaction_date": "2024-06-08T14:30:00",
        "merchant_name": "星巴克咖啡",
        "description": "购买咖啡和蛋糕",
        "category": "dining",
        "status": "completed",
        "points_earned": 19.95,
        "points_rate": 1.0,
        "reference_number": "TXN202406081430001",
        "location": "北京市朝阳区三里屯",
        "is_installment": False,
        "notes": "使用优惠券消费"
    }


@pytest.fixture
def authenticated_user(client: TestClient, test_user_data: Dict[str, Any], test_db) -> Dict[str, Any]:
    """创建认证用户并返回用户信息和token"""
    # 注册用户
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 200  # 修复：注册接口实际返回200
    
    # 登录获取token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login/username", json=login_data)
    assert response.status_code == 200
    
    result = response.json()
    if result is None or "data" not in result:
        raise ValueError(f"登录响应格式错误: {response.text}")
    
    return {
        "user": result["data"]["user"],
        "token": result["data"]["access_token"],
        "headers": {"Authorization": f"Bearer {result['data']['access_token']}"}
    }


@pytest.fixture
def test_card(client: TestClient, authenticated_user: Dict[str, Any], test_card_data: Dict[str, Any], test_db) -> Dict[str, Any]:
    """创建测试信用卡"""
    response = client.post(
        "/api/cards/",
        json=test_card_data,
        headers=authenticated_user["headers"]
    )
    assert response.status_code == 200  # 修复：创建信用卡接口实际返回200
    return response.json()["data"]


def create_test_transaction(
    client: TestClient,
    headers: Dict[str, str],
    card_id: str,
    transaction_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """创建测试交易记录的辅助函数"""
    if transaction_data is None:
        transaction_data = {
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00+08:00",  # 添加时区信息
            "merchant_name": "测试商户",
            "description": "测试交易",
            "category": "other",
            "status": "completed",
            "points_earned": 10.0,  # 添加必需字段
            "points_rate": 1.0,     # 添加必需字段
            "reference_number": f"TEST{uuid4().hex[:8]}",  # 添加唯一的参考号
            "location": "测试地点",
            "is_installment": False
        }
    
    transaction_data["card_id"] = card_id
    
    response = client.post(
        "/api/transactions/",
        json=transaction_data,
        headers=headers
    )
    assert response.status_code == 200  # 修复：创建交易接口实际返回200
    return response.json()["data"]


def assert_response_success(response, expected_status_code: int = 200):
    """断言响应成功的辅助函数"""
    assert response.status_code == expected_status_code
    result = response.json()
    assert result["success"] is True
    assert "data" in result
    return result["data"]


def assert_response_error(response, expected_status_code: int = 400):
    """断言响应错误的辅助函数"""
    assert response.status_code == expected_status_code
    result = response.json()
    if "success" in result:
        assert result["success"] is False
    return result 