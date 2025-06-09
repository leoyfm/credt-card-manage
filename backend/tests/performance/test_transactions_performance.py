"""
交易记录性能测试

基于FastAPI TestClient的性能测试，验证交易记录相关操作的性能表现。
包括响应时间、并发性能、资源使用等指标的测试。
"""

import pytest
import logging
import time
import threading
import statistics
import queue
from datetime import datetime, timedelta
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed

from tests.base_test import RequestsTestClient, BaseAPITest

logger = logging.getLogger(__name__)


@pytest.mark.performance
@pytest.mark.requires_server
class TestTransactionsPerformance(BaseAPITest):
    """交易记录性能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        client = RequestsTestClient()
        super().__init__(client)  # 正确初始化父类
        self._check_server_availability()
        self.setup_test_user()
        
        # 创建测试信用卡
        self.test_card = self.create_test_card()
        self.card_id = self.test_card["id"]
        
        # 性能测试阈值配置
        self.performance_thresholds = {
            "create_max_time": 2.0,      # 创建操作最大耗时(秒)
            "query_max_time": 1.0,       # 查询操作最大耗时(秒)
            "list_max_time": 1.5,        # 列表操作最大耗时(秒)
            "update_max_time": 2.0,      # 更新操作最大耗时(秒)
            "delete_max_time": 1.5,      # 删除操作最大耗时(秒)
            "stats_max_time": 3.0,       # 统计操作最大耗时(秒)
            "concurrent_success_rate": 0.85,  # 并发操作成功率阈值
            "batch_throughput_min": 10,  # 批量操作最小吞吐量(ops/s)
        }
        
        logger.info(f"✅ 性能测试环境准备就绪: 用户{self.user_id}, 卡片{self.card_id}")
    
    def _check_server_availability(self):
        """检查服务器是否可用"""
        try:
            response = self.client.get("/health")
            if response.status_code != 200:
                raise Exception(f"服务器健康检查失败: {response.status_code}")
        except Exception as e:
            pytest.skip(f"服务器不可用，跳过性能测试: {str(e)}")
    
    def _measure_operation_time(self, operation_func, *args, **kwargs):
        """测量操作执行时间"""
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def _create_test_transaction(self, amount: float = None, merchant_suffix: str = ""):
        """创建测试交易记录"""
        if amount is None:
            amount = 100.00 + (time.time() % 1000)
        
        timestamp_us = int(time.time() * 1000000)
        
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": amount,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": f"性能测试商户{merchant_suffix}_{timestamp_us}",
            "category": "dining",
            "description": f"性能测试交易{merchant_suffix}"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        return self.assert_api_success(response, 200)
    
    # ==================== 单操作性能测试 ====================
    
    def test_01_create_operation_performance(self):
        """测试创建操作性能"""
        performance_results = []
        
        # 执行多次创建操作测试
        for i in range(10):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": 100.00 + i,
                "transaction_date": "2024-06-08T14:30:00",
                "merchant_name": f"性能测试商户{i}_{int(time.time() * 1000000)}",
                "category": "dining"
            }
            
            result, execution_time = self._measure_operation_time(
                self.client.post, "/api/transactions", 
                json=transaction_data, headers=self.headers
            )
            
            assert result.status_code in [200, 201], f"创建操作失败: {result.status_code}"
            performance_results.append(execution_time)
            
            # 避免时间戳冲突
            time.sleep(0.001)
        
        # 分析性能数据
        avg_time = statistics.mean(performance_results)
        max_time = max(performance_results)
        min_time = min(performance_results)
        p95_time = statistics.quantiles(performance_results, n=20)[18]  # 95th percentile
        
        # 性能断言
        assert max_time < self.performance_thresholds["create_max_time"], \
            f"创建操作最大耗时超标: {max_time:.3f}s > {self.performance_thresholds['create_max_time']}s"
        
        assert avg_time < self.performance_thresholds["create_max_time"] * 0.7, \
            f"创建操作平均耗时过高: {avg_time:.3f}s"
        
        logger.info(f"✅ 创建操作性能测试完成 - 平均:{avg_time:.3f}s, 最大:{max_time:.3f}s, 最小:{min_time:.3f}s, P95:{p95_time:.3f}s")
    
    def test_02_query_operation_performance(self):
        """测试查询操作性能"""
        # 先创建一个交易记录
        transaction = self._create_test_transaction()
        transaction_id = transaction["id"]
        
        performance_results = []
        
        # 执行多次查询操作
        for i in range(20):
            result, execution_time = self._measure_operation_time(
                self.client.get, f"/api/transactions/{transaction_id}", 
                headers=self.headers
            )
            
            assert result.status_code == 200, f"查询操作失败: {result.status_code}"
            performance_results.append(execution_time)
        
        # 分析性能数据
        avg_time = statistics.mean(performance_results)
        max_time = max(performance_results)
        p95_time = statistics.quantiles(performance_results, n=20)[18]
        
        # 性能断言
        assert max_time < self.performance_thresholds["query_max_time"], \
            f"查询操作最大耗时超标: {max_time:.3f}s"
        
        assert avg_time < self.performance_thresholds["query_max_time"] * 0.5, \
            f"查询操作平均耗时过高: {avg_time:.3f}s"
        
        logger.info(f"✅ 查询操作性能测试完成 - 平均:{avg_time:.3f}s, 最大:{max_time:.3f}s, P95:{p95_time:.3f}s")
    
    def test_03_list_operation_performance(self):
        """测试列表操作性能"""
        # 先创建一些测试数据
        for i in range(10):
            self._create_test_transaction(amount=100.0 + i, merchant_suffix=f"list{i}")
            time.sleep(0.001)
        
        performance_results = []
        
        # 测试不同分页大小的性能
        page_sizes = [10, 20, 50]
        
        for page_size in page_sizes:
            for page in [1, 2]:
                result, execution_time = self._measure_operation_time(
                    self.client.get, f"/api/transactions?page={page}&page_size={page_size}",
                    headers=self.headers
                )
                
                assert result.status_code == 200, f"列表操作失败: {result.status_code}"
                performance_results.append(execution_time)
        
        # 分析性能数据
        avg_time = statistics.mean(performance_results)
        max_time = max(performance_results)
        
        # 性能断言
        assert max_time < self.performance_thresholds["list_max_time"], \
            f"列表操作最大耗时超标: {max_time:.3f}s"
        
        logger.info(f"✅ 列表操作性能测试完成 - 平均:{avg_time:.3f}s, 最大:{max_time:.3f}s")
    
    def test_04_update_operation_performance(self):
        """测试更新操作性能"""
        # 创建测试数据
        transactions = []
        for i in range(5):
            tx = self._create_test_transaction(merchant_suffix=f"update{i}")
            transactions.append(tx)
            time.sleep(0.001)
        
        performance_results = []
        
        # 执行更新操作测试
        for i, transaction in enumerate(transactions):
            update_data = {
                "amount": 200.00 + i,
                "merchant_name": f"更新后的商户{i}",
                "description": f"更新测试{i}"
            }
            
            result, execution_time = self._measure_operation_time(
                self.client.put, f"/api/transactions/{transaction['id']}",
                json=update_data, headers=self.headers
            )
            
            assert result.status_code == 200, f"更新操作失败: {result.status_code}"
            performance_results.append(execution_time)
        
        # 分析性能数据
        avg_time = statistics.mean(performance_results)
        max_time = max(performance_results)
        
        # 性能断言
        assert max_time < self.performance_thresholds["update_max_time"], \
            f"更新操作最大耗时超标: {max_time:.3f}s"
        
        logger.info(f"✅ 更新操作性能测试完成 - 平均:{avg_time:.3f}s, 最大:{max_time:.3f}s")
    
    def test_05_delete_operation_performance(self):
        """测试删除操作性能"""
        # 创建测试数据
        transactions = []
        for i in range(5):
            tx = self._create_test_transaction(merchant_suffix=f"delete{i}")
            transactions.append(tx)
            time.sleep(0.001)
        
        performance_results = []
        
        # 执行删除操作测试
        for transaction in transactions:
            result, execution_time = self._measure_operation_time(
                self.client.delete, f"/api/transactions/{transaction['id']}",
                headers=self.headers
            )
            
            assert result.status_code == 200, f"删除操作失败: {result.status_code}"
            performance_results.append(execution_time)
        
        # 分析性能数据
        avg_time = statistics.mean(performance_results)
        max_time = max(performance_results)
        
        # 性能断言
        assert max_time < self.performance_thresholds["delete_max_time"], \
            f"删除操作最大耗时超标: {max_time:.3f}s"
        
        logger.info(f"✅ 删除操作性能测试完成 - 平均:{avg_time:.3f}s, 最大:{max_time:.3f}s")
    
    # ==================== 统计操作性能测试 ====================
    
    def test_06_statistics_performance(self):
        """测试统计操作性能"""
        # 创建大量测试数据用于统计
        for i in range(20):
            self._create_test_transaction(amount=100.0 + i*10, merchant_suffix=f"stats{i}")
            time.sleep(0.001)
        
        stats_endpoints = [
            "/api/transactions/statistics/overview",
            "/api/transactions/statistics/categories",
            "/api/transactions/statistics/monthly-trend?year=2024"
        ]
        
        for endpoint in stats_endpoints:
            performance_results = []
            
            # 对每个统计接口执行多次测试
            for _ in range(5):
                result, execution_time = self._measure_operation_time(
                    self.client.get, endpoint, headers=self.headers
                )
                
                assert result.status_code == 200, f"统计操作失败: {endpoint} - {result.status_code}"
                performance_results.append(execution_time)
            
            # 分析性能数据
            avg_time = statistics.mean(performance_results)
            max_time = max(performance_results)
            
            # 性能断言
            assert max_time < self.performance_thresholds["stats_max_time"], \
                f"统计操作最大耗时超标 {endpoint}: {max_time:.3f}s"
            
            logger.info(f"✅ 统计接口 {endpoint} 性能测试 - 平均:{avg_time:.3f}s, 最大:{max_time:.3f}s")
    
    # ==================== 并发性能测试 ====================
    
    def test_07_concurrent_create_performance(self):
        """测试并发创建性能"""
        concurrent_users = 20
        operations_per_user = 3
        
        def concurrent_create_worker(worker_id):
            """并发创建工作线程"""
            results = []
            errors = []
            
            for i in range(operations_per_user):
                try:
                    start_time = time.time()
                    timestamp_us = int(time.time() * 1000000)
                    
                    transaction_data = {
                        "card_id": self.card_id,
                        "transaction_type": "expense",
                        "amount": 100.00 + worker_id + i,
                        "transaction_date": "2024-06-08T14:30:00",
                        "merchant_name": f"并发测试{worker_id}_{i}_{timestamp_us}",
                        "category": "dining"
                    }
                    
                    response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
                    execution_time = time.time() - start_time
                    
                    if response.status_code in [200, 201]:
                        results.append(execution_time)
                    else:
                        errors.append(f"Worker{worker_id}-{i}: HTTP {response.status_code}")
                        
                except Exception as e:
                    errors.append(f"Worker{worker_id}-{i}: {str(e)}")
            
            return results, errors
        
        # 执行并发测试
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(concurrent_create_worker, i) for i in range(concurrent_users)]
            
            all_results = []
            all_errors = []
            
            for future in as_completed(futures):
                results, errors = future.result()
                all_results.extend(results)
                all_errors.extend(errors)
        
        total_time = time.time() - start_time
        
        # 分析并发性能
        success_count = len(all_results)
        total_operations = concurrent_users * operations_per_user
        success_rate = success_count / total_operations
        throughput = success_count / total_time
        
        if all_results:
            avg_response_time = statistics.mean(all_results)
            max_response_time = max(all_results)
        else:
            avg_response_time = max_response_time = 0
        
        # 性能断言
        assert success_rate >= self.performance_thresholds["concurrent_success_rate"], \
            f"并发创建成功率过低: {success_rate:.2%} < {self.performance_thresholds['concurrent_success_rate']:.2%}"
        
        assert throughput >= self.performance_thresholds["batch_throughput_min"], \
            f"并发吞吐量过低: {throughput:.1f} ops/s"
        
        if all_errors:
            logger.warning(f"并发创建错误: {all_errors[:5]}...")  # 只显示前5个错误
        
        logger.info(f"✅ 并发创建性能测试完成 - 成功率:{success_rate:.2%}, 吞吐量:{throughput:.1f}ops/s, 平均响应:{avg_response_time:.3f}s")
    
    def test_08_concurrent_read_performance(self):
        """测试并发读取性能"""
        # 先创建一些测试数据
        test_transactions = []
        for i in range(10):
            tx = self._create_test_transaction(merchant_suffix=f"read{i}")
            test_transactions.append(tx)
            time.sleep(0.001)
        
        concurrent_users = 15
        reads_per_user = 5
        
        def concurrent_read_worker(worker_id):
            """并发读取工作线程"""
            results = []
            errors = []
            
            for i in range(reads_per_user):
                try:
                    start_time = time.time()
                    
                    # 随机选择读取操作
                    import random
                    if random.choice([True, False]):
                        # 读取列表
                        response = self.client.get("/api/transactions?page=1&page_size=10", headers=self.headers)
                    else:
                        # 读取详情
                        tx = random.choice(test_transactions)
                        response = self.client.get(f"/api/transactions/{tx['id']}", headers=self.headers)
                    
                    execution_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        results.append(execution_time)
                    else:
                        errors.append(f"Worker{worker_id}-{i}: HTTP {response.status_code}")
                        
                except Exception as e:
                    errors.append(f"Worker{worker_id}-{i}: {str(e)}")
            
            return results, errors
        
        # 执行并发读取测试
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(concurrent_read_worker, i) for i in range(concurrent_users)]
            
            all_results = []
            all_errors = []
            
            for future in as_completed(futures):
                results, errors = future.result()
                all_results.extend(results)
                all_errors.extend(errors)
        
        total_time = time.time() - start_time
        
        # 分析并发读取性能
        success_count = len(all_results)
        total_operations = concurrent_users * reads_per_user
        success_rate = success_count / total_operations
        throughput = success_count / total_time
        
        if all_results:
            avg_response_time = statistics.mean(all_results)
            max_response_time = max(all_results)
        else:
            avg_response_time = max_response_time = 0
        
        # 性能断言
        assert success_rate >= 0.95, f"并发读取成功率过低: {success_rate:.2%}"
        assert avg_response_time < 1.0, f"并发读取平均响应时间过长: {avg_response_time:.3f}s"
        
        logger.info(f"✅ 并发读取性能测试完成 - 成功率:{success_rate:.2%}, 吞吐量:{throughput:.1f}ops/s, 平均响应:{avg_response_time:.3f}s")
    
    # ==================== 大数据量性能测试 ====================
    
    def test_09_large_dataset_performance(self):
        """测试大数据量情况下的性能"""
        # 创建大量测试数据
        batch_size = 50
        logger.info(f"开始创建{batch_size}条测试数据...")
        
        created_ids = []
        batch_create_times = []
        
        # 分批创建数据
        for batch in range(batch_size // 10):
            batch_start = time.time()
            
            for i in range(10):
                try:
                    tx = self._create_test_transaction(
                        amount=100.0 + batch*10 + i,
                        merchant_suffix=f"large{batch}_{i}"
                    )
                    created_ids.append(tx["id"])
                    time.sleep(0.001)  # 避免时间戳冲突
                except Exception as e:
                    logger.warning(f"创建测试数据失败: {e}")
            
            batch_time = time.time() - batch_start
            batch_create_times.append(batch_time)
        
        logger.info(f"成功创建{len(created_ids)}条测试数据")
        
        # 测试大数据量下的列表查询性能
        list_performance_results = []
        
        for page_size in [10, 20, 50]:
            result, execution_time = self._measure_operation_time(
                self.client.get, f"/api/transactions?page=1&page_size={page_size}",
                headers=self.headers
            )
            
            assert result.status_code == 200, f"大数据量列表查询失败: {result.status_code}"
            list_performance_results.append(execution_time)
        
        # 测试大数据量下的统计性能
        stats_result, stats_time = self._measure_operation_time(
            self.client.get, "/api/transactions/statistics/overview",
            headers=self.headers
        )
        
        assert stats_result.status_code == 200, f"大数据量统计查询失败: {stats_result.status_code}"
        
        # 性能分析
        avg_list_time = statistics.mean(list_performance_results)
        max_list_time = max(list_performance_results)
        
        # 性能断言
        assert max_list_time < 2.0, f"大数据量列表查询耗时过长: {max_list_time:.3f}s"
        assert stats_time < 5.0, f"大数据量统计查询耗时过长: {stats_time:.3f}s"
        
        logger.info(f"✅ 大数据量性能测试完成 - 列表平均:{avg_list_time:.3f}s, 统计:{stats_time:.3f}s")
    
    # ==================== 复杂查询性能测试 ====================
    
    def test_10_complex_query_performance(self):
        """测试复杂查询的性能"""
        # 创建多样化的测试数据
        categories = ["dining", "shopping", "transport", "entertainment"]
        transaction_types = ["expense", "payment", "refund"]
        
        for i in range(30):
            import random
            category = random.choice(categories)
            tx_type = random.choice(transaction_types)
            
            self._create_test_transaction(
                amount=random.uniform(10.0, 1000.0),
                merchant_suffix=f"complex{i}_{category}_{tx_type}"
            )
            time.sleep(0.001)
        
        # 测试各种复杂查询的性能
        complex_queries = [
            "/api/transactions?transaction_type=expense&category=dining",
            "/api/transactions?min_amount=100&max_amount=500",
            "/api/transactions?start_date=2024-06-01T00:00:00&end_date=2024-06-30T23:59:59",
            "/api/transactions?keyword=complex&page=1&page_size=20",
            "/api/transactions?transaction_type=expense&category=shopping&min_amount=200"
        ]
        
        query_performance_results = []
        
        for query in complex_queries:
            # 每个查询执行多次测试
            query_times = []
            
            for _ in range(3):
                result, execution_time = self._measure_operation_time(
                    self.client.get, query, headers=self.headers
                )
                
                assert result.status_code == 200, f"复杂查询失败: {query} - {result.status_code}"
                query_times.append(execution_time)
            
            avg_query_time = statistics.mean(query_times)
            query_performance_results.append(avg_query_time)
            
            logger.info(f"查询 {query} 平均耗时: {avg_query_time:.3f}s")
        
        # 性能分析
        overall_avg_time = statistics.mean(query_performance_results)
        max_query_time = max(query_performance_results)
        
        # 性能断言
        assert max_query_time < 2.0, f"复杂查询最大耗时超标: {max_query_time:.3f}s"
        assert overall_avg_time < 1.5, f"复杂查询平均耗时过高: {overall_avg_time:.3f}s"
        
        logger.info(f"✅ 复杂查询性能测试完成 - 平均:{overall_avg_time:.3f}s, 最大:{max_query_time:.3f}s")
    
    # ==================== 内存使用和资源性能测试 ====================
    
    def test_11_resource_usage_performance(self):
        """测试资源使用性能"""
        import psutil
        import os
        
        # 获取测试开始时的资源使用情况
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行一系列操作
        operations_count = 100
        operation_times = []
        
        for i in range(operations_count):
            start_time = time.time()
            
            # 执行混合操作
            if i % 4 == 0:
                # 创建操作
                self._create_test_transaction(merchant_suffix=f"resource{i}")
            elif i % 4 == 1:
                # 列表查询
                response = self.client.get("/api/transactions?page=1&page_size=10", headers=self.headers)
                assert response.status_code == 200
            elif i % 4 == 2:
                # 统计查询
                response = self.client.get("/api/transactions/statistics/overview", headers=self.headers)
                assert response.status_code == 200
            else:
                # 分类统计
                response = self.client.get("/api/transactions/statistics/categories", headers=self.headers)
                assert response.status_code == 200
            
            operation_time = time.time() - start_time
            operation_times.append(operation_time)
            
            # 小延迟避免过载
            time.sleep(0.001)
        
        # 获取测试结束时的资源使用情况
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 性能分析
        avg_operation_time = statistics.mean(operation_times)
        total_test_time = sum(operation_times)
        throughput = operations_count / total_test_time
        
        # 资源使用分析
        logger.info(f"内存使用变化: {initial_memory:.1f}MB -> {final_memory:.1f}MB (增加{memory_increase:.1f}MB)")
        logger.info(f"平均操作耗时: {avg_operation_time:.3f}s")
        logger.info(f"整体吞吐量: {throughput:.1f} ops/s")
        
        # 性能断言
        assert memory_increase < 100, f"内存增长过多: {memory_increase:.1f}MB"
        assert avg_operation_time < 2.0, f"平均操作耗时过长: {avg_operation_time:.3f}s"
        assert throughput > 5, f"整体吞吐量过低: {throughput:.1f} ops/s"
        
        logger.info("✅ 资源使用性能测试完成")
    
    def test_12_stress_test_performance(self):
        """压力测试"""
        stress_duration = 30  # 压力测试持续时间(秒)
        max_concurrent_users = 10
        
        def stress_test_worker(worker_id, stop_event):
            """压力测试工作线程"""
            operations = 0
            errors = 0
            
            while not stop_event.is_set():
                try:
                    # 随机执行不同操作
                    import random
                    operation = random.choice(['create', 'list', 'stats'])
                    
                    if operation == 'create':
                        tx_data = {
                            "card_id": self.card_id,
                            "transaction_type": "expense",
                            "amount": random.uniform(10.0, 1000.0),
                            "transaction_date": "2024-06-08T14:30:00",
                            "merchant_name": f"压力测试{worker_id}_{int(time.time()*1000000)}",
                            "category": random.choice(["dining", "shopping", "transport"])
                        }
                        response = self.client.post("/api/transactions", json=tx_data, headers=self.headers)
                    elif operation == 'list':
                        page = random.randint(1, 3)
                        response = self.client.get(f"/api/transactions?page={page}&page_size=10", headers=self.headers)
                    else:  # stats
                        response = self.client.get("/api/transactions/statistics/overview", headers=self.headers)
                    
                    if response.status_code in [200, 201]:
                        operations += 1
                    else:
                        errors += 1
                        
                except Exception:
                    errors += 1
                
                # 短暂休息避免过载
                time.sleep(0.01)
            
            return operations, errors
        
        # 启动压力测试
        import threading
        
        stop_event = threading.Event()
        threads = []
        
        logger.info(f"开始{stress_duration}秒压力测试，{max_concurrent_users}个并发用户...")
        
        start_time = time.time()
        
        # 启动工作线程
        for i in range(max_concurrent_users):
            thread = threading.Thread(target=stress_test_worker, args=(i, stop_event))
            threads.append(thread)
            thread.start()
        
        # 运行指定时间
        time.sleep(stress_duration)
        stop_event.set()
        
        # 等待所有线程结束
        results = []
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 这里简化处理，实际应该收集每个线程的返回值
        logger.info(f"✅ 压力测试完成，运行时间: {total_time:.1f}秒")


# ==================== 性能测试数据生成器 ====================

class TransactionPerformanceTestDataGenerator:
    """交易性能测试数据生成器"""
    
    @staticmethod
    def generate_batch_test_data(card_id: str, count: int = 100) -> list:
        """生成批量性能测试数据"""
        import random
        
        categories = ["dining", "shopping", "transport", "entertainment", "other"]
        transaction_types = ["expense", "payment", "refund"]
        merchants = ["商户A", "商户B", "商户C", "商户D", "商户E"]
        
        test_data = []
        
        for i in range(count):
            timestamp_us = int(time.time() * 1000000) + i
            
            data = {
                "card_id": card_id,
                "transaction_type": random.choice(transaction_types),
                "amount": round(random.uniform(10.0, 2000.0), 2),
                "transaction_date": "2024-06-08T14:30:00",
                "merchant_name": f"{random.choice(merchants)}_perf_{timestamp_us}",
                "category": random.choice(categories),
                "description": f"性能测试数据{i+1}",
                "status": "completed"
            }
            
            test_data.append(data)
        
        return test_data 