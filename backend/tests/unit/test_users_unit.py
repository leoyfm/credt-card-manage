"""
用户认证接口单元测试

使用FastAPI TestClient进行快速单元测试，测试用户注册、登录、资料管理等核心功能。
"""

import pytest
import logging
from typing import Dict, Any
from uuid import uuid4
from tests.base_test import FastAPITestClient, BaseAPITest

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestUsersUnit:
    """用户认证单元测试基类"""
    
    def setup_method(self):
        """设置测试方法"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        logger.info("用户认证单元测试 - 设置完成")
    
    def test_01_register_with_username_email_success(self):
        """测试用户名邮箱注册成功"""
        unique_id = uuid4().hex[:8]
        register_data = {
            "username": f"newuser_{unique_id}",
            "email": f"newuser_{unique_id}@example.com",
            "password": "TestPass123456",
            "nickname": "新用户"
        }
        
        response = self.client.post("/api/auth/register", json=register_data)
        data = self.api_test.assert_api_success(response, 200)
        
        assert data["username"] == register_data["username"]
        assert data["email"] == register_data["email"]
        assert data["nickname"] == register_data["nickname"]
        assert "id" in data
        assert data["is_active"] is True
        
        logger.info(f"用户注册成功: {data['username']}")
    
    def test_02_register_with_phone_validation(self):
        """测试带手机号注册（验证码验证失败是预期的）"""
        unique_id = uuid4().hex[:8]
        register_data = {
            "username": f"phoneuser_{unique_id}",
            "email": f"phoneuser_{unique_id}@example.com",
            "password": "TestPass123456",
            "phone": f"138{int(unique_id[:7], 16) % 100000000:08d}",
            "verification_code": "123456"
        }
        
        response = self.client.post("/api/auth/register", json=register_data)
        # 验证码验证失败是预期的
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert "验证码" in result["message"]
        
        logger.info("手机号注册验证测试完成")
    
    def test_03_register_duplicate_username(self):
        """测试重复用户名注册失败"""
        # 先创建一个用户
        user_data = self.api_test.setup_test_user()
        
        # 尝试使用相同用户名注册
        register_data = {
            "username": user_data["user"]["username"],
            "email": "different@example.com",
            "password": "TestPass123456"
        }
        
        response = self.client.post("/api/auth/register", json=register_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["用户名", "已存在"])
        
        logger.info("重复用户名验证测试完成")
    
    def test_04_register_duplicate_email(self):
        """测试重复邮箱注册失败"""
        # 先创建一个用户
        user_data = self.api_test.setup_test_user()
        
        unique_id = uuid4().hex[:8]
        register_data = {
            "username": f"newuser_{unique_id}",
            "email": user_data["user"]["email"],
            "password": "TestPass123456"
        }
        
        response = self.client.post("/api/auth/register", json=register_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["邮箱", "已存在"])
        
        logger.info("重复邮箱验证测试完成")
    
    def test_05_register_validation_failures(self):
        """测试注册数据验证失败"""
        # 测试用户名太短
        short_username_data = {
            "username": "ab",
            "email": "test@example.com",
            "password": "TestPass123456"
        }
        response = self.client.post("/api/auth/register", json=short_username_data)
        assert response.status_code == 422
        
        # 测试无效邮箱格式
        unique_id = uuid4().hex[:8]
        invalid_email_data = {
            "username": f"testuser_{unique_id}",
            "email": "invalid-email",
            "password": "TestPass123456"
        }
        response = self.client.post("/api/auth/register", json=invalid_email_data)
        assert response.status_code == 422
        
        # 测试弱密码
        weak_password_data = {
            "username": f"testuser2_{unique_id}",
            "email": f"test2_{unique_id}@example.com",
            "password": "123456"
        }
        response = self.client.post("/api/auth/register", json=weak_password_data)
        assert response.status_code == 422
        
        logger.info("注册数据验证测试完成")
    
    def test_06_login_username_password_success(self):
        """测试用户名密码登录成功"""
        user_data = self.api_test.setup_test_user()
        
        login_data = {
            "username": user_data["user"]["username"],
            "password": user_data["user"]["password"]
        }
        
        response = self.client.post("/api/auth/login/username", json=login_data)
        data = self.api_test.assert_api_success(response, 200)
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        
        user_info = data["user"]
        assert user_info["username"] == user_data["user"]["username"]
        assert user_info["email"] == user_data["user"]["email"]
        
        logger.info(f"用户登录成功: {user_info['username']}")
    
    def test_07_login_email_password_success(self):
        """测试邮箱密码登录成功"""
        user_data = self.api_test.setup_test_user()
        
        login_data = {
            "username": user_data["user"]["email"],  # 使用邮箱登录
            "password": user_data["user"]["password"]
        }
        
        response = self.client.post("/api/auth/login/username", json=login_data)
        data = self.api_test.assert_api_success(response, 200)
        
        assert "access_token" in data
        user_info = data["user"]
        assert user_info["email"] == user_data["user"]["email"]
        
        logger.info(f"邮箱登录成功: {user_info['email']}")
    
    def test_08_login_wrong_password(self):
        """测试错误密码登录失败"""
        user_data = self.api_test.setup_test_user()
        
        login_data = {
            "username": user_data["user"]["username"],
            "password": "WrongPassword123"
        }
        
        response = self.client.post("/api/auth/login/username", json=login_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["密码", "错误"])
        
        logger.info("错误密码登录验证完成")
    
    def test_09_login_nonexistent_user(self):
        """测试不存在用户登录失败"""
        login_data = {
            "username": "nonexistent_user_12345",
            "password": "TestPass123456"
        }
        
        response = self.client.post("/api/auth/login/username", json=login_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["用户", "不存在"])
        
        logger.info("不存在用户登录验证完成")
    
    def test_10_get_profile_success(self):
        """测试获取用户资料成功"""
        # 创建并登录用户
        user_data = self.api_test.setup_test_user()
        
        response = self.client.get("/api/auth/profile", headers=user_data["headers"])
        data = self.api_test.assert_api_success(response, 200)
        
        assert data["username"] == user_data["user"]["username"]
        assert data["email"] == user_data["user"]["email"]
        assert "id" in data
        
        logger.info(f"获取用户资料成功: {data['username']}")
    
    def test_11_get_profile_unauthorized(self):
        """测试未认证获取用户资料失败"""
        response = self.client.get("/api/auth/profile")
        assert response.status_code == 403
        
        logger.info("未认证获取资料验证完成")
    
    def test_12_get_profile_invalid_token(self):
        """测试无效token获取用户资料失败"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 401
        
        logger.info("无效token验证完成")
    
    def test_13_update_profile_success(self):
        """测试更新用户资料成功"""
        # 创建并登录用户
        user_data = self.api_test.setup_test_user()
        
        update_data = {
            "nickname": "更新后的昵称",
            "bio": "这是更新的个人简介",
            "gender": "male"
        }
        
        response = self.client.put("/api/auth/profile", json=update_data, headers=user_data["headers"])
        data = self.api_test.assert_api_success(response, 200)
        
        assert data["nickname"] == update_data["nickname"]
        assert data["bio"] == update_data["bio"]
        assert data["gender"] == update_data["gender"]
        
        logger.info(f"用户资料更新成功: {data['nickname']}")
    
    def test_14_change_password_success(self):
        """测试修改密码成功"""
        # 创建并登录用户
        user_data = self.api_test.setup_test_user()
        
        change_data = {
            "old_password": user_data["user"]["password"],
            "new_password": "NewTestPass123456"
        }
        
        response = self.client.post("/api/auth/password/change", json=change_data, headers=user_data["headers"])
        data = self.api_test.assert_api_success(response, 200)
        
        # 检查响应格式，可能返回status字段
        assert "changed" in data.get("status", "") or "密码修改成功" in data.get("message", "")
        
        logger.info("密码修改成功")
    
    def test_15_change_password_wrong_old_password(self):
        """测试使用错误的旧密码修改密码失败"""
        # 创建并登录用户
        user_data = self.api_test.setup_test_user()
        
        change_data = {
            "old_password": "WrongOldPassword123",
            "new_password": "NewTestPass123456"
        }
        
        response = self.client.post("/api/auth/password/change", json=change_data, headers=user_data["headers"])
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["密码", "错误"])
        
        logger.info("错误旧密码验证完成")
    
    def test_16_logout_success(self):
        """测试登出成功"""
        # 创建并登录用户
        user_data = self.api_test.setup_test_user()
        
        logout_data = {"all_devices": False}
        response = self.client.post("/api/auth/logout", json=logout_data, headers=user_data["headers"])
        data = self.api_test.assert_api_success(response, 200)
        
        # 检查响应格式，可能返回status字段
        assert "logged_out" in data.get("status", "") or "登出成功" in data.get("message", "")
        
        logger.info("用户登出成功")
    
    def test_17_check_auth_status_success(self):
        """测试检查认证状态成功"""
        # 创建并登录用户
        user_data = self.api_test.setup_test_user()
        
        response = self.client.get("/api/auth/status", headers=user_data["headers"])
        data = self.api_test.assert_api_success(response, 200)
        
        # 检查响应格式，可能包含user_id或username字段
        assert "user_id" in data or "username" in data or "user" in data
        
        # 如果有user字段，记录用户名
        if "user" in data:
            logger.info(f"认证状态检查成功: {data['user']['username']}")
        elif "username" in data:
            logger.info(f"认证状态检查成功: {data['username']}")
        else:
            logger.info("认证状态检查成功")
    
    def test_18_malformed_authorization_header(self):
        """测试格式错误的认证头"""
        headers = {"Authorization": "InvalidFormat"}
        response = self.client.get("/api/auth/profile", headers=headers)
        # API可能返回401或403，都是合理的认证失败状态码
        assert response.status_code in [401, 403]
        
        logger.info("格式错误认证头验证完成")
    
    def test_19_data_validation_comprehensive(self):
        """测试数据验证的全面性"""
        test_cases = [
            # 用户名测试
            {"username": "", "email": "test@example.com", "password": "TestPass123456"},  # 空用户名
            {"username": "a" * 51, "email": "test@example.com", "password": "TestPass123456"},  # 用户名过长
            {"username": "user@name", "email": "test@example.com", "password": "TestPass123456"},  # 用户名包含特殊字符
            
            # 邮箱测试
            {"username": "testuser", "email": "", "password": "TestPass123456"},  # 空邮箱
            {"username": "testuser", "email": "notanemail", "password": "TestPass123456"},  # 无效邮箱
            {"username": "testuser", "email": "test@", "password": "TestPass123456"},  # 不完整邮箱
            
            # 密码测试
            {"username": "testuser", "email": "test@example.com", "password": ""},  # 空密码
            {"username": "testuser", "email": "test@example.com", "password": "123"},  # 密码过短
            {"username": "testuser", "email": "test@example.com", "password": "password"},  # 密码没有数字
            {"username": "testuser", "email": "test@example.com", "password": "12345678"},  # 密码没有字母
        ]
        
        for i, invalid_data in enumerate(test_cases):
            response = self.client.post("/api/auth/register", json=invalid_data)
            assert response.status_code == 422, f"测试用例 {i+1} 应该返回422: {invalid_data}"
        
        logger.info(f"数据验证测试完成，共验证 {len(test_cases)} 个无效输入案例") 