"""
用户管理功能单元测试

使用FastAPI TestClient进行用户管理功能的单元测试。
测试覆盖用户管理的CRUD操作、权限验证、数据筛选和边界条件。

覆盖范围：
- 用户列表查询和筛选
- 用户详情查看
- 用户状态管理
- 管理员权限设置
- 用户删除操作
- 登录日志查看
- 微信绑定信息
- 用户统计数据
- 认证和权限验证
- 边界条件和异常处理
"""

import pytest
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from uuid import uuid4

from tests.base_test import FastAPITestClient, BaseAPITest

logger = logging.getLogger(__name__)


class UsersTestDataGenerator:
    """用户管理测试数据生成器"""
    
    @staticmethod
    def generate_test_user_data() -> Dict[str, Any]:
        """生成测试用户数据"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "username": f"test_user_mgmt_{unique_id}",
            "email": f"testuser{unique_id}@example.com",
            "password": "TestPass123456",
            "nickname": f"测试用户管理{unique_id}"
        }
    
    @staticmethod
    def generate_admin_user_data() -> Dict[str, Any]:
        """生成测试管理员用户数据"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "username": f"admin_user_{unique_id}",
            "email": f"admin{unique_id}@example.com", 
            "password": "AdminPass123456",
            "nickname": f"测试管理员{unique_id}"
        }


@pytest.mark.unit
class TestUsersUnit:
    """用户管理单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        # 创建额外测试用户
        self.additional_users = []
        for i in range(3):
            user_data = UsersTestDataGenerator.generate_test_user_data()
            response = self.client.post("/api/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                self.additional_users.append(user_data)
        
        logger.info(f"✅ 用户管理单元测试环境准备就绪: 主用户{self.test_user['user_id']}, 额外用户{len(self.additional_users)}个")

    # ==================== 用户列表查询测试 ====================
    
    def test_01_get_users_list_success(self):
        """测试获取用户列表（成功）"""
        response = self.client.get("/api/users/", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证响应结构
        assert "items" in data
        assert "pagination" in data
        
        # 验证分页信息
        self.api_test.assert_pagination_response(data, min_items=1)
        
        # 验证用户数据结构
        if data["items"]:
            user = data["items"][0]
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "is_active" in user
            assert "created_at" in user
        
        logger.info("✅ 用户列表获取成功")

    def test_02_get_users_list_with_keyword_filter(self):
        """测试带关键词筛选的用户列表"""
        # 使用已知的用户名进行搜索
        test_username = self.test_user['user']['username']
        search_keyword = test_username[:8]  # 取用户名前8位作为搜索关键词
        
        response = self.client.get(
            "/api/users/",
            params={"keyword": search_keyword},
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证筛选结果
        assert "items" in data
        self.api_test.assert_pagination_response(data)
        
        # 验证筛选逻辑（如果有结果，应该包含搜索关键词）
        for user in data["items"]:
            user_info = f"{user['username']} {user['email']} {user.get('nickname', '')}"
            # 关键词应该在用户名、邮箱或昵称中
            assert any(search_keyword.lower() in field.lower() for field in [
                user['username'], user['email'], user.get('nickname', '')
            ])
        
        logger.info(f"✅ 关键词筛选测试成功: {search_keyword}")

    def test_03_get_users_list_with_status_filter(self):
        """测试带状态筛选的用户列表"""
        response = self.client.get(
            "/api/users/",
            params={"is_active": True},
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证筛选结果
        assert "items" in data
        self.api_test.assert_pagination_response(data)
        
        # 验证所有返回用户都是激活状态
        for user in data["items"]:
            assert user["is_active"] == True
        
        logger.info("✅ 状态筛选测试成功")

    def test_04_get_users_list_pagination(self):
        """测试用户列表分页功能"""
        # 测试第一页
        response = self.client.get(
            "/api/users/",
            params={"page": 1, "page_size": 2},
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证分页响应
        self.api_test.assert_pagination_response(data)
        assert data["pagination"]["current_page"] == 1
        assert data["pagination"]["page_size"] == 2
        
        # 如果有多于2个用户，测试第二页
        if data["pagination"]["total"] > 2:
            response2 = self.client.get(
                "/api/users/",
                params={"page": 2, "page_size": 2},
                headers=self.headers
            )
            data2 = self.api_test.assert_api_success(response2, 200)
            assert data2["pagination"]["current_page"] == 2
        
        logger.info("✅ 分页功能测试成功")

    # ==================== 用户详情查看测试 ====================
    
    def test_05_get_user_by_id_success(self):
        """测试获取用户详情（成功）"""
        user_id = self.test_user['user_id']
        response = self.client.get(f"/api/users/{user_id}", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证用户详情结构
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "nickname" in data
        assert "is_active" in data
        assert "is_verified" in data
        assert "is_admin" in data
        assert "created_at" in data
        assert "last_login_at" in data
        
        # 验证用户ID匹配
        assert data["id"] == user_id
        
        logger.info("✅ 用户详情获取成功")

    def test_06_get_user_by_id_not_found(self):
        """测试获取不存在的用户详情"""
        fake_user_id = str(uuid4())
        response = self.client.get(f"/api/users/{fake_user_id}", headers=self.headers)
        self.api_test.assert_api_error(response, 404)
        
        logger.info("✅ 用户不存在错误处理正确")

    def test_07_get_user_by_invalid_id(self):
        """测试使用无效ID格式获取用户"""
        invalid_id = "invalid-uuid-format"
        response = self.client.get(f"/api/users/{invalid_id}", headers=self.headers)
        # 可能返回400或422，取决于UUID验证的实现
        assert response.status_code in [400, 422, 500]
        
        logger.info("✅ 无效ID格式错误处理正确")

    # ==================== 用户状态管理测试 ====================
    
    def test_08_update_user_status_forbidden_self(self):
        """测试用户不能修改自己的状态"""
        user_id = self.test_user['user_id']
        update_data = {"is_active": False}
        
        response = self.client.put(
            f"/api/users/{user_id}/status",
            json=update_data,
            headers=self.headers
        )
        # 用户不能修改自己的状态，应该返回403
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 用户无法修改自己状态的限制正确")

    def test_09_update_user_status_non_admin(self):
        """测试非管理员用户无法修改其他用户状态"""
        if self.additional_users:
            # 创建另一个用户并获取其ID
            other_user_data = self.additional_users[0]
            login_response = self.client.post("/api/auth/login/username", json={
                "username": other_user_data["username"],
                "password": other_user_data["password"]
            })
            
            if login_response.status_code == 200:
                # 尝试修改第三个用户的状态
                fake_user_id = str(uuid4())
                update_data = {"is_active": False}
                
                response = self.client.put(
                    f"/api/users/{fake_user_id}/status",
                    json=update_data,
                    headers=self.headers
                )
                # 非管理员应该被拒绝访问
                self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 非管理员权限限制正确")

    # ==================== 管理员权限设置测试 ====================
    
    def test_10_update_admin_status_forbidden_self(self):
        """测试用户不能修改自己的管理员权限"""
        user_id = self.test_user['user_id']
        update_data = {"is_admin": True}
        
        response = self.client.put(
            f"/api/users/{user_id}/admin",
            json=update_data,
            headers=self.headers
        )
        # 用户不能修改自己的管理员权限，应该返回403
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 用户无法修改自己管理员权限的限制正确")

    def test_11_update_admin_status_non_admin(self):
        """测试非管理员用户无法修改管理员权限"""
        fake_user_id = str(uuid4())
        update_data = {"is_admin": True}
        
        response = self.client.put(
            f"/api/users/{fake_user_id}/admin",
            json=update_data,
            headers=self.headers
        )
        # 非管理员应该被拒绝访问
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 非管理员设置管理员权限的限制正确")

    # ==================== 用户删除测试 ====================
    
    def test_12_delete_user_forbidden_self(self):
        """测试用户不能删除自己"""
        user_id = self.test_user['user_id']
        
        response = self.client.delete(f"/api/users/{user_id}", headers=self.headers)
        # 用户不能删除自己，应该返回403
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 用户无法删除自己的限制正确")

    def test_13_delete_user_non_admin(self):
        """测试非管理员用户无法删除其他用户"""
        fake_user_id = str(uuid4())
        
        response = self.client.delete(f"/api/users/{fake_user_id}", headers=self.headers)
        # 非管理员应该被拒绝访问
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 非管理员删除用户的限制正确")

    def test_14_delete_user_not_found(self):
        """测试删除不存在的用户"""
        fake_user_id = str(uuid4())
        
        response = self.client.delete(f"/api/users/{fake_user_id}", headers=self.headers)
        # 应该返回403（权限不足）或404（用户不存在）
        assert response.status_code in [403, 404]
        
        logger.info("✅ 删除不存在用户的错误处理正确")

    # ==================== 登录日志查看测试 ====================
    
    def test_15_get_user_login_logs_success(self):
        """测试获取用户登录日志（成功）"""
        user_id = self.test_user['user_id']
        response = self.client.get(f"/api/users/{user_id}/login-logs", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证响应结构
        assert "items" in data
        assert "pagination" in data
        
        # 验证分页信息
        self.api_test.assert_pagination_response(data, min_items=1)  # 至少有登录记录
        
        # 验证登录日志结构
        if data["items"]:
            log = data["items"][0]
            assert "id" in log
            assert "user_id" in log
            assert "login_type" in log
            assert "ip_address" in log
            assert "user_agent" in log
            assert "is_success" in log
            assert "created_at" in log
        
        logger.info("✅ 用户登录日志获取成功")

    def test_16_get_other_user_login_logs_forbidden(self):
        """测试获取其他用户登录日志被禁止"""
        fake_user_id = str(uuid4())
        response = self.client.get(f"/api/users/{fake_user_id}/login-logs", headers=self.headers)
        # 普通用户只能查看自己的登录日志，应该返回403
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 获取其他用户登录日志的权限限制正确")

    # ==================== 微信绑定信息测试 ====================
    
    def test_17_get_user_wechat_binding_no_binding(self):
        """测试获取用户微信绑定信息（无绑定）"""
        user_id = self.test_user['user_id']
        response = self.client.get(f"/api/users/{user_id}/wechat-binding", headers=self.headers)
        
        # 可能返回404（无绑定）或200（空数据）
        if response.status_code == 404:
            self.api_test.assert_api_error(response, 404)
        else:
            data = self.api_test.assert_api_success(response, 200)
            # 如果返回200，应该是空数据或表明无绑定
            assert data is None or data == {}
        
        logger.info("✅ 无微信绑定的情况处理正确")

    def test_18_get_other_user_wechat_binding_forbidden(self):
        """测试获取其他用户微信绑定信息被禁止"""
        fake_user_id = str(uuid4())
        response = self.client.get(f"/api/users/{fake_user_id}/wechat-binding", headers=self.headers)
        # 普通用户只能查看自己的微信绑定，应该返回403
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 获取其他用户微信绑定的权限限制正确")

    # ==================== 用户统计数据测试 ====================
    
    def test_19_get_users_statistics_forbidden(self):
        """测试普通用户无法获取用户统计数据"""
        response = self.client.get("/api/users/statistics/overview", headers=self.headers)
        # 普通用户无法查看统计数据，应该返回403
        self.api_test.assert_api_error(response, 403)
        
        logger.info("✅ 普通用户查看统计数据的权限限制正确")

    # ==================== 认证和权限验证测试 ====================
    
    def test_20_users_api_requires_authentication(self):
        """测试用户API需要认证"""
        # 不带认证头的请求
        response = self.client.get("/api/users/")
        self.api_test.assert_api_error(response, 401)
        
        logger.info("✅ 用户API认证要求正确")

    def test_21_users_api_invalid_token(self):
        """测试无效token访问用户API"""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        response = self.client.get("/api/users/", headers=invalid_headers)
        self.api_test.assert_api_error(response, 401)
        
        logger.info("✅ 无效token错误处理正确")

    # ==================== 边界条件和异常处理测试 ====================
    
    def test_22_get_users_list_invalid_page(self):
        """测试无效页码参数"""
        response = self.client.get(
            "/api/users/",
            params={"page": 0},  # 页码应该从1开始
            headers=self.headers
        )
        # 可能返回400或默认处理为第1页
        if response.status_code == 400:
            self.api_test.assert_api_error(response, 400)
        else:
            data = self.api_test.assert_api_success(response, 200)
            # 如果默认处理，应该返回第1页数据
            assert data["pagination"]["current_page"] >= 1
        
        logger.info("✅ 无效页码参数处理正确")

    def test_23_get_users_list_large_page_size(self):
        """测试过大的页面大小参数"""
        response = self.client.get(
            "/api/users/",
            params={"page_size": 1000},  # 超过最大限制
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 页面大小应该被限制在合理范围内（通常最大100）
        assert data["pagination"]["page_size"] <= 100
        
        logger.info("✅ 页面大小限制处理正确")

    def test_24_users_api_response_time(self):
        """测试用户API响应时间"""
        start_time = time.time()
        response = self.client.get("/api/users/", headers=self.headers)
        end_time = time.time()
        
        # 验证响应成功
        self.api_test.assert_api_success(response, 200)
        
        # 验证响应时间在合理范围内（应该小于2秒）
        response_time = end_time - start_time
        assert response_time < 2.0, f"响应时间过长: {response_time:.2f}秒"
        
        logger.info(f"✅ 用户API响应时间测试通过: {response_time:.3f}秒")

    def test_25_users_data_consistency(self):
        """测试用户数据一致性"""
        # 获取用户列表
        list_response = self.client.get("/api/users/", headers=self.headers)
        list_data = self.api_test.assert_api_success(list_response, 200)
        
        if list_data["items"]:
            # 获取第一个用户的详情
            first_user = list_data["items"][0]
            detail_response = self.client.get(f"/api/users/{first_user['id']}", headers=self.headers)
            detail_data = self.api_test.assert_api_success(detail_response, 200)
            
            # 验证列表和详情中的基本信息一致
            assert first_user["id"] == detail_data["id"]
            assert first_user["username"] == detail_data["username"]
            assert first_user["email"] == detail_data["email"]
            assert first_user["is_active"] == detail_data["is_active"]
        
        logger.info("✅ 用户数据一致性验证通过")


if __name__ == "__main__":
    pytest.main([__file__]) 