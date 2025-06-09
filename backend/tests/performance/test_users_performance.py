"""
用户认证接口性能测试

测试用户认证相关接口的性能基准、响应时间测试。
"""

import pytest
import logging
from typing import Dict, Any
from uuid import uuid4
from tests.base_test import FastAPITestClient, BaseAPITest, TestPerformanceMixin

logger = logging.getLogger(__name__)


@pytest.mark.performance
@pytest.mark.slow
class TestUsersPerformance(TestPerformanceMixin):
    """用户认证性能测试基类"""
    
    def setup_method(self):
        """设置测试方法"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        logger.info("用户认证性能测试 - 设置完成")
    
    def test_01_user_registration_performance(self):
        """测试用户注册接口性能"""
        def register_user():
            unique_id = uuid4().hex[:8]
            register_data = {
                "username": f"perfuser_{unique_id}",
                "email": f"perfuser_{unique_id}@example.com",
                "password": "TestPass123456",
                "nickname": "性能测试用户"
            }
            
            response = self.client.post("/api/auth/register", json=register_data)
            return response
        
        # 单次性能测试
        self.measure_response_time(register_user, max_time=2.0)
        
        # 批量性能测试
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: register_user(), count=10, max_avg_time=1.5
        )
        
        logger.info(f"用户注册性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_02_user_login_performance(self):
        """测试用户登录接口性能"""
        def login_user():
            login_data = {
                "username": self.test_user["user"]["username"],
                "password": self.test_user["user"]["password"]
            }
            
            response = self.client.post("/api/auth/login/username", json=login_data)
            return response
        
        # 单次性能测试
        self.measure_response_time(login_user, max_time=1.5)
        
        # 批量性能测试
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: login_user(), count=20, max_avg_time=1.0
        )
        
        logger.info(f"用户登录性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_03_profile_query_performance(self):
        """测试用户资料查询性能"""
        def query_profile():
            response = self.client.get("/api/auth/profile", headers=self.test_user["headers"])
            return response
        
        # 单次性能测试
        self.measure_response_time(query_profile, max_time=0.8)
        
        # 批量性能测试
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: query_profile(), count=30, max_avg_time=0.5
        )
        
        logger.info(f"用户资料查询性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_04_profile_update_performance(self):
        """测试用户资料更新性能"""
        def update_profile():
            unique_suffix = uuid4().hex[:6]
            update_data = {
                "nickname": f"性能测试用户_{unique_suffix}",
                "bio": f"这是性能测试的个人简介 {unique_suffix}",
                "gender": "male"
            }
            
            response = self.client.put("/api/auth/profile", json=update_data, headers=self.test_user["headers"])
            return response
        
        # 单次性能测试
        self.measure_response_time(update_profile, max_time=1.5)
        
        # 批量性能测试
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: update_profile(), count=15, max_avg_time=1.0
        )
        
        logger.info(f"用户资料更新性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_05_password_change_performance(self):
        """测试密码修改性能"""
        def change_password():
            # 为每次测试创建新用户，避免密码冲突
            test_user = self.api_test.setup_test_user()
            
            # 修改密码
            change_data = {
                "old_password": test_user["user"]["password"],
                "new_password": f"NewPass{uuid4().hex[:8]}"
            }
            
            response = self.client.post("/api/auth/password/change", json=change_data, headers=test_user["headers"])
            return response
        
        # 单次性能测试
        self.measure_response_time(change_password, max_time=2.0)
        
        # 批量性能测试 - 减少数量避免过多用户创建
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: change_password(), count=5, max_avg_time=1.5
        )
        
        logger.info(f"密码修改性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_06_auth_status_check_performance(self):
        """测试认证状态检查性能"""
        def check_auth_status():
            response = self.client.get("/api/auth/status", headers=self.test_user["headers"])
            return response
        
        # 单次性能测试
        self.measure_response_time(check_auth_status, max_time=0.5)
        
        # 批量性能测试
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: check_auth_status(), count=50, max_avg_time=0.3
        )
        
        logger.info(f"认证状态检查性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_07_logout_performance(self):
        """测试登出操作性能"""
        def logout_operation():
            # 为每次测试创建新用户和会话
            test_user = self.api_test.setup_test_user()
            
            # 登出
            logout_data = {"all_devices": False}
            response = self.client.post("/api/auth/logout", json=logout_data, headers=test_user["headers"])
            return response
        
        # 单次性能测试
        self.measure_response_time(logout_operation, max_time=1.0)
        
        # 批量性能测试
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: logout_operation(), count=10, max_avg_time=0.8
        )
        
        logger.info(f"登出操作性能测试完成 - 平均响应时间: {avg_time:.3f}s")
    
    def test_08_stress_test_user_registration(self):
        """用户注册压力测试"""
        def stress_register():
            unique_id = uuid4().hex[:8]
            register_data = {
                "username": f"stress_{unique_id}",
                "email": f"stress_{unique_id}@example.com",
                "password": "StressTest123456",
                "nickname": "压力测试用户"
            }
            
            response = self.client.post("/api/auth/register", json=register_data)
            return response
        
        logger.info("开始用户注册压力测试...")
        
        # 压力测试 - 大量注册请求
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: stress_register(), count=50, max_avg_time=3.0
        )
        
        logger.info(f"用户注册压力测试完成 - 50个请求，平均响应时间: {avg_time:.3f}s")
    
    def test_09_memory_stability_test(self):
        """内存稳定性测试"""
        def memory_test_operation():
            # 创建用户、登录、查询资料、更新资料、登出的完整流程
            unique_id = uuid4().hex[:8]
            
            # 1. 注册用户
            register_data = {
                "username": f"memory_{unique_id}",
                "email": f"memory_{unique_id}@example.com",
                "password": "MemoryTest123456",
                "nickname": "内存测试用户"
            }
            response = self.client.post("/api/auth/register", json=register_data)
            if response.status_code != 200:
                return response
            
            # 2. 登录
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            response = self.client.post("/api/auth/login/username", json=login_data)
            if response.status_code != 200:
                return response
            
            result = response.json()
            if not result.get("success"):
                return response
            
            headers = {"Authorization": f"Bearer {result['data']['access_token']}"}
            
            # 3. 查询资料
            response = self.client.get("/api/auth/profile", headers=headers)
            if response.status_code != 200:
                return response
            
            # 4. 更新资料
            update_data = {
                "nickname": f"更新的内存测试用户_{unique_id[:4]}",
                "bio": "内存稳定性测试"
            }
            response = self.client.put("/api/auth/profile", json=update_data, headers=headers)
            if response.status_code != 200:
                return response
            
            # 5. 登出
            logout_data = {"all_devices": False}
            response = self.client.post("/api/auth/logout", json=logout_data, headers=headers)
            return response
        
        logger.info("开始内存稳定性测试...")
        
        # 执行完整操作流程
        total_time, avg_time = self._measure_batch_operations_performance(
            lambda i: memory_test_operation(), count=20, max_avg_time=4.0
        )
        
        logger.info(f"内存稳定性测试完成 - 20个完整流程，平均时间: {avg_time:.3f}s")
    
    def test_10_performance_consistency_test(self):
        """性能一致性测试"""
        def consistency_test():
            login_data = {
                "username": self.test_user["user"]["username"],
                "password": self.test_user["user"]["password"]
            }
            
            response = self.client.post("/api/auth/login/username", json=login_data)
            return response
        
        logger.info("开始性能一致性测试...")
        
        # 多轮测试检查性能一致性
        round_times = []
        
        for round_num in range(3):
            total_time, avg_time = self._measure_batch_operations_performance(
                lambda i: consistency_test(), count=10, max_avg_time=1.2
            )
            round_times.append(avg_time)
            logger.info(f"第{round_num + 1}轮平均响应时间: {avg_time:.3f}s")
        
        # 检查性能一致性
        max_time = max(round_times)
        min_time = min(round_times)
        time_variance = max_time - min_time
        
        # 性能波动不应超过50%
        variance_ratio = time_variance / min_time if min_time > 0 else 0
        assert variance_ratio <= 0.5, f"性能波动过大: {variance_ratio:.1%} (最大:{max_time:.3f}s, 最小:{min_time:.3f}s)"
        
        avg_all_rounds = sum(round_times) / len(round_times)
        assert avg_all_rounds < 1.2, f"整体平均性能不达标: {avg_all_rounds:.3f}s"
        
        logger.info(f"性能一致性测试完成 - 3轮测试，性能波动: {variance_ratio:.1%}") 