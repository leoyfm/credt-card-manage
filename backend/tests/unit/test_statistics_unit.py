"""
统计功能模块单元测试

使用FastAPI TestClient进行统计功能的单元测试。
测试覆盖统计数据的获取、筛选功能、时间范围查询和边界条件。

覆盖范围：
- 统计概览接口
- 各项分类统计接口  
- 查询参数筛选功能
- 时间范围查询
- 认证和权限验证
- 边界条件和异常处理
"""

import pytest
import logging
import time
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, Any, List
from uuid import uuid4

from tests.base_test import FastAPITestClient, BaseAPITest

logger = logging.getLogger(__name__)


class StatisticsTestDataGenerator:
    """统计功能测试数据生成器"""
    
    @staticmethod
    def generate_test_card_data() -> Dict[str, Any]:
        """生成测试信用卡数据"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "card_name": f"统计测试卡{unique_id}",
            "bank_name": "统计测试银行",
            "card_number": f"422{unique_id:010d}1234",
            "expiry_month": 12,
            "expiry_year": 2027,
            "credit_limit": "50000.00",
            "status": "active"
        }
    
    @staticmethod
    def generate_test_transaction_data(card_id: str) -> Dict[str, Any]:
        """生成测试交易数据"""
        return {
            "card_id": card_id,
            "transaction_type": "expense",
            "amount": "1500.00",
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "统计测试商户",
            "category": "dining",
            "description": "统计功能测试交易"
        }
    
    @staticmethod
    def generate_batch_transactions(card_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """生成批量测试交易"""
        transactions = []
        categories = ["dining", "shopping", "transport", "entertainment", "other"]
        amounts = ["100.00", "200.00", "500.00", "800.00", "1200.00"]
        
        for i in range(count):
            unique_id = int(time.time() * 1000000) % 1000000 + i
            transaction = {
                "card_id": card_id,
                "transaction_type": "expense",
                "amount": amounts[i % len(amounts)],
                "transaction_date": f"2024-{6+i%6:02d}-{8+i%20:02d}T{10+i%12:02d}:30:00",
                "merchant_name": f"统计测试商户{unique_id}",
                "category": categories[i % len(categories)],
                "description": f"统计测试交易{i+1}"
            }
            transactions.append(transaction)
        return transactions


@pytest.mark.unit
class TestStatisticsUnit:
    """统计功能单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        # 创建测试信用卡
        self.test_card = self.api_test.create_test_card(
            StatisticsTestDataGenerator.generate_test_card_data()
        )
        self.card_id = self.test_card["id"]
        
        # 创建一些测试交易数据
        self.test_transactions = []
        for tx_data in StatisticsTestDataGenerator.generate_batch_transactions(self.card_id, 5):
            response = self.client.post("/api/transactions", json=tx_data, headers=self.headers)
            if response.status_code == 201:
                transaction_data = self.api_test.assert_api_success(response, 201)
                self.test_transactions.append(transaction_data)
        
        logger.info(f"✅ 统计单元测试环境准备就绪: 用户{self.test_user['user_id']}, 卡片{self.card_id}, 交易{len(self.test_transactions)}笔")

    # ==================== 基础统计测试 ====================
    
    def test_01_get_statistics_overview_success(self):
        """测试获取统计概览（成功）"""
        response = self.client.get("/api/statistics/overview", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证统计概览结构
        assert "card_stats" in data
        assert "credit_stats" in data
        assert "transaction_stats" in data
        assert "annual_fee_stats" in data
        assert "top_categories" in data
        assert "monthly_trends" in data
        assert "bank_distribution" in data
        
        # 验证信用卡统计
        card_stats = data["card_stats"]
        assert "total_cards" in card_stats
        assert "active_cards" in card_stats
        assert card_stats["total_cards"] >= 1  # 至少有我们创建的测试卡
        
        logger.info("✅ 统计概览获取成功")

    def test_02_get_card_statistics_success(self):
        """测试获取信用卡统计（成功）"""
        response = self.client.get("/api/statistics/cards", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证信用卡统计结构
        assert "total_cards" in data
        assert "active_cards" in data
        assert "inactive_cards" in data
        assert "frozen_cards" in data
        assert "cancelled_cards" in data
        assert "expired_cards" in data
        assert "expiring_soon_cards" in data
        
        # 验证数据类型和合理性
        assert isinstance(data["total_cards"], int)
        assert data["total_cards"] >= 1  # 至少有我们创建的测试卡
        assert data["active_cards"] >= 0
        
        logger.info("✅ 信用卡统计获取成功")

    def test_03_get_credit_limit_statistics_success(self):
        """测试获取信用额度统计（成功）"""
        response = self.client.get("/api/statistics/credit-limit", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证信用额度统计结构
        assert "total_credit_limit" in data
        assert "total_used_amount" in data
        assert "total_available_amount" in data
        assert "overall_utilization_rate" in data
        assert "highest_utilization_rate" in data
        assert "lowest_utilization_rate" in data
        assert "average_utilization_rate" in data
        
        # 验证数据合理性
        assert float(data["total_credit_limit"]) >= 0
        assert float(data["total_used_amount"]) >= 0
        assert float(data["total_available_amount"]) >= 0
        assert 0 <= data["overall_utilization_rate"] <= 100
        
        logger.info("✅ 信用额度统计获取成功")

    def test_04_get_transaction_statistics_success(self):
        """测试获取交易统计（成功）"""
        response = self.client.get("/api/statistics/transactions", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证交易统计结构
        assert "total_transactions" in data
        assert "total_expense_amount" in data
        assert "total_payment_amount" in data
        assert "total_points_earned" in data
        assert "current_month_transactions" in data
        assert "current_month_expense_amount" in data
        assert "average_transaction_amount" in data
        
        # 验证数据合理性
        assert isinstance(data["total_transactions"], int)
        assert data["total_transactions"] >= len(self.test_transactions)
        assert float(data["total_expense_amount"]) >= 0
        
        logger.info("✅ 交易统计获取成功")

    def test_05_get_annual_fee_statistics_success(self):
        """测试获取年费统计（成功）"""
        response = self.client.get("/api/statistics/annual-fee", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证年费统计结构
        assert "total_annual_fee" in data
        assert "waived_count" in data
        assert "pending_count" in data
        assert "paid_count" in data
        assert "overdue_count" in data
        assert "current_year_due_amount" in data
        assert "savings_from_waiver" in data
        
        # 验证数据合理性
        assert float(data["total_annual_fee"]) >= 0
        assert isinstance(data["waived_count"], int)
        assert data["waived_count"] >= 0
        
        logger.info("✅ 年费统计获取成功")

    def test_06_get_category_statistics_success(self):
        """测试获取分类统计（成功）"""
        response = self.client.get("/api/statistics/categories", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证分类统计结构
        assert isinstance(data, list)
        if data:
            first_category = data[0]
            assert "category" in first_category
            assert "category_name" in first_category
            assert "transaction_count" in first_category
            assert "total_amount" in first_category
            assert "percentage" in first_category
            
            # 验证数据合理性
            assert isinstance(first_category["transaction_count"], int)
            assert first_category["transaction_count"] > 0
            assert float(first_category["total_amount"]) > 0
            assert 0 <= first_category["percentage"] <= 100
        
        logger.info("✅ 分类统计获取成功")

    def test_07_get_monthly_trends_success(self):
        """测试获取月度趋势（成功）"""
        response = self.client.get("/api/statistics/monthly-trends", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证月度趋势结构
        assert isinstance(data, list)
        if data:
            first_month = data[0]
            assert "year_month" in first_month
            assert "transaction_count" in first_month
            assert "expense_amount" in first_month
            assert "payment_amount" in first_month
            assert "points_earned" in first_month
            
            # 验证数据合理性
            assert isinstance(first_month["transaction_count"], int)
            assert float(first_month["expense_amount"]) >= 0
            assert float(first_month["payment_amount"]) >= 0
        
        logger.info("✅ 月度趋势获取成功")

    def test_08_get_bank_statistics_success(self):
        """测试获取银行统计（成功）"""
        response = self.client.get("/api/statistics/banks", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证银行统计结构
        assert isinstance(data, list)
        if data:
            first_bank = data[0]
            assert "bank_name" in first_bank
            assert "card_count" in first_bank
            assert "total_credit_limit" in first_bank
            assert "total_used_amount" in first_bank
            assert "utilization_rate" in first_bank
            
            # 验证数据合理性
            assert isinstance(first_bank["card_count"], int)
            assert first_bank["card_count"] > 0
            assert float(first_bank["total_credit_limit"]) >= 0
        
        logger.info("✅ 银行统计获取成功")

    # ==================== 查询参数筛选测试 ====================
    
    def test_09_overview_with_date_filter(self):
        """测试带日期筛选的统计概览"""
        start_date = "2024-06-01"
        end_date = "2024-06-30"
        
        response = self.client.get(
            f"/api/statistics/overview?start_date={start_date}&end_date={end_date}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回数据结构正确
        assert "transaction_stats" in data
        assert "monthly_trends" in data
        
        logger.info("✅ 带日期筛选的统计概览获取成功")

    def test_10_overview_with_bank_filter(self):
        """测试带银行筛选的统计概览"""
        bank_name = "统计测试银行"
        
        response = self.client.get(
            f"/api/statistics/overview?bank_name={bank_name}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回数据结构正确
        assert "card_stats" in data
        assert "bank_distribution" in data
        
        logger.info("✅ 带银行筛选的统计概览获取成功")

    def test_11_overview_with_card_filter(self):
        """测试带信用卡筛选的统计概览"""
        response = self.client.get(
            f"/api/statistics/overview?card_id={self.card_id}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回数据结构正确
        assert "transaction_stats" in data
        
        logger.info("✅ 带信用卡筛选的统计概览获取成功")

    def test_12_transactions_with_date_range(self):
        """测试带日期范围的交易统计"""
        start_date = "2024-06-01"
        end_date = "2024-12-31"
        
        response = self.client.get(
            f"/api/statistics/transactions?start_date={start_date}&end_date={end_date}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证统计数据合理
        assert "total_transactions" in data
        assert isinstance(data["total_transactions"], int)
        
        logger.info("✅ 带日期范围的交易统计获取成功")

    def test_13_categories_with_limit(self):
        """测试带数量限制的分类统计"""
        limit = 5
        
        response = self.client.get(
            f"/api/statistics/categories?limit={limit}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回的分类数量不超过限制
        assert isinstance(data, list)
        assert len(data) <= limit
        
        logger.info("✅ 带数量限制的分类统计获取成功")

    def test_14_cards_with_include_cancelled(self):
        """测试包含已注销卡片的信用卡统计"""
        response = self.client.get(
            "/api/statistics/cards?include_cancelled=true",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证统计数据包含已注销卡片
        assert "total_cards" in data
        assert "cancelled_cards" in data
        
        logger.info("✅ 包含已注销卡片的统计获取成功")

    # ==================== 边界条件测试 ====================
    
    def test_15_invalid_date_format(self):
        """测试无效日期格式"""
        response = self.client.get(
            "/api/statistics/overview?start_date=invalid-date",
            headers=self.headers
        )
        
        # 应该返回400错误或者忽略无效参数
        assert response.status_code in [200, 400, 422]
        
        logger.info("✅ 无效日期格式处理验证成功")

    def test_16_future_date_range(self):
        """测试未来日期范围"""
        start_date = "2030-01-01"
        end_date = "2030-12-31"
        
        response = self.client.get(
            f"/api/statistics/overview?start_date={start_date}&end_date={end_date}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 未来日期应该返回空数据或零值
        assert "transaction_stats" in data
        
        logger.info("✅ 未来日期范围处理验证成功")

    def test_17_invalid_card_id_filter(self):
        """测试无效信用卡ID筛选"""
        invalid_card_id = str(uuid4())
        
        response = self.client.get(
            f"/api/statistics/overview?card_id={invalid_card_id}",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 无效卡片ID应该返回空数据或零值
        assert "card_stats" in data
        
        logger.info("✅ 无效信用卡ID筛选处理验证成功")

    def test_18_large_limit_value(self):
        """测试超大限制值"""
        response = self.client.get(
            "/api/statistics/categories?limit=1000",
            headers=self.headers
        )
        
        # 应该被限制在合理范围内或返回错误
        assert response.status_code in [200, 400, 422]
        
        logger.info("✅ 超大限制值处理验证成功")

    def test_19_negative_limit_value(self):
        """测试负数限制值"""
        response = self.client.get(
            "/api/statistics/categories?limit=-1",
            headers=self.headers
        )
        
        # 应该返回400验证错误
        assert response.status_code in [400, 422]
        
        logger.info("✅ 负数限制值验证成功")

    def test_20_empty_bank_name_filter(self):
        """测试空银行名称筛选"""
        response = self.client.get(
            "/api/statistics/overview?bank_name=",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 空银行名称应该被忽略或返回所有数据
        assert "bank_distribution" in data
        
        logger.info("✅ 空银行名称筛选处理验证成功")

    # ==================== 权限和安全测试 ====================
    
    def test_21_unauthorized_access(self):
        """测试未授权访问"""
        response = self.client.get("/api/statistics/overview")
        assert response.status_code == 403
        
        logger.info("✅ 未授权访问验证成功")

    def test_22_invalid_token_access(self):
        """测试无效令牌访问"""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/statistics/overview", headers=invalid_headers)
        assert response.status_code in [401, 403]
        
        logger.info("✅ 无效令牌访问验证成功")

    def test_23_data_isolation_verification(self):
        """测试数据隔离验证"""
        # 创建另一个用户
        other_user = self.api_test.setup_test_user()
        other_headers = {"Authorization": f"Bearer {other_user['token']}"}
        
        # 获取当前用户的统计
        response1 = self.client.get("/api/statistics/overview", headers=self.headers)
        data1 = self.api_test.assert_api_success(response1, 200)
        
        # 获取其他用户的统计  
        response2 = self.client.get("/api/statistics/overview", headers=other_headers)
        data2 = self.api_test.assert_api_success(response2, 200)
        
        # 验证数据不同（其他用户没有我们的测试卡）
        assert data1["card_stats"]["total_cards"] >= 1
        assert data2["card_stats"]["total_cards"] == 0
        
        logger.info("✅ 数据隔离验证成功")

    # ==================== 性能和响应测试 ====================
    
    def test_24_overview_response_time(self):
        """测试统计概览响应时间"""
        start_time = time.time()
        response = self.client.get("/api/statistics/overview", headers=self.headers)
        response_time = time.time() - start_time
        
        self.api_test.assert_api_success(response, 200)
        assert response_time < 3.0  # 统计概览应在3秒内响应
        
        logger.info(f"✅ 统计概览响应时间: {response_time:.3f}秒")

    def test_25_concurrent_statistics_requests(self):
        """测试并发统计请求"""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def make_request():
            try:
                response = self.client.get("/api/statistics/overview", headers=self.headers)
                result_queue.put(response.status_code)
            except Exception as e:
                result_queue.put(f"error: {str(e)}")
        
        # 创建5个并发请求
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        success_count = 0
        while not result_queue.empty():
            result = result_queue.get()
            if result == 200:
                success_count += 1
        
        # 至少80%的请求应该成功
        assert success_count >= 4
        
        logger.info(f"✅ 并发统计请求测试: {success_count}/5 成功")

    def test_26_complex_filter_combination(self):
        """测试复杂筛选条件组合"""
        response = self.client.get(
            f"/api/statistics/overview?start_date=2024-01-01&end_date=2024-12-31&bank_name=统计测试银行&include_cancelled=false",
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证复杂筛选仍能正常工作
        assert "card_stats" in data
        assert "transaction_stats" in data
        
        logger.info("✅ 复杂筛选条件组合测试成功")

    def test_27_statistics_data_consistency(self):
        """测试统计数据一致性"""
        # 获取各项独立统计
        card_response = self.client.get("/api/statistics/cards", headers=self.headers)
        card_data = self.api_test.assert_api_success(card_response, 200)
        
        transaction_response = self.client.get("/api/statistics/transactions", headers=self.headers)
        transaction_data = self.api_test.assert_api_success(transaction_response, 200)
        
        # 获取总体统计
        overview_response = self.client.get("/api/statistics/overview", headers=self.headers)
        overview_data = self.api_test.assert_api_success(overview_response, 200)
        
        # 验证数据一致性
        assert overview_data["card_stats"]["total_cards"] == card_data["total_cards"]
        assert overview_data["transaction_stats"]["total_transactions"] == transaction_data["total_transactions"]
        
        logger.info("✅ 统计数据一致性验证成功")

    def test_28_all_endpoints_accessibility(self):
        """测试所有统计接口可访问性"""
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
        
        failed_endpoints = []
        
        for endpoint in endpoints:
            try:
                response = self.client.get(endpoint, headers=self.headers)
                if response.status_code != 200:
                    failed_endpoints.append(f"{endpoint}: {response.status_code}")
            except Exception as e:
                failed_endpoints.append(f"{endpoint}: {str(e)}")
        
        if failed_endpoints:
            logger.warning(f"部分接口访问失败: {failed_endpoints}")
        
        # 大部分接口应该可以正常访问
        success_rate = (len(endpoints) - len(failed_endpoints)) / len(endpoints)
        assert success_rate >= 0.8  # 至少80%的接口应该正常
        
        logger.info(f"✅ 统计接口可访问性测试: {success_rate*100:.1f}% 成功")

    def test_29_statistics_with_no_data(self):
        """测试无数据时的统计响应"""
        # 创建一个新用户（没有任何数据）
        new_user = self.api_test.setup_test_user()
        new_headers = {"Authorization": f"Bearer {new_user['token']}"}
        
        response = self.client.get("/api/statistics/overview", headers=new_headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证无数据时的默认值
        assert data["card_stats"]["total_cards"] == 0
        assert float(data["transaction_stats"]["total_expense_amount"]) == 0
        assert len(data["top_categories"]) == 0
        
        logger.info("✅ 无数据统计响应验证成功")

    def test_30_statistics_error_handling(self):
        """测试统计功能错误处理"""
        # 测试格式错误的参数
        test_cases = [
            "/api/statistics/categories?limit=abc",  # 非数字limit
            "/api/statistics/overview?start_date=2024-13-45",  # 无效日期
            "/api/statistics/transactions?card_id=invalid-uuid"  # 无效UUID格式
        ]
        
        for endpoint in test_cases:
            response = self.client.get(endpoint, headers=self.headers)
            # 应该返回400或422错误，或者200但处理了错误
            assert response.status_code in [200, 400, 422]
        
        logger.info("✅ 统计功能错误处理验证成功") 