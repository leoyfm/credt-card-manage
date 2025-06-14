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
        # 导入Base和所有模型
        from app.db.database import Base, TestEngine
        # 导入所有数据库模型以确保它们被注册到Base.metadata中
        import app.models.database  # 这会触发__init__.py中的所有导入
        
        print("正在创建测试数据库表...")
        
        # 删除所有现有表（如果存在）
        Base.metadata.drop_all(bind=TestEngine)
        
        # 创建所有表
        Base.metadata.create_all(bind=TestEngine)
        
        print(f"成功创建了 {len(Base.metadata.tables)} 个表:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        yield
        
        # 测试完成后清理
        print("清理测试数据库表...")
        Base.metadata.drop_all(bind=TestEngine)
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
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