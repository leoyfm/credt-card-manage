import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 现在可以正常导入项目模块
from tests.factories.user_factory import build_user
from tests.utils.api import APIClient
from tests.utils.db import create_test_session

@pytest.fixture(scope="session", autouse=True)
def create_all_tables():
    """创建测试数据库表"""
    try:
        from app.db.database import Base
        session = create_test_session()
        engine = session.get_bind()
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
        session.close()
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        yield

@pytest.fixture
def user_and_api():
    """创建用户和API客户端"""
    user = build_user()
    api = APIClient()
    
    # 注册用户
    api.post("/api/v1/public/auth/register", user)
    
    # 登录获取token
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