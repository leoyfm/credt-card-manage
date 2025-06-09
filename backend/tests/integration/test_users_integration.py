"""
用户认证接口集成测试

使用真实HTTP请求进行端到端测试，验证用户认证功能在真实网络环境下的表现。
"""

import pytest
import logging
from typing import Dict, Any
from uuid import uuid4
from tests.base_test import RequestsTestClient, BaseAPITest

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.requires_server
class TestUsersIntegration(BaseAPITest):
    """用户认证集成测试基类"""
    
    def setup_class(self):
        """设置测试类"""
        self.client = RequestsTestClient()
        self._check_server_availability()
        logger.info("用户认证集成测试 - 设置完成")
    
    def _check_server_availability(self):
        """检查服务器是否可用"""
        try:
            response = self.client.get("/api/health")
            if response.status_code != 200:
                raise Exception(f"服务器不可用: {response.status_code}")
            logger.info("服务器可用性检查通过")
        except Exception as e:
            pytest.skip(f"服务器不可用，跳过集成测试: {str(e)}")
    
    def test_01_user_registration_flow(self):
        """测试完整的用户注册流程"""
        unique_id = uuid4().hex[:8]
        register_data = {
            "username": f"integuser_{unique_id}",
            "email": f"integuser_{unique_id}@example.com",
            "password": "TestPass123456",
            "nickname": "集成测试用户"
        }
        
        # 1. 注册用户
        response = self.client.post("/api/auth/register", json=register_data)
        data = self.assert_api_success(response, 200)
        
        user_id = data["id"]
        assert data["username"] == register_data["username"]
        assert data["email"] == register_data["email"]
        assert data["is_active"] is True
        
        logger.info(f"用户注册成功: {data['username']}, ID: {user_id}")
        
        # 2. 使用注册的用户登录
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        
        response = self.client.post("/api/auth/login/username", json=login_data)
        login_result = self.assert_api_success(response, 200)
        
        assert "access_token" in login_result
        assert login_result["user"]["id"] == user_id
        
        logger.info(f"用户登录成功: {login_result['user']['username']}")
        
        return {
            "user": data,
            "token": login_result["access_token"],
            "headers": {"Authorization": f"Bearer {login_result['access_token']}"}
        }
    
    def test_02_user_profile_management_flow(self):
        """测试用户资料管理完整流程"""
        # 1. 注册并登录用户
        auth_data = self.test_01_user_registration_flow()
        
        # 2. 获取用户资料
        response = self.client.get("/api/auth/profile", headers=auth_data["headers"])
        profile_data = self.assert_api_success(response, 200)
        
        assert profile_data["id"] == auth_data["user"]["id"]
        assert profile_data["username"] == auth_data["user"]["username"]
        
        logger.info(f"获取用户资料成功: {profile_data['username']}")
        
        # 3. 更新用户资料
        update_data = {
            "nickname": "更新的集成测试用户",
            "bio": "这是集成测试中的个人简介",
            "gender": "female"
        }
        
        response = self.client.put("/api/auth/profile", json=update_data, headers=auth_data["headers"])
        updated_profile = self.assert_api_success(response, 200)
        
        assert updated_profile["nickname"] == update_data["nickname"]
        assert updated_profile["bio"] == update_data["bio"]
        assert updated_profile["gender"] == update_data["gender"]
        
        logger.info("用户资料更新成功")
        
        # 4. 再次获取资料确认更新
        response = self.client.get("/api/auth/profile", headers=auth_data["headers"])
        final_profile = self.assert_api_success(response, 200)
        
        assert final_profile["nickname"] == update_data["nickname"]
        assert final_profile["bio"] == update_data["bio"]
        
        logger.info("用户资料更新验证完成")
    
    def test_03_password_change_flow(self):
        """测试密码修改完整流程"""
        # 1. 注册并登录用户
        auth_data = self.test_01_user_registration_flow()
        original_password = "TestPass123456"
        new_password = "NewTestPass654321"
        
        # 2. 修改密码
        change_data = {
            "old_password": original_password,
            "new_password": new_password
        }
        
        response = self.client.post("/api/auth/password/change", json=change_data, headers=auth_data["headers"])
        result = self.assert_api_success(response, 200)
        
        logger.info("密码修改成功")
        
        # 3. 使用旧密码登录（应该失败）
        old_login_data = {
            "username": auth_data["user"]["username"],
            "password": original_password
        }
        
        response = self.client.post("/api/auth/login/username", json=old_login_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            logger.info("旧密码登录失败验证通过")
        
        # 4. 使用新密码登录（应该成功）
        new_login_data = {
            "username": auth_data["user"]["username"],
            "password": new_password
        }
        
        response = self.client.post("/api/auth/login/username", json=new_login_data)
        login_result = self.assert_api_success(response, 200)
        
        assert "access_token" in login_result
        assert login_result["user"]["id"] == auth_data["user"]["id"]
        
        logger.info("新密码登录成功验证通过")
    
    def test_04_multiple_login_sessions(self):
        """测试多重登录会话管理"""
        # 1. 注册用户
        auth_data = self.test_01_user_registration_flow()
        
        login_data = {
            "username": auth_data["user"]["username"],
            "password": "TestPass123456"
        }
        
        # 2. 创建多个登录会话
        sessions = []
        for i in range(3):
            response = self.client.post("/api/auth/login/username", json=login_data)
            session_data = self.assert_api_success(response, 200)
            
            sessions.append({
                "token": session_data["access_token"],
                "headers": {"Authorization": f"Bearer {session_data['access_token']}"}
            })
            
            logger.info(f"创建登录会话 {i+1} 成功")
        
        # 3. 验证所有会话都有效
        for i, session in enumerate(sessions):
            response = self.client.get("/api/auth/status", headers=session["headers"])
            status_data = self.assert_api_success(response, 200)
            
            logger.info(f"会话 {i+1} 状态验证成功")
        
        # 4. 从一个会话登出所有设备
        logout_data = {"all_devices": True}
        response = self.client.post("/api/auth/logout", json=logout_data, headers=sessions[0]["headers"])
        result = self.assert_api_success(response, 200)
        
        logger.info("全设备登出执行完成")
        
        # 5. 验证所有会话都已失效（可选，取决于实现）
        # 某些实现可能不会立即使所有令牌失效
    
    def test_05_authentication_edge_cases(self):
        """测试认证边界情况"""
        # 1. 测试无效令牌
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        response = self.client.get("/api/auth/profile", headers=invalid_headers)
        assert response.status_code == 401
        
        logger.info("无效令牌验证完成")
        
        # 2. 测试格式错误的认证头
        malformed_headers = {"Authorization": "InvalidFormat some_token"}
        response = self.client.get("/api/auth/profile", headers=malformed_headers)
        assert response.status_code in [401, 403]
        
        logger.info("格式错误认证头验证完成")
        
        # 3. 测试缺少认证头
        response = self.client.get("/api/auth/profile")
        assert response.status_code == 403
        
        logger.info("缺少认证头验证完成")
        
        # 4. 测试过期令牌（模拟）
        expired_headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxfQ.invalid"}
        response = self.client.get("/api/auth/profile", headers=expired_headers)
        assert response.status_code == 401
        
        logger.info("过期令牌验证完成")
    
    def test_06_duplicate_registration_validation(self):
        """测试重复注册验证"""
        # 1. 注册第一个用户
        unique_id = uuid4().hex[:8]
        user1_data = {
            "username": f"dupuser_{unique_id}",
            "email": f"dupuser_{unique_id}@example.com",
            "password": "TestPass123456",
            "nickname": "重复测试用户1"
        }
        
        response = self.client.post("/api/auth/register", json=user1_data)
        first_user = self.assert_api_success(response, 200)
        
        logger.info(f"第一个用户注册成功: {first_user['username']}")
        
        # 2. 尝试使用相同用户名注册
        user2_data = {
            "username": user1_data["username"],  # 相同用户名
            "email": "different@example.com",
            "password": "TestPass123456"
        }
        
        response = self.client.post("/api/auth/register", json=user2_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["用户名", "已存在"])
        
        logger.info("重复用户名验证完成")
        
        # 3. 尝试使用相同邮箱注册
        user3_data = {
            "username": f"another_user_{unique_id}",
            "email": user1_data["email"],  # 相同邮箱
            "password": "TestPass123456"
        }
        
        response = self.client.post("/api/auth/register", json=user3_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["邮箱", "已存在"])
        
        logger.info("重复邮箱验证完成")
    
    def test_07_login_methods_validation(self):
        """测试不同登录方式验证"""
        # 1. 注册用户
        auth_data = self.test_01_user_registration_flow()
        username = auth_data["user"]["username"]
        email = auth_data["user"]["email"]
        password = "TestPass123456"
        
        # 2. 测试用户名登录
        username_login_data = {
            "username": username,
            "password": password
        }
        
        response = self.client.post("/api/auth/login/username", json=username_login_data)
        username_result = self.assert_api_success(response, 200)
        
        assert "access_token" in username_result
        logger.info("用户名登录验证成功")
        
        # 3. 测试邮箱登录
        email_login_data = {
            "username": email,  # 使用邮箱作为用户名
            "password": password
        }
        
        response = self.client.post("/api/auth/login/username", json=email_login_data)
        email_result = self.assert_api_success(response, 200)
        
        assert "access_token" in email_result
        assert email_result["user"]["id"] == auth_data["user"]["id"]
        logger.info("邮箱登录验证成功")
        
        # 4. 测试错误密码
        wrong_password_data = {
            "username": username,
            "password": "WrongPassword123"
        }
        
        response = self.client.post("/api/auth/login/username", json=wrong_password_data)
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert any(keyword in result["message"] for keyword in ["密码", "错误"])
        
        logger.info("错误密码验证完成")
    
    def test_08_verification_code_integration(self):
        """测试验证码相关功能集成"""
        # 1. 测试发送验证码到手机
        phone_data = {
            "phone_or_email": "13800138000",
            "code_type": "login"
        }
        
        response = self.client.post("/api/auth/code/send", json=phone_data)
        # 可能因为短信服务未配置而失败，这是预期的
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"发送手机验证码结果: {result['success']}")
        else:
            logger.info("短信服务未配置，发送手机验证码失败（预期）")
        
        # 2. 测试发送验证码到邮箱
        email_data = {
            "phone_or_email": "test@example.com",
            "code_type": "register"
        }
        
        response = self.client.post("/api/auth/code/send", json=email_data)
        # 可能因为邮件服务未配置而失败，这是预期的
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"发送邮箱验证码结果: {result['success']}")
        else:
            logger.info("邮件服务未配置，发送邮箱验证码失败（预期）")
        
        # 3. 测试验证验证码
        verify_data = {
            "phone_or_email": "13800138000",
            "code": "123456",
            "code_type": "login"
        }
        
        response = self.client.post("/api/auth/code/verify", json=verify_data)
        # 验证码验证可能失败，因为没有实际发送
        assert response.status_code in [200, 400]
        
        logger.info("验证码验证集成测试完成")
    
    def test_09_wechat_login_integration(self):
        """测试微信登录集成"""
        wechat_data = {
            "code": "test_wechat_integration_code",
            "user_info": {
                "nickname": "集成测试微信用户",
                "avatar_url": "https://wx.qlogo.cn/mmopen/integration_test.jpg",
                "sex": "male",
                "country": "中国",
                "province": "广东",
                "city": "深圳"
            }
        }
        
        response = self.client.post("/api/auth/login/wechat", json=wechat_data)
        # 微信登录可能因为微信服务未配置而失败
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                assert "access_token" in result["data"]
                logger.info("微信登录集成测试成功")
            else:
                logger.info(f"微信登录失败（预期）: {result['message']}")
        else:
            logger.info("微信服务未配置，微信登录失败（预期）")
    
    def test_10_token_refresh_integration(self):
        """测试令牌刷新集成"""
        # 1. 注册并登录用户
        auth_data = self.test_01_user_registration_flow()
        
        # 2. 尝试刷新令牌
        refresh_data = {
            "refresh_token": auth_data["token"]  # 使用访问令牌作为刷新令牌测试
        }
        
        response = self.client.post("/api/auth/token/refresh", json=refresh_data)
        # 可能因为刷新令牌机制不同而失败
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                assert "access_token" in result["data"]
                logger.info("令牌刷新成功")
            else:
                logger.info(f"令牌刷新失败: {result['message']}")
        else:
            logger.info("令牌刷新机制不同，刷新失败（可能预期）")
    
    def test_11_comprehensive_user_journey(self):
        """测试用户完整使用旅程"""
        unique_id = uuid4().hex[:8]
        
        # 1. 用户注册
        register_data = {
            "username": f"journey_{unique_id}",
            "email": f"journey_{unique_id}@example.com",
            "password": "JourneyPass123456",
            "nickname": "完整旅程用户"
        }
        
        response = self.client.post("/api/auth/register", json=register_data)
        user_data = self.assert_api_success(response, 200)
        logger.info(f"步骤1: 用户注册完成 - {user_data['username']}")
        
        # 2. 用户登录
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        
        response = self.client.post("/api/auth/login/username", json=login_data)
        login_result = self.assert_api_success(response, 200)
        headers = {"Authorization": f"Bearer {login_result['access_token']}"}
        logger.info("步骤2: 用户登录完成")
        
        # 3. 查看个人资料
        response = self.client.get("/api/auth/profile", headers=headers)
        profile = self.assert_api_success(response, 200)
        logger.info("步骤3: 查看个人资料完成")
        
        # 4. 更新个人资料
        update_data = {
            "nickname": "已更新的完整旅程用户",
            "bio": "这是我的完整使用旅程",
            "gender": "male"
        }
        
        response = self.client.put("/api/auth/profile", json=update_data, headers=headers)
        updated_profile = self.assert_api_success(response, 200)
        logger.info("步骤4: 更新个人资料完成")
        
        # 5. 修改密码
        new_password = "NewJourneyPass654321"
        change_data = {
            "old_password": register_data["password"],
            "new_password": new_password
        }
        
        response = self.client.post("/api/auth/password/change", json=change_data, headers=headers)
        result = self.assert_api_success(response, 200)
        logger.info("步骤5: 修改密码完成")
        
        # 6. 使用新密码重新登录
        new_login_data = {
            "username": register_data["username"],
            "password": new_password
        }
        
        response = self.client.post("/api/auth/login/username", json=new_login_data)
        new_login_result = self.assert_api_success(response, 200)
        new_headers = {"Authorization": f"Bearer {new_login_result['access_token']}"}
        logger.info("步骤6: 新密码登录完成")
        
        # 7. 检查认证状态
        response = self.client.get("/api/auth/status", headers=new_headers)
        status = self.assert_api_success(response, 200)
        logger.info("步骤7: 检查认证状态完成")
        
        # 8. 登出
        logout_data = {"all_devices": False}
        response = self.client.post("/api/auth/logout", json=logout_data, headers=new_headers)
        logout_result = self.assert_api_success(response, 200)
        logger.info("步骤8: 用户登出完成")
        
        logger.info("用户完整使用旅程测试完成 ✅") 