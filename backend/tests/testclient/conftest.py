"""
TestClient 测试专用配置
"""
import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from main import app
from tests.factories.user_factory import build_user
from app.db.database import TestSessionLocal, get_db, Base, TestEngine


def override_get_db():
    """覆盖数据库依赖，使用测试数据库"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """设置测试数据库"""
    # 导入所有模型以确保它们被注册到Base.metadata中
    import app.models.database
    
    # 创建所有表
    Base.metadata.create_all(bind=TestEngine)
    
    yield
    
    # 清理：删除所有表
    Base.metadata.drop_all(bind=TestEngine)


@pytest.fixture(scope="session")
def test_client():
    """创建FastAPI TestClient"""
    # 覆盖数据库依赖，使用测试数据库
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # 恢复原始依赖
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """创建测试用户数据"""
    return build_user()


@pytest.fixture
def authenticated_client(test_client, test_user):
    """创建已认证的TestClient"""
    # 注册用户
    register_resp = test_client.post("/api/v1/public/auth/register", json=test_user)
    assert register_resp.status_code in [200, 201], f"用户注册失败: {register_resp.text}"
    
    # 登录获取token
    login_resp = test_client.post("/api/v1/public/auth/login/username", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert login_resp.status_code == 200, f"用户登录失败: {login_resp.text}"
    
    # 解析token
    login_data = login_resp.json()
    token = login_data.get("data", {}).get("access_token")
    assert token, f"获取访问令牌失败: {login_data}"
    
    # 设置认证头
    test_client.headers.update({"Authorization": f"Bearer {token}"})
    
    return test_client, test_user


@pytest.fixture
def clean_database():
    """清理数据库（每个测试前后）"""
    # 测试前清理
    yield
    # 测试后清理（如果需要的话）
    pass 