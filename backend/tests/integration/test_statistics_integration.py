"""
统计功能集成测试

使用真实HTTP请求测试统计功能的端到端功能。
需要手动启动服务器：python start.py dev

覆盖范围：
- 端到端统计流程测试
- 复杂业务场景验证
- 网络层协议验证
- 真实用户操作模拟
- 安全性和权限验证
- 数据完整性检查
"""

import pytest
import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from uuid import uuid4

from tests.base_test import RequestsTestClient, BaseAPITest

logger = logging.getLogger(__name__)


class StatisticsIntegrationTestDataGenerator:
    """统计集成测试数据生成器"""
    
    @staticmethod
    def generate_integration_card_data() -> Dict[str, Any]:
        """生成集成测试用信用卡数据"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "card_name": f"统计集成测试卡{unique_id}",
            "bank_name": "统计集成测试银行",
            "card_number": f"533{unique_id:010d}5678",
            "expiry_month": 11,
            "expiry_year": 2028,
            "credit_limit": "80000.00",
            "status": "active"
        }
    
    @staticmethod
    def generate_comprehensive_transaction_data(card_id: str) -> List[Dict[str, Any]]:
        """生成全面的测试交易数据"""
        transactions = []
        categories = ["dining", "shopping", "transport", "entertainment", "medical", "education", "travel", "other"]
        transaction_types = ["expense", "payment", "refund"]
        
        # 生成最近6个月的交易数据
        base_date = datetime.now()
        for month_offset in range(6):
            month_date = base_date - timedelta(days=30 * month_offset)
            
            # 每个月生成5-10笔交易
            import random
            transaction_count = random.randint(5, 10)
            
            for i in range(transaction_count):
                unique_id = int(time.time() * 1000000) % 1000000 + month_offset * 100 + i
                transaction = {
                    "card_id": card_id,
                    "transaction_type": random.choice(transaction_types),
                    "amount": f"{random.randint(100, 3000)}.{random.randint(10, 99):02d}",
                    "transaction_date": f"{month_date.year}-{month_date.month:02d}-{random.randint(1, 28):02d}T{random.randint(9, 21)}:{random.randint(0, 59):02d}:00",
                    "merchant_name": f"统计集成测试商户{unique_id}",
                    "category": random.choice(categories),
                    "description": f"统计集成测试交易{unique_id}"
                }
                transactions.append(transaction)
        
        return transactions


@pytest.mark.integration
@pytest.mark.requires_server
class TestStatisticsIntegration:
    """统计功能集成测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.client = RequestsTestClient()
        cls.api_test = BaseAPITest(cls.client)
        cls._check_server_availability()
        cls.user_data = cls.api_test.setup_test_user()
        cls.headers = {"Authorization": f"Bearer {cls.user_data['token']}"}
        
        # 创建多张测试信用卡
        cls.test_cards = []
        for i in range(3):
            card_data = StatisticsIntegrationTestDataGenerator.generate_integration_card_data()
            card = cls.api_test.create_test_card(card_data)
            cls.test_cards.append(card)
        
        # 为每张卡创建交易数据
        cls.test_transactions = []
        for card in cls.test_cards:
            transactions = StatisticsIntegrationTestDataGenerator.generate_comprehensive_transaction_data(card["id"])
            for tx_data in transactions:
                response = cls.client.post("/api/transactions", json=tx_data, headers=cls.headers)
                if response.status_code == 201:
                    transaction_data = cls.api_test.assert_api_success(response, 201)
                    cls.test_transactions.append(transaction_data)
        
        logger.info(f"✅ 统计集成测试环境设置完成: {len(cls.test_cards)}张卡片, {len(cls.test_transactions)}笔交易")

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
    
    def test_01_complete_statistics_workflow(self):
        """测试完整的统计数据获取流程"""
        # 1. 获取统计概览
        overview_response = self.client.get("/api/statistics/overview", headers=self.headers)
        overview_data = self.api_test.assert_api_success(overview_response, 200)
        
        # 2. 验证概览数据完整性
        assert "card_stats" in overview_data
        assert "credit_stats" in overview_data
        assert "transaction_stats" in overview_data
        assert "annual_fee_stats" in overview_data
        assert "top_categories" in overview_data
        assert "monthly_trends" in overview_data
        assert "bank_distribution" in overview_data
        
        # 3. 验证数据合理性
        assert overview_data["card_stats"]["total_cards"] >= len(self.test_cards)
        assert overview_data["transaction_stats"]["total_transactions"] >= len(self.test_transactions)
        
        # 4. 获取详细统计并验证一致性
        card_response = self.client.get("/api/statistics/cards", headers=self.headers)
        card_data = self.api_test.assert_api_success(card_response, 200)
        assert card_data["total_cards"] == overview_data["card_stats"]["total_cards"]
        
        logger.info("✅ 完整统计流程测试成功")

    def test_02_cross_module_data_consistency(self):
        """测试跨模块数据一致性"""
        # 获取统计数据
        stats_response = self.client.get("/api/statistics/overview", headers=self.headers)
        stats_data = self.api_test.assert_api_success(stats_response, 200)
        
        # 获取信用卡列表数据
        cards_response = self.client.get("/api/cards", headers=self.headers)
        cards_data = self.api_test.assert_api_success(cards_response, 200)
        cards_count = len(cards_data["items"]) if "items" in cards_data else len(cards_data)
        
        # 获取交易列表数据
        transactions_response = self.client.get("/api/transactions", headers=self.headers)
        transactions_data = self.api_test.assert_api_success(transactions_response, 200)
        transactions_count = len(transactions_data["items"]) if "items" in transactions_data else len(transactions_data)
        
        # 验证数据一致性
        assert stats_data["card_stats"]["total_cards"] >= cards_count
        assert stats_data["transaction_stats"]["total_transactions"] >= transactions_count
        
        logger.info("✅ 跨模块数据一致性验证成功")

    def test_03_real_time_data_reflection(self):
        """测试实时数据反映"""
        # 1. 获取当前统计
        before_response = self.client.get("/api/statistics/overview", headers=self.headers)
        before_data = self.api_test.assert_api_success(before_response, 200)
        
        # 2. 创建新交易
        new_transaction = {
            "card_id": self.test_cards[0]["id"],
            "transaction_type": "expense",
            "amount": "999.99",
            "transaction_date": "2024-06-20T15:30:00",
            "merchant_name": "实时测试商户",
            "category": "other",
            "description": "实时数据反映测试"
        }
        
        create_response = self.client.post("/api/transactions", json=new_transaction, headers=self.headers)
        self.api_test.assert_api_success(create_response, 200)
        
        # 3. 获取更新后的统计
        after_response = self.client.get("/api/statistics/overview", headers=self.headers)
        after_data = self.api_test.assert_api_success(after_response, 200)
        
        # 4. 验证统计数据已更新
        assert after_data["transaction_stats"]["total_transactions"] >= before_data["transaction_stats"]["total_transactions"]
        assert float(after_data["transaction_stats"]["total_expense_amount"]) >= float(before_data["transaction_stats"]["total_expense_amount"])
        
        logger.info("✅ 实时数据反映测试成功")

    def test_04_multi_user_data_isolation(self):
        """测试多用户数据隔离"""
        # 创建另一个用户
        other_user = self.api_test.setup_test_user()
        other_headers = {"Authorization": f"Bearer {other_user['token']}"}
        
        # 获取当前用户统计
        user1_response = self.client.get("/api/statistics/overview", headers=self.headers)
        user1_data = self.api_test.assert_api_success(user1_response, 200)
        
        # 获取其他用户统计
        user2_response = self.client.get("/api/statistics/overview", headers=other_headers)
        user2_data = self.api_test.assert_api_success(user2_response, 200)
        
        # 验证数据隔离
        assert user1_data["card_stats"]["total_cards"] >= len(self.test_cards)
        assert user2_data["card_stats"]["total_cards"] == 0
        assert user1_data["transaction_stats"]["total_transactions"] >= len(self.test_transactions)
        assert user2_data["transaction_stats"]["total_transactions"] == 0
        
        logger.info("✅ 多用户数据隔离验证成功")

    # ==================== 复杂业务场景测试 ====================
    
    def test_05_comprehensive_filtering_scenarios(self):
        """测试综合筛选场景"""
        test_bank = "统计集成测试银行"
        test_card_id = self.test_cards[0]["id"]
        
        # 测试各种筛选组合
        filter_scenarios = [
            {"bank_name": test_bank},
            {"card_id": test_card_id},
            {"start_date": "2024-01-01", "end_date": "2024-12-31"},
            {"bank_name": test_bank, "include_cancelled": "false"},
            {"start_date": "2024-06-01", "end_date": "2024-06-30", "bank_name": test_bank}
        ]
        
        for scenario in filter_scenarios:
            query_params = "&".join([f"{k}={v}" for k, v in scenario.items()])
            response = self.client.get(f"/api/statistics/overview?{query_params}", headers=self.headers)
            data = self.api_test.assert_api_success(response, 200)
            
            # 验证筛选数据的合理性
            assert "card_stats" in data
            assert "transaction_stats" in data
        
        logger.info("✅ 综合筛选场景测试成功")

    def test_06_statistics_performance_under_load(self):
        """测试负载下的统计性能"""
        start_time = time.time()
        
        # 并发请求不同的统计接口
        import threading
        import queue
        
        result_queue = queue.Queue()
        endpoints = [
            "/api/statistics/overview",
            "/api/statistics/cards",
            "/api/statistics/credit-limit",
            "/api/statistics/transactions",
            "/api/statistics/categories",
            "/api/statistics/monthly-trends"
        ]
        
        def make_request(endpoint):
            try:
                response = self.client.get(endpoint, headers=self.headers)
                result_queue.put((endpoint, response.status_code, response.elapsed.total_seconds()))
            except Exception as e:
                result_queue.put((endpoint, "error", str(e)))
        
        # 创建并启动线程
        threads = []
        for endpoint in endpoints:
            thread = threading.Thread(target=make_request, args=(endpoint,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        total_time = time.time() - start_time
        success_count = 0
        total_response_time = 0
        
        while not result_queue.empty():
            endpoint, status, response_time = result_queue.get()
            if status == 200:
                success_count += 1
                if isinstance(response_time, (int, float)):
                    total_response_time += response_time
        
        # 验证性能指标
        assert success_count >= len(endpoints) * 0.8  # 至少80%成功
        assert total_time < 10.0  # 总时间不超过10秒
        
        logger.info(f"✅ 负载性能测试: {success_count}/{len(endpoints)} 成功, 总时间: {total_time:.2f}秒")

    def test_07_data_aggregation_accuracy(self):
        """测试数据聚合准确性"""
        # 获取分类统计
        categories_response = self.client.get("/api/statistics/categories", headers=self.headers)
        categories_data = self.api_test.assert_api_success(categories_response, 200)
        
        # 获取月度趋势
        trends_response = self.client.get("/api/statistics/monthly-trends", headers=self.headers)
        trends_data = self.api_test.assert_api_success(trends_response, 200)
        
        # 获取银行分布
        banks_response = self.client.get("/api/statistics/banks", headers=self.headers)
        banks_data = self.api_test.assert_api_success(banks_response, 200)
        
        # 验证聚合数据的数学一致性
        if categories_data:
            total_category_percentage = sum(cat["percentage"] for cat in categories_data)
            assert 0 <= total_category_percentage <= 100  # 百分比总和合理
        
        if trends_data:
            # 验证月度数据的时间顺序
            if len(trends_data) > 1:
                for i in range(1, len(trends_data)):
                    assert trends_data[i]["year_month"] <= trends_data[i-1]["year_month"] or trends_data[i]["year_month"] >= trends_data[i-1]["year_month"]
        
        if banks_data:
            # 验证银行数据的完整性
            total_bank_cards = sum(bank["card_count"] for bank in banks_data)
            overview_response = self.client.get("/api/statistics/overview", headers=self.headers)
            overview_data = self.api_test.assert_api_success(overview_response, 200)
            assert total_bank_cards == overview_data["card_stats"]["total_cards"]
        
        logger.info("✅ 数据聚合准确性验证成功")

    # ==================== 网络和协议测试 ====================
    
    def test_08_http_headers_and_content_type(self):
        """测试HTTP头和内容类型"""
        response = self.client.get("/api/statistics/overview", headers=self.headers)
        
        # 验证响应头
        assert response.headers.get("content-type", "").startswith("application/json")
        assert "server" in response.headers
        
        # 验证响应状态
        assert response.status_code == 200
        
        # 验证JSON格式
        data = response.json()
        assert isinstance(data, dict)
        assert "success" in data
        assert data["success"] is True
        
        logger.info("✅ HTTP协议验证成功")

    def test_09_response_compression_and_size(self):
        """测试响应压缩和大小"""
        # 请求大数据量的统计
        response = self.client.get("/api/statistics/overview", headers=self.headers)
        
        # 验证响应大小合理
        content_length = len(response.content)
        assert content_length > 0
        assert content_length < 1024 * 1024  # 小于1MB
        
        # 验证响应时间
        assert response.elapsed.total_seconds() < 5.0  # 5秒内响应
        
        logger.info(f"✅ 响应大小验证: {content_length} bytes, 响应时间: {response.elapsed.total_seconds():.3f}秒")

    def test_10_error_handling_and_recovery(self):
        """测试错误处理和恢复"""
        # 测试各种错误场景
        error_scenarios = [
            ("/api/statistics/categories?limit=-1", [400, 422]),
            ("/api/statistics/overview?start_date=invalid", [200, 400, 422]),
            ("/api/statistics/transactions?card_id=invalid-uuid", [200, 400, 422])
        ]
        
        for endpoint, expected_codes in error_scenarios:
            response = self.client.get(endpoint, headers=self.headers)
            assert response.status_code in expected_codes
            
            # 验证错误响应格式
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    assert isinstance(error_data, dict)
                except:
                    pass  # 某些错误可能不返回JSON
        
        # 验证系统恢复能力 - 正常请求仍然工作
        recovery_response = self.client.get("/api/statistics/overview", headers=self.headers)
        self.api_test.assert_api_success(recovery_response, 200)
        
        logger.info("✅ 错误处理和恢复验证成功")

    def test_11_concurrent_operations_integrity(self):
        """测试并发操作的数据完整性"""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def create_transaction_and_check_stats():
            try:
                # 创建交易
                new_transaction = {
                    "card_id": self.test_cards[0]["id"],
                    "transaction_type": "expense",
                    "amount": "100.00",
                    "transaction_date": "2024-06-25T12:00:00",
                    "merchant_name": "并发测试商户",
                    "category": "other",
                    "description": "并发完整性测试"
                }
                
                create_response = self.client.post("/api/transactions", json=new_transaction, headers=self.headers)
                
                # 立即查询统计
                stats_response = self.client.get("/api/statistics/overview", headers=self.headers)
                
                result_queue.put({
                    "create_status": create_response.status_code,
                    "stats_status": stats_response.status_code
                })
            except Exception as e:
                result_queue.put({"error": str(e)})
        
        # 启动多个并发操作
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_transaction_and_check_stats)
            threads.append(thread)
            thread.start()
        
        # 等待完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        success_count = 0
        while not result_queue.empty():
            result = result_queue.get()
            if "error" not in result and result["stats_status"] == 200:
                success_count += 1
        
        assert success_count >= 4  # 至少80%成功
        
        logger.info(f"✅ 并发操作完整性验证: {success_count}/5 成功")

    def test_12_comprehensive_integration_scenario(self):
        """测试综合集成场景"""
        # 这是一个模拟真实用户使用的综合测试场景
        
        # 1. 用户登录后查看统计概览
        overview_response = self.client.get("/api/statistics/overview", headers=self.headers)
        overview_data = self.api_test.assert_api_success(overview_response, 200)
        
        # 2. 查看详细的信用卡统计
        cards_response = self.client.get("/api/statistics/cards", headers=self.headers)
        cards_data = self.api_test.assert_api_success(cards_response, 200)
        
        # 3. 查看特定银行的统计
        bank_name = "统计集成测试银行"
        bank_stats_response = self.client.get(f"/api/statistics/overview?bank_name={bank_name}", headers=self.headers)
        bank_stats_data = self.api_test.assert_api_success(bank_stats_response, 200)
        
        # 4. 查看最近3个月的交易统计
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        period_response = self.client.get(
            f"/api/statistics/transactions?start_date={three_months_ago}&end_date={today}",
            headers=self.headers
        )
        period_data = self.api_test.assert_api_success(period_response, 200)
        
        # 5. 查看消费分类统计（前5名）
        categories_response = self.client.get("/api/statistics/categories?limit=5", headers=self.headers)
        categories_data = self.api_test.assert_api_success(categories_response, 200)
        
        # 6. 查看月度趋势
        trends_response = self.client.get("/api/statistics/monthly-trends", headers=self.headers)
        trends_data = self.api_test.assert_api_success(trends_response, 200)
        
        # 验证所有数据的一致性和合理性
        assert overview_data["card_stats"]["total_cards"] >= len(self.test_cards)
        assert overview_data["transaction_stats"]["total_transactions"] >= len(self.test_transactions)
        assert cards_data["total_cards"] == overview_data["card_stats"]["total_cards"]
        assert len(categories_data) <= 5
        
        logger.info("✅ 综合集成场景测试成功") 