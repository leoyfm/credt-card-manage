"""
推荐接口性能测试

专注于性能指标测试，包括：
- 响应时间基准测试
- 吞吐量测试
- 内存使用测试
- 并发压力测试
"""

import pytest
import logging
import time
import concurrent.futures
import threading
from typing import List, Dict, Any
from statistics import mean, median, stdev

from tests.base_test import (
    FastAPITestClient, 
    RequestsTestClient,
    BaseRecommendationTest, 
    TestPerformanceMixin,
    TestDataGenerator
)

pytestmark = [pytest.mark.performance, pytest.mark.slow]

logger = logging.getLogger(__name__)


class TestRecommendationsPerformance(TestPerformanceMixin):
    """推荐接口性能测试类"""
    
    def setup_method(self):
        """每个测试方法的初始化"""
        # 使用FastAPI TestClient以获得更稳定的性能测试
        self.client = FastAPITestClient()
        self.api_test = BaseRecommendationTest(self.client)
        
        logger.info("⚡ 推荐接口性能测试开始")
        
        # 设置测试用户（性能测试使用共享用户以避免重复创建）
        self.user_info = self.api_test.setup_test_user()
        self.headers = self.user_info["headers"]  # 直接使用返回的headers
        logger.info(f"✅ 测试用户设置完成: {self.user_info['user']['username']}")
        
        # 创建基础测试数据
        self.test_cards = []
        card_data_list = TestDataGenerator.generate_test_cards(5)  # 减少数量以提高性能
        for card_data in card_data_list:
            card = self.api_test.create_test_card(card_data)
            self.test_cards.append(card)
            
            # 为每张卡创建交易记录
            transaction_data_list = TestDataGenerator.generate_test_transactions(card["id"], 10)
            for transaction_data in transaction_data_list:
                self.api_test.create_test_transaction(card["id"], transaction_data)
        
        logger.info(f"✅ 性能测试数据创建完成: {len(self.test_cards)}张卡")

    
    def _measure_multiple_requests(self, request_func, count: int = 100) -> Dict[str, Any]:
        """测量多次请求的性能指标"""
        response_times = []
        success_count = 0
        error_count = 0
        
        start_time = time.time()
        
        for i in range(count):
            request_start = time.time()
            try:
                result = request_func()
                request_end = time.time()
                response_times.append(request_end - request_start)
                success_count += 1
            except Exception as e:
                request_end = time.time()
                response_times.append(request_end - request_start)
                error_count += 1
                logger.warning(f"请求 {i+1} 失败: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response_times:
            return {
                "total_requests": count,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_count / count * 100,
                "total_time": total_time,
                "avg_response_time": mean(response_times),
                "median_response_time": median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "std_response_time": stdev(response_times) if len(response_times) > 1 else 0,
                "requests_per_second": count / total_time,
                "response_times": response_times
            }
        else:
            return {
                "total_requests": count,
                "success_count": 0,
                "error_count": count,
                "success_rate": 0,
                "total_time": total_time
            }
    
    def test_01_user_profile_stats_performance(self):
        """测试用户画像分析性能"""
        logger.info("📊 测试用户画像分析性能...")
        
        def request_func():
            return self.api_test.test_user_profile_stats()
        
        # 测量100次请求
        metrics = self._measure_multiple_requests(request_func, count=100)
        
        # 性能基准验证
        assert metrics["success_rate"] >= 95, f"成功率过低: {metrics['success_rate']:.1f}%"
        assert metrics["avg_response_time"] < 0.5, f"平均响应时间过长: {metrics['avg_response_time']:.3f}s"
        assert metrics["max_response_time"] < 2.0, f"最大响应时间过长: {metrics['max_response_time']:.3f}s"
        assert metrics["requests_per_second"] > 20, f"每秒请求数过低: {metrics['requests_per_second']:.1f}"
        
        logger.info(f"✅ 用户画像性能验证通过:")
        logger.info(f"   - 平均响应时间: {metrics['avg_response_time']:.3f}s")
        logger.info(f"   - 中位数响应时间: {metrics['median_response_time']:.3f}s")
        logger.info(f"   - 每秒处理请求: {metrics['requests_per_second']:.1f}")
        logger.info(f"   - 成功率: {metrics['success_rate']:.1f}%")
    
    def test_02_generate_recommendations_performance(self):
        """测试推荐生成性能"""
        logger.info("🎯 测试推荐生成性能...")
        
        def request_func():
            return self.api_test.test_generate_recommendations()
        
        # 测量50次请求（推荐生成相对较慢）
        metrics = self._measure_multiple_requests(request_func, count=50)
        
        # 性能基准验证
        assert metrics["success_rate"] >= 90, f"成功率过低: {metrics['success_rate']:.1f}%"
        assert metrics["avg_response_time"] < 2.0, f"平均响应时间过长: {metrics['avg_response_time']:.3f}s"
        assert metrics["max_response_time"] < 5.0, f"最大响应时间过长: {metrics['max_response_time']:.3f}s"
        assert metrics["requests_per_second"] > 5, f"每秒请求数过低: {metrics['requests_per_second']:.1f}"
        
        logger.info(f"✅ 推荐生成性能验证通过:")
        logger.info(f"   - 平均响应时间: {metrics['avg_response_time']:.3f}s")
        logger.info(f"   - 中位数响应时间: {metrics['median_response_time']:.3f}s")
        logger.info(f"   - 每秒处理请求: {metrics['requests_per_second']:.1f}")
        logger.info(f"   - 成功率: {metrics['success_rate']:.1f}%")
    
    def test_03_recommendations_list_performance(self):
        """测试推荐列表性能"""
        logger.info("📄 测试推荐列表性能...")
        
        # 先生成一些推荐
        self.api_test.test_generate_recommendations()
        
        def request_func():
            return self.api_test.test_get_recommendations_list(page_size=20)
        
        # 测量100次请求
        metrics = self._measure_multiple_requests(request_func, count=100)
        
        # 性能基准验证
        assert metrics["success_rate"] >= 95, f"成功率过低: {metrics['success_rate']:.1f}%"
        assert metrics["avg_response_time"] < 0.3, f"平均响应时间过长: {metrics['avg_response_time']:.3f}s"
        assert metrics["max_response_time"] < 1.0, f"最大响应时间过长: {metrics['max_response_time']:.3f}s"
        assert metrics["requests_per_second"] > 30, f"每秒请求数过低: {metrics['requests_per_second']:.1f}"
        
        logger.info(f"✅ 推荐列表性能验证通过:")
        logger.info(f"   - 平均响应时间: {metrics['avg_response_time']:.3f}s")
        logger.info(f"   - 中位数响应时间: {metrics['median_response_time']:.3f}s")
        logger.info(f"   - 每秒处理请求: {metrics['requests_per_second']:.1f}")
        logger.info(f"   - 成功率: {metrics['success_rate']:.1f}%")
    
    def test_04_concurrent_requests_performance(self):
        """测试并发请求性能"""
        logger.info("🚀 测试并发请求性能...")
        
        # 先生成一些推荐
        self.api_test.test_generate_recommendations()
        
        def single_request(index):
            """单个并发请求"""
            start_time = time.time()
            try:
                data = self.api_test.test_get_recommendations_list(page_size=10)
                end_time = time.time()
                return {
                    "index": index,
                    "success": True,
                    "response_time": end_time - start_time,
                    "item_count": len(data["items"])
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "index": index,
                    "success": False,
                    "response_time": end_time - start_time,
                    "error": str(e)
                }
        
        # 测试不同并发级别
        concurrency_levels = [5, 10, 20]
        
        for concurrency in concurrency_levels:
            logger.info(f"测试并发级别: {concurrency}")
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(single_request, i) for i in range(concurrency * 2)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 分析并发测试结果
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            success_rate = len(successful_requests) / len(results) * 100
            avg_response_time = mean([r["response_time"] for r in successful_requests]) if successful_requests else 0
            requests_per_second = len(results) / total_time
            
            # 验证并发性能
            assert success_rate >= 90, f"并发{concurrency}成功率过低: {success_rate:.1f}%"
            assert avg_response_time < 3.0, f"并发{concurrency}平均响应时间过长: {avg_response_time:.3f}s"
            
            logger.info(f"✅ 并发{concurrency}性能验证通过: 成功率{success_rate:.1f}%，响应时间{avg_response_time:.3f}s")
    
    def test_05_memory_usage_stability(self):
        """测试内存使用稳定性"""
        logger.info("💾 测试内存使用稳定性...")
        
        def memory_intensive_requests():
            """内存密集型请求序列"""
            results = []
            for i in range(50):
                try:
                    # 生成推荐（相对内存密集）
                    recommendations = self.api_test.test_generate_recommendations()
                    # 获取列表
                    list_data = self.api_test.test_get_recommendations_list(page_size=50)
                    results.append({
                        "iteration": i,
                        "recommendations_count": len(recommendations),
                        "list_items_count": len(list_data["items"])
                    })
                except Exception as e:
                    logger.warning(f"内存测试迭代 {i} 失败: {e}")
            
            return results
        
        # 执行内存密集型测试
        start_time = time.time()
        results = memory_intensive_requests()
        end_time = time.time()
        
        # 验证结果
        assert len(results) >= 45, f"内存测试完成率过低: {len(results)}/50"
        
        total_time = end_time - start_time
        avg_time_per_iteration = total_time / len(results)
        
        logger.info(f"✅ 内存稳定性验证通过:")
        logger.info(f"   - 完成迭代: {len(results)}/50")
        logger.info(f"   - 总耗时: {total_time:.3f}s")
        logger.info(f"   - 平均每次迭代: {avg_time_per_iteration:.3f}s")
    
    def test_06_pagination_performance_scaling(self):
        """测试分页性能伸缩性"""
        logger.info("📊 测试分页性能伸缩性...")
        
        # 先生成一些推荐数据
        for _ in range(3):
            self.api_test.test_generate_recommendations()
        
        page_sizes = [10, 20, 50, 100]
        performance_data = []
        
        for page_size in page_sizes:
            def request_func():
                return self.api_test.test_get_recommendations_list(page_size=page_size)
            
            # 测量每种分页大小的性能
            metrics = self._measure_multiple_requests(request_func, count=20)
            
            performance_data.append({
                "page_size": page_size,
                "avg_response_time": metrics["avg_response_time"],
                "requests_per_second": metrics["requests_per_second"],
                "success_rate": metrics["success_rate"]
            })
            
            # 验证基本性能要求
            assert metrics["success_rate"] >= 95, f"分页大小{page_size}成功率过低"
            assert metrics["avg_response_time"] < 1.0, f"分页大小{page_size}响应时间过长"
            
            logger.info(f"✅ 分页大小{page_size}性能验证通过: {metrics['avg_response_time']:.3f}s")
        
        # 验证响应时间与分页大小的合理关系
        # 响应时间不应该随分页大小线性增长过快
        min_time = min(p["avg_response_time"] for p in performance_data)
        max_time = max(p["avg_response_time"] for p in performance_data)
        time_ratio = max_time / min_time if min_time > 0 else 1
        
        assert time_ratio < 5.0, f"分页响应时间伸缩性过差: 最大/最小时间比例{time_ratio:.2f}"
        
        logger.info(f"✅ 分页性能伸缩性验证通过: 时间比例{time_ratio:.2f}")
    
    def test_07_search_performance(self):
        """测试搜索性能"""
        logger.info("🔍 测试搜索性能...")
        
        # 先生成一些推荐数据
        self.api_test.test_generate_recommendations()
        
        search_keywords = ["信用卡", "银行", "推荐", "优惠", "积分"]
        
        for keyword in search_keywords:
            def request_func():
                return self.api_test.test_get_recommendations_list(keyword=keyword)
            
            # 测量搜索性能
            metrics = self._measure_multiple_requests(request_func, count=30)
            
            # 验证搜索性能
            assert metrics["success_rate"] >= 90, f"搜索'{keyword}'成功率过低: {metrics['success_rate']:.1f}%"
            assert metrics["avg_response_time"] < 0.8, f"搜索'{keyword}'响应时间过长: {metrics['avg_response_time']:.3f}s"
            
            logger.info(f"✅ 搜索'{keyword}'性能验证通过: {metrics['avg_response_time']:.3f}s")
    
    def test_08_stress_test(self):
        """压力测试"""
        logger.info("💪 执行压力测试...")
        
        # 先生成一些推荐数据
        self.api_test.test_generate_recommendations()
        
        def stress_request(index):
            """压力测试请求"""
            operations = [
                lambda: self.api_test.test_user_profile_stats(),
                lambda: self.api_test.test_generate_recommendations(),
                lambda: self.api_test.test_get_recommendations_list(page_size=20),
                lambda: self.api_test.test_get_recommendations_list(keyword="信用卡")
            ]
            
            # 随机选择操作
            import random
            operation = random.choice(operations)
            
            start_time = time.time()
            try:
                result = operation()
                end_time = time.time()
                return {
                    "index": index,
                    "success": True,
                    "response_time": end_time - start_time,
                    "operation": operation.__name__ if hasattr(operation, '__name__') else "lambda"
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "index": index,
                    "success": False,
                    "response_time": end_time - start_time,
                    "error": str(e)
                }
        
        # 执行压力测试：100个并发请求
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(stress_request, i) for i in range(100)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 分析压力测试结果
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results) * 100
        avg_response_time = mean([r["response_time"] for r in successful_requests]) if successful_requests else 0
        requests_per_second = len(results) / total_time
        
        # 验证压力测试结果
        assert success_rate >= 85, f"压力测试成功率过低: {success_rate:.1f}%"
        assert avg_response_time < 3.0, f"压力测试平均响应时间过长: {avg_response_time:.3f}s"
        
        logger.info(f"✅ 压力测试验证通过:")
        logger.info(f"   - 总请求: {len(results)}")
        logger.info(f"   - 成功率: {success_rate:.1f}%")
        logger.info(f"   - 平均响应时间: {avg_response_time:.3f}s")
        logger.info(f"   - 每秒处理请求: {requests_per_second:.1f}")
        logger.info(f"   - 总耗时: {total_time:.3f}s")
        
        if failed_requests:
            logger.warning(f"   - 失败请求: {len(failed_requests)}个")
    
    def test_09_performance_consistency(self):
        """测试性能一致性"""
        logger.info("📈 测试性能一致性...")
        
        # 多轮性能测试，检查性能一致性
        rounds = 5
        round_results = []
        
        for round_num in range(rounds):
            logger.info(f"执行第 {round_num + 1}/{rounds} 轮性能测试...")
            
            def request_func():
                return self.api_test.test_get_recommendations_list(page_size=20)
            
            metrics = self._measure_multiple_requests(request_func, count=20)
            round_results.append(metrics)
            
            time.sleep(1)  # 轮次间短暂休息
        
        # 分析性能一致性
        avg_response_times = [r["avg_response_time"] for r in round_results]
        requests_per_seconds = [r["requests_per_second"] for r in round_results]
        success_rates = [r["success_rate"] for r in round_results]
        
        # 计算性能指标的标准差
        response_time_std = stdev(avg_response_times) if len(avg_response_times) > 1 else 0
        rps_std = stdev(requests_per_seconds) if len(requests_per_seconds) > 1 else 0
        
        # 验证性能一致性
        avg_response_time_mean = mean(avg_response_times)
        rps_mean = mean(requests_per_seconds)
        
        # 标准差不应该太大（不超过均值的30%）
        response_time_cv = response_time_std / avg_response_time_mean if avg_response_time_mean > 0 else 0
        rps_cv = rps_std / rps_mean if rps_mean > 0 else 0
        
        assert response_time_cv < 0.3, f"响应时间变异系数过大: {response_time_cv:.3f}"
        assert rps_cv < 0.3, f"每秒请求数变异系数过大: {rps_cv:.3f}"
        
        logger.info(f"✅ 性能一致性验证通过:")
        logger.info(f"   - 响应时间变异系数: {response_time_cv:.3f}")
        logger.info(f"   - 每秒请求数变异系数: {rps_cv:.3f}")
        logger.info(f"   - 平均响应时间: {avg_response_time_mean:.3f}s (±{response_time_std:.3f})")
        logger.info(f"   - 平均每秒请求数: {rps_mean:.1f} (±{rps_std:.1f})")
    
    def test_10_performance_benchmark_summary(self):
        """性能基准总结测试"""
        logger.info("📋 执行性能基准总结...")
        
        # 定义基准测试场景
        benchmark_scenarios = [
            ("用户画像", lambda: self.api_test.test_user_profile_stats()),
            ("推荐生成", lambda: self.api_test.test_generate_recommendations()),
            ("推荐列表", lambda: self.api_test.test_get_recommendations_list()),
            ("搜索功能", lambda: self.api_test.test_get_recommendations_list(keyword="信用卡"))
        ]
        
        benchmark_results = []
        
        for scenario_name, scenario_func in benchmark_scenarios:
            logger.info(f"基准测试: {scenario_name}")
            
            # 测量性能
            metrics = self._measure_multiple_requests(scenario_func, count=30)
            
            benchmark_results.append({
                "scenario": scenario_name,
                "avg_response_time": metrics["avg_response_time"],
                "median_response_time": metrics["median_response_time"],
                "p95_response_time": sorted(metrics["response_times"])[int(len(metrics["response_times"]) * 0.95)],
                "requests_per_second": metrics["requests_per_second"],
                "success_rate": metrics["success_rate"]
            })
            
            logger.info(f"   {scenario_name}: {metrics['avg_response_time']:.3f}s, {metrics['requests_per_second']:.1f} RPS")
        
        # 验证整体性能满足基准要求
        for result in benchmark_results:
            scenario = result["scenario"]
            
            # 基本成功率要求
            assert result["success_rate"] >= 95, f"{scenario}成功率不达标: {result['success_rate']:.1f}%"
            
            # 根据场景类型设置不同的响应时间要求
            if scenario == "用户画像":
                assert result["avg_response_time"] < 0.5, f"{scenario}响应时间不达标"
                assert result["requests_per_second"] > 20, f"{scenario}吞吐量不达标"
            elif scenario == "推荐生成":
                assert result["avg_response_time"] < 2.0, f"{scenario}响应时间不达标"
                assert result["requests_per_second"] > 5, f"{scenario}吞吐量不达标"
            elif scenario == "推荐列表":
                assert result["avg_response_time"] < 0.3, f"{scenario}响应时间不达标"
                assert result["requests_per_second"] > 30, f"{scenario}吞吐量不达标"
            elif scenario == "搜索功能":
                assert result["avg_response_time"] < 0.8, f"{scenario}响应时间不达标"
                assert result["requests_per_second"] > 15, f"{scenario}吞吐量不达标"
        
        logger.info("✅ 性能基准总结验证通过:")
        for result in benchmark_results:
            logger.info(f"   {result['scenario']}: "
                       f"平均{result['avg_response_time']:.3f}s, "
                       f"P95 {result['p95_response_time']:.3f}s, "
                       f"{result['requests_per_second']:.1f} RPS") 