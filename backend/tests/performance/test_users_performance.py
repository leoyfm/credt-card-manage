"""
用户认证接口性能测试

测试用户认证相关接口的性能基准、响应时间测试。
"""

import pytest
import logging
from typing import Dict, Any, List
import uuid
import time
import threading

from tests.base_test import FastAPITestClient, BaseAPITest, TestPerformanceMixin

logger = logging.getLogger(__name__)


@pytest.mark.performance
@pytest.mark.slow
class TestUsersPerformance(TestPerformanceMixin):
    """用户认证性能测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        logger.info("用户认证性能测试 - 设置完成")
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        pass
    
    def test_01_user_registration_performance(self):
        """测试用户注册性能"""
        def register_user():
            """单次用户注册操作"""
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "username": f"perfuser_{unique_id}",
                "email": f"perfuser_{unique_id}@example.com",
                "password": "TestPassword123",
                "phone": None,
                "display_name": f"性能测试用户{unique_id}"
            }
            
            response = self.client.post("/api/auth/register", json=user_data)
            return response.status_code == 200
        
        # 测试单次注册性能
        metrics = self.measure_response_time(register_user, max_time=2.0, description="用户注册")
        assert metrics["success"], "用户注册操作应在2秒内完成"
        
        # 测试批量注册性能
        def batch_register():
            for i in range(5):
                register_user()
        
        metrics = self.measure_batch_operations_performance(
            batch_register,
            count=5,
            max_avg_time=0.4,
            description="批量用户注册"
        )
        
        assert metrics["success"], "批量注册平均时间应符合要求"
        print(f"📊 用户注册性能：批量注册5个用户，平均{metrics['avg_response_time']:.3f}秒/用户")
    
    def test_02_user_login_performance(self):
        """测试用户登录性能"""
        def login_user():
            """单次用户登录操作"""
            login_data = {
                "username": self.test_user["user"]["username"],
                "password": "TestPassword123"
            }
            
            response = self.client.post("/api/auth/login/username", json=login_data)
            return response.status_code == 200
        
        # 测试单次登录性能
        metrics = self.measure_response_time(login_user, max_time=1.0, description="用户登录")
        assert metrics["success"], "用户登录操作应在1秒内完成"
        
        # 测试批量登录性能
        def batch_login():
            for i in range(10):
                login_user()
        
        metrics = self.measure_batch_operations_performance(
            batch_login,
            count=10,
            max_avg_time=0.2,
            description="批量用户登录"
        )
        
        assert metrics["success"], "批量登录平均时间应符合要求"
        print(f"📊 用户登录性能：批量登录10次，平均{metrics['avg_response_time']:.3f}秒/次")
    
    def test_03_profile_query_performance(self):
        """测试用户资料查询性能"""
        def query_profile():
            """单次资料查询操作"""
            response = self.client.get("/api/auth/profile", headers=self.headers)
            return response.status_code == 200
        
        # 测试单次查询性能
        metrics = self.measure_response_time(query_profile, max_time=0.5, description="用户资料查询")
        assert metrics["success"], "用户资料查询应在0.5秒内完成"
        
        # 测试批量查询性能
        def batch_query():
            for i in range(20):
                query_profile()
        
        metrics = self.measure_batch_operations_performance(
            batch_query,
            count=20,
            max_avg_time=0.05,
            description="批量用户资料查询"
        )
        
        assert metrics["success"], "批量查询平均时间应符合要求"
        print(f"📊 用户资料查询性能：批量查询20次，平均{metrics['avg_response_time']:.3f}秒/次")
    
    def test_04_profile_update_performance(self):
        """测试用户资料更新性能"""
        def update_profile():
            """单次资料更新操作"""
            update_data = {
                "display_name": f"更新测试用户{time.time():.0f}",
                "phone": "13800138000"
            }
            
            response = self.client.put("/api/auth/profile", json=update_data, headers=self.headers)
            return response.status_code == 200
        
        # 测试单次更新性能
        metrics = self.measure_response_time(update_profile, max_time=1.0, description="用户资料更新")
        assert metrics["success"], "用户资料更新应在1秒内完成"
        
        # 测试批量更新性能
        def batch_update():
            for i in range(5):
                update_profile()
        
        metrics = self.measure_batch_operations_performance(
            batch_update,
            count=5,
            max_avg_time=0.3,
            description="批量用户资料更新"
        )
        
        assert metrics["success"], "批量更新平均时间应符合要求"
        print(f"📊 用户资料更新性能：批量更新5次，平均{metrics['avg_response_time']:.3f}秒/次")
    
    def test_05_password_change_performance(self):
        """测试密码修改性能"""
        # 先创建一个新用户用于密码修改测试
        new_user = self.api_test.setup_test_user()
        new_headers = {"Authorization": f"Bearer {new_user['token']}"}
        
        def change_password():
            """单次密码修改操作"""
            password_data = {
                "old_password": "TestPassword123",
                "new_password": "NewTestPassword123"
            }
            
            response = self.client.post("/api/auth/password/change", json=password_data, headers=new_headers)
            return response.status_code == 200
        
        # 测试单次密码修改性能
        metrics = self.measure_response_time(change_password, max_time=2.0, description="密码修改")
        assert metrics["success"], "密码修改操作应在2秒内完成"
        
        # 测试批量密码修改性能（创建多个用户）
        def batch_password_change():
            users_created = 0
            for i in range(3):
                try:
                    test_user = self.api_test.setup_test_user()
                    test_headers = {"Authorization": f"Bearer {test_user['token']}"}
                    
                    password_data = {
                        "old_password": "TestPassword123",
                        "new_password": f"NewPassword{i}123"
                    }
                    
                    response = self.client.post("/api/auth/password/change", json=password_data, headers=test_headers)
                    if response.status_code == 200:
                        users_created += 1
                except Exception:
                    pass
            return users_created >= 2  # 至少2个成功
        
        metrics = self.measure_batch_operations_performance(
            batch_password_change,
            count=3,
            max_avg_time=3.0,
            description="批量密码修改"
        )
        
        assert metrics["success"], "批量密码修改平均时间应符合要求"
        print(f"📊 密码修改性能：批量修改3次，平均{metrics['avg_response_time']:.3f}秒/次")
    
    def test_06_auth_status_check_performance(self):
        """测试认证状态检查性能"""
        def check_auth_status():
            """单次认证状态检查操作"""
            response = self.client.get("/api/auth/status", headers=self.headers)
            return response.status_code == 200
        
        # 测试单次状态检查性能
        metrics = self.measure_response_time(check_auth_status, max_time=0.2, description="认证状态检查")
        assert metrics["success"], "认证状态检查应在0.2秒内完成"
        
        # 测试批量状态检查性能
        def batch_status_check():
            for i in range(30):
                check_auth_status()
        
        metrics = self.measure_batch_operations_performance(
            batch_status_check,
            count=30,
            max_avg_time=0.03,
            description="批量认证状态检查"
        )
        
        assert metrics["success"], "批量状态检查平均时间应符合要求"
        print(f"📊 认证状态检查性能：批量检查30次，平均{metrics['avg_response_time']:.3f}秒/次")
    
    def test_07_logout_performance(self):
        """测试用户登出性能"""
        # 先创建一个新用户用于登出测试
        new_user = self.api_test.setup_test_user()
        new_headers = {"Authorization": f"Bearer {new_user['token']}"}
        
        def logout_user():
            """单次用户登出操作"""
            response = self.client.post("/api/auth/logout", headers=new_headers)
            return response.status_code == 200
        
        # 测试单次登出性能
        metrics = self.measure_response_time(logout_user, max_time=1.0, description="用户登出")
        assert metrics["success"], "用户登出操作应在1秒内完成"
        
        # 测试批量登出性能（创建多个用户）
        def batch_logout():
            users_logged_out = 0
            for i in range(5):
                try:
                    test_user = self.api_test.setup_test_user()
                    test_headers = {"Authorization": f"Bearer {test_user['token']}"}
                    
                    response = self.client.post("/api/auth/logout", headers=test_headers)
                    if response.status_code == 200:
                        users_logged_out += 1
                except Exception:
                    pass
            return users_logged_out >= 3  # 至少3个成功
        
        metrics = self.measure_batch_operations_performance(
            batch_logout,
            count=5,
            max_avg_time=1.0,
            description="批量用户登出"
        )
        
        assert metrics["success"], "批量登出平均时间应符合要求"
        print(f"📊 用户登出性能：批量登出5次，平均{metrics['avg_response_time']:.3f}秒/次")
    
    def test_08_stress_test_user_registration(self):
        """用户注册压力测试"""
        logger.info("开始用户注册压力测试...")
        
        def stress_register():
            """压力测试用户注册"""
            success_count = 0
            for i in range(20):
                try:
                    unique_id = str(uuid.uuid4())[:8]
                    user_data = {
                        "username": f"stress_{unique_id}",
                        "email": f"stress_{unique_id}@example.com", 
                        "password": "StressTest123",
                        "display_name": f"压力测试用户{i}"
                    }
                    
                    response = self.client.post("/api/auth/register", json=user_data)
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            
            return success_count >= 15  # 至少75%成功率
        
        metrics = self.measure_batch_operations_performance(
            stress_register,
            count=20,
            max_avg_time=8.0,
            description="用户注册压力测试"
        )
        
        assert metrics["success"], "压力测试应在合理时间内完成"
        print(f"📊 用户注册压力测试：20次批量注册，平均{metrics['avg_response_time']:.3f}秒")
    
    def test_09_memory_stability_test(self):
        """内存稳定性测试"""
        logger.info("开始内存稳定性测试...")
        
        def memory_stability():
            """内存稳定性测试"""
            operations_completed = 0
            
            # 执行多种操作的混合测试
            for i in range(50):
                try:
                    # 轮换执行不同操作
                    if i % 4 == 0:
                        # 注册用户
                        unique_id = str(uuid.uuid4())[:8]
                        user_data = {
                            "username": f"mem_{unique_id}",
                            "email": f"mem_{unique_id}@example.com",
                            "password": "MemTest123"
                        }
                        response = self.client.post("/api/auth/register", json=user_data)
                    elif i % 4 == 1:
                        # 用户登录
                        login_data = {
                            "username": self.test_user["user"]["username"],
                            "password": "TestPassword123"
                        }
                        response = self.client.post("/api/auth/login/username", json=login_data)
                    elif i % 4 == 2:
                        # 查询用户资料
                        response = self.client.get("/api/auth/profile", headers=self.headers)
                    else:
                        # 检查认证状态
                        response = self.client.get("/api/auth/status", headers=self.headers)
                    
                    if response.status_code == 200:
                        operations_completed += 1
                        
                except Exception:
                    pass
            
            return operations_completed >= 35  # 至少70%成功率
        
        metrics = self.measure_batch_operations_performance(
            memory_stability,
            count=50,
            max_avg_time=15.0,
            description="内存稳定性测试"
        )
        
        assert metrics["success"], "内存稳定性测试应成功完成"
        print(f"📊 内存稳定性测试：50次混合操作，平均{metrics['avg_response_time']:.3f}秒")
    
    def test_10_performance_consistency_test(self):
        """性能一致性测试"""
        logger.info("开始性能一致性测试...")
        
        def consistency_test():
            """性能一致性测试"""
            # 连续执行相同操作，检查性能一致性
            response_times = []
            
            for i in range(20):
                start_time = time.time()
                response = self.client.get("/api/auth/profile", headers=self.headers)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if len(response_times) >= 15:
                # 计算性能一致性
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                # 检查最大响应时间与最小响应时间的比值
                consistency_ratio = max_time / min_time if min_time > 0 else 999
                
                return consistency_ratio < 10  # 最大响应时间不应超过最小响应时间的10倍
            
            return False
        
        metrics = self.measure_batch_operations_performance(
            consistency_test,
            count=20,
            max_avg_time=5.0,
            description="性能一致性测试"
        )
        
        assert metrics["success"], "性能一致性测试应符合要求"
        print(f"📊 性能一致性测试：20次连续操作，平均{metrics['avg_response_time']:.3f}秒") 