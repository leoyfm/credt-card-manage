import pytest
import subprocess
from tests.factories.user_factory import build_user
from tests.utils.api import APIClient
from tests.utils.db import create_test_session

@pytest.fixture(scope="session", autouse=True)
def create_all_tables():
    # 直接用SQLAlchemy模型自动建表，测试后自动清理
    from app.db.database import Base  # 假设所有模型继承自Base
    session = create_test_session()
    engine = session.get_bind()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    session.close()

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