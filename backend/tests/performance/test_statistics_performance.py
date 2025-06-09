"""
统计功能性能测试

基于FastAPI TestClient的性能测试，验证统计功能相关操作的性能表现。
包括响应时间、并发性能、资源使用等指标的测试。
"""

import pytest
import logging
import time
import statistics
import threading
import queue
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from tests.base_test import FastAPITestClient, BaseAPITest

logger = logging.getLogger(__name__)


class StatisticsPerformanceDataGenerator:
    """统计性能测试数据生成器"""
    
    @staticmethod
    def generate_performance_card_data() -> dict:
        """生成性能测试用信用卡数据"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "card_name": f"性能测试卡{unique_id}",
            "bank_name": f"性能测试银行{unique_id % 5}",  # 5个不同银行
            "card_number": f"644{unique_id:010d}9876",
            "expiry_month": 10,
            "expiry_year": 2029,
            "credit_limit": "100000.00",
            "status": "active"
        }
    
    @staticmethod
    def generate_bulk_transaction_data(card_ids: list, count: int) -> list:
        """生成大量交易数据"""
        transactions = []
        categories = ["dining", "shopping", "transport", "entertainment", "medical", "education", "travel", "other"]
        transaction_types = ["expense", "payment", "refund", "transfer"]
        
        import random
        for i in range(count):
            card_id = random.choice(card_ids)
            unique_id = int(time.time() * 1000000) % 1000000 + i
            
            # 生成随机日期（最近12个月）
            days_ago = random.randint(0, 365)
            transaction_date = datetime.now() - timedelta(days=days_ago)
            
            transaction = {
                "card_id": card_id,
                "transaction_type": random.choice(transaction_types),
                "amount": f"{random.randint(50, 5000)}.{random.randint(0, 99):02d}",
                "transaction_date": transaction_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "merchant_name": f"性能测试商户{unique_id}",
                "category": random.choice(categories),
                "description": f"性能测试交易{i+1}"
            }
            transactions.append(transaction)
        
        return transactions


@pytest.mark.performance
class TestStatisticsPerformance:
    """统计功能性能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        # 创建多张测试信用卡
        self.test_cards = []
        for i in range(5):
            card_data = StatisticsPerformanceDataGenerator.generate_performance_card_data()
            card = self.api_test.create_test_card(card_data)
            self.test_cards.append(card)
        
        self.card_ids = [card["id"] for card in self.test_cards]
        
        # 创建大量测试交易数据
        self.test_transactions = []
        bulk_transactions = StatisticsPerformanceDataGenerator.generate_bulk_transaction_data(self.card_ids, 50)
        
        for tx_data in bulk_transactions:
            response = self.client.post("/api/transactions", json=tx_data, headers=self.headers)
            if response.status_code == 201:
                transaction_data = self.api_test.assert_api_success(response, 201)
                self.test_transactions.append(transaction_data)
        
        logger.info(f"✅ 统计性能测试环境设置完成: {len(self.test_cards)}张卡片, {len(self.test_transactions)}笔交易")

    def _measure_response_time(self, operation, max_time: float = 5.0) -> float:
        """测量单次操作响应时间"""
        start_time = time.time()
        operation()
        response_time = time.time() - start_time
        
        assert response_time < max_time, f"响应时间 {response_time:.3f}s 超过预期 {max_time}s"
        return response_time

    def _measure_multiple_requests(self, operation, count: int = 10, max_avg_time: float = 2.0) -> dict:
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

    def _test_concurrent_performance(self, operation, concurrent_count: int = 10, success_rate: float = 0.9) -> dict:
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
    
    def test_01_overview_statistics_performance(self):
        """测试统计概览性能"""
        def get_overview():
            response = self.client.get("/api/statistics/overview", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_overview, max_time=3.0)
        logger.info(f"✅ 统计概览性能: {response_time:.3f}秒")

    def test_02_card_statistics_performance(self):
        """测试信用卡统计性能"""
        def get_card_stats():
            response = self.client.get("/api/statistics/cards", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_card_stats, max_time=1.5)
        logger.info(f"✅ 信用卡统计性能: {response_time:.3f}秒")

    def test_03_transaction_statistics_performance(self):
        """测试交易统计性能"""
        def get_transaction_stats():
            response = self.client.get("/api/statistics/transactions", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_transaction_stats, max_time=2.0)
        logger.info(f"✅ 交易统计性能: {response_time:.3f}秒")

    def test_04_category_statistics_performance(self):
        """测试分类统计性能"""
        def get_category_stats():
            response = self.client.get("/api/statistics/categories", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_category_stats, max_time=1.5)
        logger.info(f"✅ 分类统计性能: {response_time:.3f}秒")

    def test_05_monthly_trends_performance(self):
        """测试月度趋势性能"""
        def get_monthly_trends():
            response = self.client.get("/api/statistics/monthly-trends", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_monthly_trends, max_time=2.0)
        logger.info(f"✅ 月度趋势性能: {response_time:.3f}秒")

    # ==================== 批量操作性能测试 ====================
    
    def test_06_multiple_overview_requests_performance(self):
        """测试多次概览请求性能"""
        def get_overview():
            response = self.client.get("/api/statistics/overview", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._measure_multiple_requests(get_overview, count=10, max_avg_time=3.0)
        logger.info(f"✅ 多次概览请求性能: 平均 {metrics['avg_response_time']:.3f}秒, 范围 {metrics['min_response_time']:.3f}-{metrics['max_response_time']:.3f}秒")

    def test_07_filtered_statistics_performance(self):
        """测试带筛选条件的统计性能"""
        def get_filtered_stats():
            # 测试各种筛选条件的性能
            test_scenarios = [
                "/api/statistics/overview?start_date=2024-01-01&end_date=2024-12-31",
                f"/api/statistics/overview?bank_name=性能测试银行0",
                f"/api/statistics/overview?card_id={self.card_ids[0]}",
                "/api/statistics/categories?limit=5"
            ]
            
            for scenario in test_scenarios:
                response = self.client.get(scenario, headers=self.headers)
                self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_filtered_stats, max_time=5.0)
        logger.info(f"✅ 筛选统计性能: {response_time:.3f}秒")

    def test_08_all_endpoints_sequential_performance(self):
        """测试所有统计接口顺序执行性能"""
        def get_all_statistics():
            endpoints = [
                "/api/statistics/overview",
                "/api/statistics/cards",
                "/api/statistics/credit-limit", 
                "/api/statistics/transactions",
                "/api/statistics/annual-fee",
                "/api/statistics/categories",
                "/api/statistics/monthly-trends",
                "/api/statistics/banks"
            ]
            
            for endpoint in endpoints:
                response = self.client.get(endpoint, headers=self.headers)
                self.api_test.assert_api_success(response, 200)
        
        response_time = self._measure_response_time(get_all_statistics, max_time=8.0)
        logger.info(f"✅ 全接口顺序执行性能: {response_time:.3f}秒")

    # ==================== 并发性能测试 ====================
    
    def test_09_concurrent_overview_requests(self):
        """测试并发概览请求性能"""
        def get_overview():
            response = self.client.get("/api/statistics/overview", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._test_concurrent_performance(get_overview, concurrent_count=10, success_rate=0.8)
        logger.info(f"✅ 并发概览请求: 成功率 {metrics['success_rate']:.2%}, 吞吐量 {metrics['throughput']:.1f} req/s")

    def test_10_concurrent_different_statistics(self):
        """测试并发不同统计请求性能"""
        endpoints = [
            "/api/statistics/overview",
            "/api/statistics/cards",
            "/api/statistics/transactions",
            "/api/statistics/categories",
            "/api/statistics/monthly-trends"
        ]
        
        def get_random_statistics():
            import random
            endpoint = random.choice(endpoints)
            response = self.client.get(endpoint, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        metrics = self._test_concurrent_performance(get_random_statistics, concurrent_count=15, success_rate=0.8)
        logger.info(f"✅ 并发不同统计请求: 成功率 {metrics['success_rate']:.2%}, 吞吐量 {metrics['throughput']:.1f} req/s")

    # ==================== 压力测试 ====================
    
    def test_11_high_load_statistics_performance(self):
        """测试高负载下的统计性能"""
        def heavy_statistics_load():
            # 模拟重负载场景：大量筛选条件的复杂查询
            complex_scenarios = [
                "/api/statistics/overview?start_date=2023-01-01&end_date=2024-12-31&include_cancelled=true",
                "/api/statistics/transactions?start_date=2024-01-01&end_date=2024-12-31",
                "/api/statistics/categories?limit=20",
                "/api/statistics/monthly-trends"
            ]
            
            for scenario in complex_scenarios:
                response = self.client.get(scenario, headers=self.headers)
                self.api_test.assert_api_success(response, 200)
        
        # 连续执行5次重负载测试
        metrics = self._measure_multiple_requests(heavy_statistics_load, count=5, max_avg_time=10.0)
        logger.info(f"✅ 高负载统计性能: 平均 {metrics['avg_response_time']:.3f}秒")

    def test_12_sustained_load_performance(self):
        """测试持续负载性能"""
        def sustained_operation():
            response = self.client.get("/api/statistics/overview", headers=self.headers)
            self.api_test.assert_api_success(response, 200)
            time.sleep(0.1)  # 100ms间隔
        
        # 持续30秒的负载测试
        start_time = time.time()
        request_count = 0
        response_times = []
        
        while time.time() - start_time < 30:
            request_start = time.time()
            sustained_operation()
            request_time = time.time() - request_start
            response_times.append(request_time)
            request_count += 1
        
        total_time = time.time() - start_time
        avg_response_time = statistics.mean(response_times)
        throughput = request_count / total_time
        
        # 验证持续负载下的性能稳定性
        assert avg_response_time < 5.0, f"持续负载平均响应时间 {avg_response_time:.3f}s 过长"
        assert throughput > 1.0, f"持续负载吞吐量 {throughput:.1f} req/s 过低"
        
        logger.info(f"✅ 持续负载性能: {request_count}次请求, 平均 {avg_response_time:.3f}秒/请求, 吞吐量 {throughput:.1f} req/s") 