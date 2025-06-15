"""
用户认证功能测试

使用测试数据库进行完整的用户认证流程测试
"""
import pytest
from tests.factories.user_factory import build_user


class TestUserAuth:
    """用户认证测试类"""
    
    def test_user_register_success(self, test_client):
        """测试用户注册成功"""
        user_data = build_user()
        
        response = test_client.post("/api/v1/public/auth/register", json=user_data)
        
        assert response.status_code in [200, 201], f"注册失败: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"注册响应格式错误: {data}"
        assert "data" in data, "响应中缺少data字段"
        
        user_info = data["data"]
        assert user_info.get("username") == user_data["username"], "返回的用户名不匹配"
        assert user_info.get("email") == user_data["email"], "返回的邮箱不匹配"
        assert "user_id" in user_info, "返回的用户信息中缺少user_id"
        assert "access_token" in user_info, "返回的用户信息中缺少access_token"
    
    def test_user_register_duplicate_username(self, test_client):
        """测试重复用户名注册失败"""
        user_data = build_user()
        
        # 第一次注册
        response1 = test_client.post("/api/v1/public/auth/register", json=user_data)
        assert response1.status_code in [200, 201], f"首次注册失败: {response1.text}"
        
        # 第二次注册相同用户名
        response2 = test_client.post("/api/v1/public/auth/register", json=user_data)
        assert response2.status_code == 400, f"重复注册应该失败，但状态码是: {response2.status_code}"
        
        data = response2.json()
        # 检查错误响应格式（可能是统一格式或FastAPI默认格式）
        if "success" in data:
            assert data.get("success") is False, "重复注册应该返回失败状态"
        else:
            # FastAPI默认错误格式
            assert "detail" in data, "错误响应中应该包含detail字段"
            assert "用户名已存在" in data["detail"], "错误信息应该提示用户名已存在"
    
    def test_user_login_username_success(self, test_client):
        """测试用户名登录成功"""
        user_data = build_user()
        
        # 先注册用户
        register_resp = test_client.post("/api/v1/public/auth/register", json=user_data)
        assert register_resp.status_code in [200, 201], f"注册失败: {register_resp.text}"
        
        # 用户名登录
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = test_client.post("/api/v1/public/auth/login/username", json=login_data)
        assert response.status_code == 200, f"登录失败: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"登录响应格式错误: {data}"
        assert "data" in data, "登录响应中缺少data字段"
        
        login_result = data["data"]
        assert "access_token" in login_result, "登录响应中缺少访问令牌"
        assert "token_type" in login_result, "登录响应中缺少令牌类型"
        assert login_result.get("token_type") == "bearer", "令牌类型应该是bearer"
    
    def test_get_user_profile_success(self, authenticated_client):
        """测试获取用户资料成功"""
        test_client, user_data = authenticated_client
        
        response = test_client.get("/api/v1/user/profile/info")
        assert response.status_code == 200, f"获取用户资料失败: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, f"获取用户资料响应格式错误: {data}"
        
        profile = data["data"]
        assert profile.get("username") == user_data["username"], "用户资料中用户名不匹配"
        assert profile.get("email") == user_data["email"], "用户资料中邮箱不匹配"
        assert "id" in profile, "用户资料中缺少ID"
    
    def test_complete_auth_flow(self, test_client):
        """测试完整的认证流程"""
        user_data = build_user()
        
        # 1. 注册用户
        register_resp = test_client.post("/api/v1/public/auth/register", json=user_data)
        assert register_resp.status_code in [200, 201], "注册失败"
        
        # 2. 用户名登录
        login_resp = test_client.post("/api/v1/public/auth/login/username", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        assert login_resp.status_code == 200, "登录失败"
        
        # 3. 获取访问令牌
        token = login_resp.json()["data"]["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        
        # 4. 获取用户资料
        profile_resp = test_client.get("/api/v1/user/profile/info")
        assert profile_resp.status_code == 200, "获取用户资料失败"
        
        profile_data = profile_resp.json()["data"]
        assert profile_data["username"] == user_data["username"], "用户资料验证失败" 