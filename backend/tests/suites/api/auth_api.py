import pytest
from tests.framework.clients.api import APIClient
import uuid

class TestAuthAPI:
    BASE = "/api/v1/public/auth"

    def setup_method(self):
        self.api = APIClient()
        self.username = "testuser2024"
        self.email = "testuser2024@example.com"
        self.password = "TestPass123456"

    def test_register(self):
        username = f"apitest_{uuid.uuid4().hex[:8]}"
        email = f"{username}@ex.com"
        resp = self.api.post(f"{self.BASE}/register", {
            "username": username,
            "email": email,
            "password": self.password,
            "nickname": "测试用户2024"
        })
        print(resp.status_code, resp.text)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["username"] == username
        assert "access_token" in data["data"]
        self.api.set_auth(data["data"]["access_token"])

    def test_login(self):
        username = f"apitest_{uuid.uuid4().hex[:8]}"
        email = f"{username}@ex.com"
        # 先注册
        self.api.post(f"{self.BASE}/register", {
            "username": username,
            "email": email,
            "password": self.password
        })
        # 登录
        resp = self.api.post(f"{self.BASE}/login/username", {
            "username": username,
            "password": self.password
        })
        print(resp.status_code, resp.text)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == username
        assert "access_token" in data
        self.api.set_auth(data["access_token"])

    def test_refresh_token(self):
        username = f"apitest_{uuid.uuid4().hex[:8]}"
        email = f"{username}@ex.com"
        # 注册并登录
        reg = self.api.post(f"{self.BASE}/register", {
            "username": username,
            "email": email,
            "password": self.password
        })
        print(reg.status_code, reg.text)
        tokens = reg.json()["data"]
        # 刷新令牌
        resp = self.api.post(f"{self.BASE}/refresh-token", {
            "refresh_token": tokens["refresh_token"]
        })
        print(resp.status_code, resp.text)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "access_token" in data
        assert data["refresh_token"] == tokens["refresh_token"] 