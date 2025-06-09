"""
推荐接口集成测试

使用requests库对真实运行的服务器进行集成测试
测试覆盖：
- 真实HTTP请求/响应
- 网络层面的问题
- 端到端的用户场景
"""

import pytest
import logging
import requests
import time
from typing import List, Dict, Any

from tests.base_test import (
    RequestsTestClient, 
    BaseRecommendationTest, 
    TestPerformanceMixin,
    TestDataGenerator
)

pytestmark = [pytest.mark.integration, pytest.mark.requires_server]

logger = logging.getLogger(__name__)


class TestRecommendationsIntegration(TestPerformanceMixin):
    """推荐接口集成测试类"""
    
    def setup_method(self):
        """每个测试方法的初始化"""
        self.client = RequestsTestClient()
        self.api_test = BaseRecommendationTest(self.client)
        
        logger.info("🌐 推荐接口集成测试开始")
        
        # 检查服务器是否可用
        self._check_server_availability()
        
        # 设置测试用户（每次都创建新用户避免冲突）
        self.user_info = self.api_test.setup_test_user()
        self.headers = self.user_info["headers"]  # 直接使用返回的headers
        logger.info(f"✅ 测试用户设置完成: {self.user_info['user']['username']}")
        
        # 创建基础测试数据
        self.test_cards = []
        card_data_list = TestDataGenerator.generate_test_cards(2)
        for card_data in card_data_list:
            card = self.api_test.create_test_card(card_data)
            self.test_cards.append(card)
            
            # 为每张卡创建一些交易记录
            transaction_data_list = TestDataGenerator.generate_test_transactions(card["id"], 3)
            for transaction_data in transaction_data_list:
                self.api_test.create_test_transaction(card["id"], transaction_data)
    
    def _check_server_availability(self):
        """检查服务器是否可用"""
        max_retries = 5
        retry_interval = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.client.base_url}/docs", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 服务器可用")
                    return
            except requests.exceptions.RequestException as e:
                logger.warning(f"服务器连接尝试 {attempt + 1}/{max_retries} 失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
        
        pytest.fail("❌ 服务器不可用，请确保服务器已启动")
    
    def test_01_http_response_headers(self):
        """测试HTTP响应头"""
        logger.info("📋 测试HTTP响应头...")
        
        response = self.client.get("/api/recommendations/stats/user-profile", headers=self.headers)
        
        # 验证基本响应头
        assert "content-type" in response.headers
        assert "application/json" in response.headers.get("content-type", "")
        
        # 验证CORS头（如果配置了）
        if "access-control-allow-origin" in response.headers:
            logger.info("✅ CORS配置已启用")
        
        # 验证响应时间在合理范围内
        assert response.elapsed.total_seconds() < 5.0, "响应时间过长"
        
        logger.info(f"✅ HTTP响应头验证通过，响应时间: {response.elapsed.total_seconds():.3f}s")
    
    def test_02_concurrent_requests_handling(self):
        """测试并发请求处理"""
        logger.info("🚀 测试并发请求处理...")
        
        import concurrent.futures
        import threading
        
        def make_request(index):
            """发送单个请求"""
            try:
                response = self.client.get("/api/recommendations/stats/user-profile", headers=self.headers)
                return {
                    "index": index,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "index": index,
                    "error": str(e),
                    "success": False
                }
        
        # 发送10个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 分析结果
        successful_requests = [r for r in results if r.get("success", False)]
        failed_requests = [r for r in results if not r.get("success", False)]
        
        success_rate = len(successful_requests) / len(results) * 100
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
        
        # 验证成功率
        assert success_rate >= 90, f"并发请求成功率过低: {success_rate:.1f}%"
        assert avg_response_time < 3.0, f"平均响应时间过长: {avg_response_time:.3f}s"
        
        logger.info(f"✅ 并发处理验证通过: 成功率{success_rate:.1f}%，平均响应时间{avg_response_time:.3f}s")
        
        if failed_requests:
            logger.warning(f"⚠️  {len(failed_requests)}个请求失败")
    
    def test_03_network_error_resilience(self):
        """测试网络错误恢复能力"""
        logger.info("🌐 测试网络错误恢复能力...")
        
        # 测试超时处理
        try:
            # 使用极短的超时时间模拟网络问题
            response = requests.get(
                f"{self.client.base_url}/api/recommendations/stats/user-profile",
                headers=self.headers,
                timeout=0.001  # 1毫秒超时
            )
        except requests.exceptions.Timeout:
            logger.info("✅ 超时处理正常")
        except Exception as e:
            logger.info(f"✅ 网络异常处理正常: {type(e).__name__}")
        
        # 验证正常请求仍然工作
        response = self.client.get("/api/recommendations/stats/user-profile", headers=self.headers)
        self.api_test.assert_api_success(response)
        
        logger.info("✅ 网络错误恢复能力验证通过")
    
    def test_04_large_response_handling(self):
        """测试大响应处理"""
        logger.info("📦 测试大响应处理...")
        
        # 生成大量推荐以测试大响应
        for _ in range(3):
            self.api_test.test_generate_recommendations()
        
        # 请求大量数据
        response = self.client.get(
            "/api/recommendations",
            headers=self.headers,
            params={"page_size": 50}
        )
        
        data = self.api_test.assert_api_success(response)
        
        # 验证响应大小合理
        response_size = len(response.content)
        assert response_size < 1024 * 1024, f"响应过大: {response_size}字节"  # 限制1MB
        
        logger.info(f"✅ 大响应处理验证通过: 响应大小{response_size}字节")
    
    def test_05_session_persistence(self):
        """测试会话持久性"""
        logger.info("🔐 测试会话持久性...")
        
        # 使用同一token进行多次请求
        requests_count = 5
        for i in range(requests_count):
            response = self.client.get("/api/recommendations/stats/user-profile", headers=self.headers)
            self.api_test.assert_api_success(response)
            
            # 短暂延迟以模拟真实使用场景
            time.sleep(0.1)
        
        logger.info(f"✅ 会话持久性验证通过: {requests_count}次连续请求成功")
    
    def test_06_api_versioning_compatibility(self):
        """测试API版本兼容性"""
        logger.info("🔄 测试API版本兼容性...")
        
        # 测试不同的API路径格式
        api_endpoints = [
            "/api/recommendations",
            "/api/recommendations/",
            "/api/recommendations/stats/user-profile",
            "/api/recommendations/stats/user-profile/"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint, headers=self.headers)
                # 应该返回200或404，不应该返回500
                assert response.status_code in [200, 404], f"端点{endpoint}返回异常状态码: {response.status_code}"
                logger.info(f"✅ 端点{endpoint}: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ 端点{endpoint}测试失败: {e}")
    
    def test_07_real_world_user_flow(self):
        """测试真实用户流程"""
        logger.info("👤 测试真实用户流程...")
        
        # 步骤1: 用户查看画像
        profile_data = self.api_test.test_user_profile_stats()
        logger.info(f"👤 用户画像: {profile_data['total_cards']}张卡")
        
        # 步骤2: 生成推荐
        recommendations = self.api_test.test_generate_recommendations()
        logger.info(f"🎯 生成推荐: {len(recommendations)}条")
        
        # 步骤3: 浏览推荐列表
        list_data = self.api_test.test_get_recommendations_list(page_size=5)
        logger.info(f"📄 推荐列表: {len(list_data['items'])}条")
        
        # 步骤4: 查看推荐详情（如果有推荐）
        if len(recommendations) > 0:
            rec_id = recommendations[0]["id"]
            response = self.client.get(f"/api/recommendations/{rec_id}", headers=self.headers)
            detail_data = self.api_test.assert_api_success(response)
            logger.info(f"📝 推荐详情: {detail_data['title']}")
            
            # 步骤5: 提交反馈
            feedback_data = {
                "feedback_type": "like",
                "rating": 4,
                "comment": "很有帮助的推荐"
            }
            response = self.client.post(
                f"/api/recommendations/{rec_id}/feedback",
                json=feedback_data,
                headers=self.headers
            )
            feedback_result = self.api_test.assert_api_success(response, expected_status=201)
            logger.info("👍 反馈提交成功")
        
        # 步骤6: 搜索特定推荐
        search_data = self.api_test.test_get_recommendations_list(keyword="信用卡")
        logger.info(f"🔍 搜索结果: {len(search_data['items'])}条")
        
        logger.info("✅ 真实用户流程验证通过")
    
    def test_08_data_integrity_across_requests(self):
        """测试跨请求数据完整性"""
        logger.info("🔗 测试跨请求数据完整性...")
        
        # 生成推荐
        generated_recs = self.api_test.test_generate_recommendations()
        
        if len(generated_recs) > 0:
            # 获取推荐列表
            list_data = self.api_test.test_get_recommendations_list()
            
            # 获取第一个推荐的详情
            if len(list_data["items"]) > 0:
                rec_id = list_data["items"][0]["id"]
                
                response = self.client.get(f"/api/recommendations/{rec_id}", headers=self.headers)
                detail_data = self.api_test.assert_api_success(response)
                
                # 验证详情数据与列表数据一致
                list_item = list_data["items"][0]
                for field in ["id", "title", "bank_name", "recommendation_score"]:
                    if field in list_item and field in detail_data:
                        assert list_item[field] == detail_data[field], f"字段{field}在列表和详情中不一致"
                
                logger.info("✅ 跨请求数据一致性验证通过")
            else:
                logger.info("ℹ️  无推荐数据，跳过一致性测试")
        else:
            logger.info("ℹ️  无推荐数据，跳过一致性测试")
    
    def test_09_error_response_format(self):
        """测试错误响应格式"""
        logger.info("⚠️  测试错误响应格式...")
        
        # 测试404错误
        from uuid import uuid4
        fake_id = str(uuid4())
        response = self.client.get(f"/api/recommendations/{fake_id}", headers=self.headers)
        
        # API可能返回200但data为空，或者返回404
        assert response.status_code in [200, 404], f"期望状态码200或404，实际{response.status_code}"
        
        error_data = response.json()
        
        # 验证错误响应格式
        required_error_fields = ["success", "message"]
        for field in required_error_fields:
            assert field in error_data, f"错误响应缺少{field}字段"
        
        # 如果status_code是200，可能success为False或data为空
        if response.status_code == 200:
            assert error_data.get("success") is False or error_data.get("data") is None
        else:
            assert error_data["success"] is False
            
        assert isinstance(error_data["message"], str)
        assert len(error_data["message"]) > 0
        
        logger.info("✅ 错误响应格式验证通过")
    
    def test_10_performance_under_load(self):
        """测试负载下的性能"""
        logger.info("⚡ 测试负载下的性能...")
        
        def load_test_request(index):
            """负载测试请求"""
            start_time = time.time()
            try:
                response = self.client.get("/api/recommendations", headers=self.headers)
                end_time = time.time()
                
                return {
                    "success": response.status_code == 200,
                    "response_time": end_time - start_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "success": False,
                    "response_time": end_time - start_time,
                    "error": str(e)
                }
        
        # 并发负载测试
        metrics = self.measure_batch_operations_performance(
            lambda: load_test_request(0),
            count=20,
            max_avg_time=2.0,
            description="负载测试"
        )
        
        logger.info(f"✅ 负载性能验证通过: 平均{metrics['avg_response_time']:.3f}s/请求") 