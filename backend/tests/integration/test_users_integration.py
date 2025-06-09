"""
用户管理功能集成测试

使用真实HTTP请求测试用户管理功能的端到端功能。
需要手动启动服务器：python start.py dev

覆盖范围：
- 端到端用户管理流程测试
- 复杂权限场景验证
- 网络层协议验证
- 真实管理员操作模拟
- 安全性和权限验证
- 数据完整性检查
"""

import pytest
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from uuid import uuid4

from tests.base_test import RequestsTestClient, BaseAPITest

logger = logging.getLogger(__name__)


class UsersIntegrationTestDataGenerator:
    """用户管理集成测试数据生成器"""
    
    @staticmethod
    def generate_test_users(count: int = 5) -> List[Dict[str, Any]]:
        """生成多个测试用户"""
        users = []
        for i in range(count):
            unique_id = int(time.time() * 1000000) % 1000000 + i
            user = {
                "username": f"integration_user_{unique_id}",
                "email": f"integration{unique_id}@example.com",
                "password": "IntegrationTest123456",
                "nickname": f"集成测试用户{i+1}"
            }
            users.append(user)
        return users
    
    @staticmethod
    def generate_admin_user() -> Dict[str, Any]:
        """生成测试管理员用户"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "username": f"integration_admin_{unique_id}",
            "email": f"admin_integration{unique_id}@example.com",
            "password": "AdminIntegration123456",
            "nickname": f"集成测试管理员"
        }


@pytest.mark.integration
@pytest.mark.requires_server
class TestUsersIntegration:
    """用户管理集成测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.client = RequestsTestClient()
        cls.api_test = BaseAPITest(cls.client)
        cls._check_server_availability()
        
        # 创建普通测试用户
        cls.test_user_data = cls.api_test.setup_test_user()
        cls.user_headers = {"Authorization": f"Bearer {cls.test_user_data['token']}"}
        
        # 创建多个额外测试用户
        cls.additional_users = []
        test_users = UsersIntegrationTestDataGenerator.generate_test_users(3)
        for user_data in test_users:
            register_response = cls.client.post("/api/auth/register", json=user_data)
            if register_response.status_code in [200, 201]:
                login_response = cls.client.post("/api/auth/login/username", json={
                    "username": user_data["username"],
                    "password": user_data["password"]
                })
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    user_info = {
                        "user_data": user_data,
                        "token": login_result["data"]["access_token"],
                        "user_id": login_result["data"]["user"]["id"]
                    }
                    cls.additional_users.append(user_info)
        
        logger.info(f"✅ 用户管理集成测试环境设置完成: 主用户 + {len(cls.additional_users)}个额外用户")

    @classmethod
    def _check_server_availability(cls):
        """检查服务器是否可用"""
        try:
            response = cls.client.get("/health")
            if response.status_code == 200:
                logger.info("✅ 服务器连接正常")
            else:
                pytest.skip(f"服务器不可用，状态码: {response.status_code}")
        except Exception as e:
            pytest.skip(f"无法连接服务器，请确保服务器已启动 (python start.py dev): {str(e)}")

    # ==================== 端到端测试 ====================
    
    def test_01_complete_user_management_workflow(self):
        """测试完整的用户管理工作流程"""
        # 1. 获取用户列表
        list_response = self.client.get("/api/users/", headers=self.user_headers)
        list_data = self.api_test.assert_api_success(list_response, 200)
        
        # 验证分页响应结构
        assert "items" in list_data
        assert "pagination" in list_data
        self.api_test.assert_pagination_response(list_data, min_items=1)
        
        # 2. 获取用户详情
        user_id = self.test_user_data['user_id']
        detail_response = self.client.get(f"/api/users/{user_id}", headers=self.user_headers)
        detail_data = self.api_test.assert_api_success(detail_response, 200)
        
        # 验证详情数据完整性
        assert detail_data["id"] == user_id
        assert "username" in detail_data
        assert "email" in detail_data
        assert "is_active" in detail_data
        
        # 3. 获取用户登录日志
        logs_response = self.client.get(f"/api/users/{user_id}/login-logs", headers=self.user_headers)
        logs_data = self.api_test.assert_api_success(logs_response, 200)
        
        # 验证登录日志结构
        assert "items" in logs_data
        assert "pagination" in logs_data
        self.api_test.assert_pagination_response(logs_data, min_items=1)
        
        logger.info("✅ 完整用户管理工作流程测试成功")

    def test_02_user_permission_enforcement(self):
        """测试用户权限强制执行"""
        if self.additional_users:
            target_user = self.additional_users[0]
            target_user_id = target_user['user_id']
            
            # 1. 普通用户尝试修改其他用户状态（应该被拒绝）
            status_response = self.client.put(
                f"/api/users/{target_user_id}/status",
                json={"is_active": False},
                headers=self.user_headers
            )
            self.api_test.assert_api_error(status_response, 403)
            
            # 2. 普通用户尝试设置管理员权限（应该被拒绝）
            admin_response = self.client.put(
                f"/api/users/{target_user_id}/admin",
                json={"is_admin": True},
                headers=self.user_headers
            )
            self.api_test.assert_api_error(admin_response, 403)
        
        logger.info("✅ 用户权限强制执行测试成功")

    def test_03_user_search_and_filtering(self):
        """测试用户搜索和筛选功能"""
        # 1. 测试关键词搜索
        if self.additional_users:
            search_user = self.additional_users[0]
            search_keyword = search_user['user_data']['username'][:10]
            
            search_response = self.client.get(
                "/api/users/",
                params={"keyword": search_keyword},
                headers=self.user_headers
            )
            search_data = self.api_test.assert_api_success(search_response, 200)
            
            # 验证搜索结果
            assert "items" in search_data
        
        # 2. 测试分页功能
        page1_response = self.client.get(
            "/api/users/",
            params={"page": 1, "page_size": 3},
            headers=self.user_headers
        )
        page1_data = self.api_test.assert_api_success(page1_response, 200)
        
        assert page1_data["pagination"]["current_page"] == 1
        assert page1_data["pagination"]["page_size"] == 3
        
        logger.info("✅ 用户搜索和筛选功能测试成功")

    def test_04_authentication_flow_integrity(self):
        """测试认证流程完整性"""
        # 1. 无认证访问（应该被拒绝）
        no_auth_response = self.client.get("/api/users/")
        assert no_auth_response.status_code == 401
        
        # 2. 有效token访问（应该成功）
        valid_response = self.client.get("/api/users/", headers=self.user_headers)
        self.api_test.assert_api_success(valid_response, 200)
        
        logger.info("✅ 认证流程完整性验证成功")

    def test_05_error_handling_consistency(self):
        """测试错误处理一致性"""
        # 1. 不存在的用户ID
        fake_id = str(uuid4())
        not_found_response = self.client.get(f"/api/users/{fake_id}", headers=self.user_headers)
        assert not_found_response.status_code == 404
        
        error_data = not_found_response.json()
        assert "success" in error_data
        assert error_data["success"] == False
        assert "message" in error_data
        
        logger.info("✅ 错误处理一致性验证成功")

    def test_06_concurrent_user_operations(self):
        """测试并发用户操作"""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def get_user_list():
            try:
                response = self.client.get("/api/users/", headers=self.user_headers)
                result_queue.put({"success": response.status_code == 200})
            except Exception as e:
                result_queue.put({"success": False, "error": str(e)})
        
        # 启动5个并发请求
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_user_list)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        success_count = sum(1 for r in results if r["success"])
        success_rate = success_count / len(results)
        
        # 至少90%的请求应该成功
        assert success_rate >= 0.9, f"并发成功率 {success_rate:.2%} 低于预期"
        
        logger.info(f"✅ 并发用户操作测试成功: {success_count}/{len(results)} 请求成功")


if __name__ == "__main__":
    pytest.main([__file__]) 