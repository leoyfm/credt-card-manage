"""
用户管理功能性能测试

基于FastAPI TestClient的性能测试，验证用户管理功能相关操作的性能表现。
包括响应时间、并发性能、资源使用等指标的测试。
"""

import pytest
import logging
import time
import statistics
import threading
import queue

from tests.base_test import FastAPITestClient, BaseAPITest

logger = logging.getLogger(__name__)


@pytest.mark.performance
class TestUsersPerformance:
    """用户管理性能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        logger.info(f"✅ 用户管理性能测试环境设置完成")

    def _measure_response_time(self, operation, max_time: float = 5.0) -> float:
        """测量单次操作响应时间"""
        start_time = time.time()
        operation()
        response_time = time.time() - start_time
        
        assert response_time < max_time, f"响应时间 {response_time:.3f}s 超过预期 {max_time}s"
        return response_time

    def _measure_multiple_requests(self, operation, count: int = 5, max_avg_time: float = 2.0) -> dict:
        """测量多次请求的性能指标"""
        response_times = []
        
        for _ in range(count):
            start_time = time.time()
            operation()
            response_time = time.time() - start_time
            response_times.append(response_time)
        
        metrics = {
            "count": count,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times)
        }
        
        assert metrics["avg_response_time"] < max_avg_time, f"平均响应时间 {metrics['avg_response_time']:.3f}s 超过预期 {max_avg_time}s"
        
        return metrics

    def _test_concurrent_performance(self, operation, concurrent_count: int = 3, success_rate: float = 0.9) -> dict:
        """测试并发性能"""
        result_queue = queue.Queue()
        
        def worker():
            try:
                start_time = time.time()
                operation()
                response_time = time.time() - start_time
                result_queue.put({"success": True, "response_time": response_time})
            except Exception as e:
                result_queue.put({"success": False, "error": str(e)})
        
        # 启动并发线程
        threads = []
        start_time = time.time()
        
        for _ in range(concurrent_count):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 收集结果
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        success_count = sum(1 for r in results if r["success"])
        actual_success_rate = success_count / len(results)
        response_times = [r["response_time"] for r in results if r["success"]]
        
        metrics = {
            "concurrent_count": concurrent_count,
            "success_count": success_count,
            "success_rate": actual_success_rate,
            "total_time": total_time,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "throughput": success_count / total_time if total_time > 0 else 0
        }
        
        assert actual_success_rate >= success_rate, f"成功率 {actual_success_rate:.2%} 低于预期 {success_rate:.2%}"
        
        return metrics

    # ==================== 单次操作性能测试 ====================
    
    def test_01_user_list_performance(self):
        """测试用户列表查询性能"""
        def get_user_list():
            response = self.client.get("/api/users/", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_user_list, max_time=2.0)
        logger.info(f"✅ 用户列表查询性能: {response_time:.3f}秒")

    def test_02_user_detail_performance(self):
        """测试用户详情查询性能"""
        user_id = self.test_user['user_id']
        
        def get_user_detail():
            response = self.client.get(f"/api/users/{user_id}", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_user_detail, max_time=1.0)
        logger.info(f"✅ 用户详情查询性能: {response_time:.3f}秒")

    def test_03_user_search_performance(self):
        """测试用户搜索性能"""
        def search_users():
            response = self.client.get(
                "/api/users/",
                params={"keyword": "test"},
                headers=self.headers
            )
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(search_users, max_time=2.0)
        logger.info(f"✅ 用户搜索性能: {response_time:.3f}秒")

    def test_04_login_logs_performance(self):
        """测试登录日志查询性能"""
        user_id = self.test_user['user_id']
        
        def get_login_logs():
            response = self.client.get(f"/api/users/{user_id}/login-logs", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_login_logs, max_time=1.5)
        logger.info(f"✅ 登录日志查询性能: {response_time:.3f}秒")

    def test_05_user_statistics_performance(self):
        """测试用户统计性能"""
        def get_user_statistics():
            response = self.client.get("/api/users/statistics/overview", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_user_statistics, max_time=3.0)
        logger.info(f"✅ 用户统计查询性能: {response_time:.3f}秒")

    # ==================== 批量操作性能测试 ====================
    
    def test_06_multiple_user_list_requests_performance(self):
        """测试多次用户列表请求性能"""
        def get_user_list():
            response = self.client.get("/api/users/", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._measure_multiple_requests(get_user_list, count=5, max_avg_time=1.5)
        logger.info(f"✅ 多次用户列表请求性能: 平均 {metrics['avg_response_time']:.3f}秒")

    def test_07_paginated_requests_performance(self):
        """测试分页请求性能"""
        def get_paginated_users():
            response = self.client.get(
                "/api/users/",
                params={"page": 1, "page_size": 5},
                headers=self.headers
            )
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._measure_multiple_requests(get_paginated_users, count=3, max_avg_time=1.0)
        logger.info(f"✅ 分页请求性能: 平均 {metrics['avg_response_time']:.3f}秒")

    def test_08_mixed_operations_performance(self):
        """测试混合操作性能"""
        def mixed_operation():
            # 随机执行不同的用户管理操作
            import random
            operation_type = random.choice(['list', 'detail', 'logs'])
            
            if operation_type == 'list':
                response = self.client.get("/api/users/", headers=self.headers)
            elif operation_type == 'detail':
                response = self.client.get(f"/api/users/{self.test_user['user_id']}", headers=self.headers)
            elif operation_type == 'logs':
                response = self.client.get(f"/api/users/{self.test_user['user_id']}/login-logs", headers=self.headers)
            
            # 验证响应成功
            assert response.status_code in [200, 403, 404]
        
        metrics = self._measure_multiple_requests(mixed_operation, count=3, max_avg_time=2.0)
        logger.info(f"✅ 混合操作性能: 平均 {metrics['avg_response_time']:.3f}秒")

    # ==================== 并发性能测试 ====================
    
    def test_09_concurrent_user_list_requests(self):
        """测试并发用户列表请求"""
        def get_user_list():
            response = self.client.get("/api/users/", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._test_concurrent_performance(get_user_list, concurrent_count=3, success_rate=0.9)
        logger.info(f"✅ 并发用户列表请求: 吞吐量 {metrics['throughput']:.2f} req/s, 成功率 {metrics['success_rate']:.2%}")

    def test_10_concurrent_user_detail_requests(self):
        """测试并发用户详情请求"""
        user_id = self.test_user['user_id']
        
        def get_user_detail():
            response = self.client.get(f"/api/users/{user_id}", headers=self.headers)
            assert response.status_code in [200, 403]
        
        metrics = self._test_concurrent_performance(get_user_detail, concurrent_count=3, success_rate=0.8)
        logger.info(f"✅ 并发用户详情请求: 吞吐量 {metrics['throughput']:.2f} req/s, 成功率 {metrics['success_rate']:.2%}")

    def test_11_high_load_user_operations(self):
        """测试高负载用户操作"""
        def heavy_user_load():
            # 模拟重负载场景：复杂搜索和分页
            response = self.client.get(
                "/api/users/",
                params={
                    "keyword": "performance",
                    "page": 1,
                    "page_size": 10,
                    "is_active": True
                },
                headers=self.headers
            )
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._test_concurrent_performance(heavy_user_load, concurrent_count=2, success_rate=0.8)
        logger.info(f"✅ 高负载用户操作: 吞吐量 {metrics['throughput']:.2f} req/s, 平均响应 {metrics['avg_response_time']:.3f}s")

    def test_12_sustained_load_performance(self):
        """测试持续负载性能"""
        def sustained_operation():
            # 持续负载：模拟真实使用场景
            operations = [
                lambda: self.client.get("/api/users/", headers=self.headers),
                lambda: self.client.get(f"/api/users/{self.test_user['user_id']}", headers=self.headers),
                lambda: self.client.get(f"/api/users/{self.test_user['user_id']}/login-logs", headers=self.headers)
            ]
            
            import random
            operation = random.choice(operations)
            response = operation()
            assert response.status_code in [200, 403, 404]
        
        # 持续5秒的负载测试
        start_time = time.time()
        success_count = 0
        total_requests = 0
        
        while time.time() - start_time < 5:  # 5秒持续测试
            try:
                sustained_operation()
                success_count += 1
            except Exception as e:
                logger.warning(f"持续负载测试中的错误: {e}")
            total_requests += 1
            time.sleep(0.2)  # 200ms间隔
        
        duration = time.time() - start_time
        success_rate = success_count / total_requests if total_requests > 0 else 0
        throughput = success_count / duration
        
        assert success_rate >= 0.8, f"持续负载成功率 {success_rate:.2%} 低于预期"
        
        logger.info(f"✅ 持续负载性能: {duration:.1f}s, {total_requests}请求, 成功率 {success_rate:.2%}, 吞吐量 {throughput:.2f} req/s")


if __name__ == "__main__":
    pytest.main([__file__]) 