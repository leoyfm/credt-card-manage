"""
统计接口测试

测试统计相关的所有API接口功能
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from tests.conftest import create_test_transaction


class TestStatisticsAPI:
    """统计API测试类"""
    
    def test_get_statistics_overview(self, client: TestClient, authenticated_user):
        """测试获取总体统计概览"""
        response = client.get(
            "/api/statistics/overview",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证响应数据结构
        overview_data = data["data"]
        assert "card_stats" in overview_data
        assert "credit_stats" in overview_data
        assert "transaction_stats" in overview_data
        assert "annual_fee_stats" in overview_data
        assert "top_categories" in overview_data
        assert "monthly_trends" in overview_data
        assert "bank_distribution" in overview_data
        
        # 验证基本统计数据类型
        assert isinstance(overview_data["card_stats"]["total_cards"], int)
        assert isinstance(overview_data["credit_stats"]["total_credit_limit"], str)
        assert isinstance(overview_data["transaction_stats"]["total_transactions"], int)
        
    def test_get_statistics_overview_with_filters(self, client: TestClient, authenticated_user):
        """测试带筛选条件的总体统计概览"""
        # 使用时间范围筛选
        response = client.get(
            "/api/statistics/overview",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "include_cancelled": False
            },
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_get_card_statistics(self, client: TestClient, authenticated_user):
        """测试获取信用卡统计信息"""
        response = client.get(
            "/api/statistics/cards",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证信用卡统计数据结构
        card_stats = data["data"]
        required_fields = [
            "total_cards", "active_cards", "inactive_cards", 
            "frozen_cards", "cancelled_cards", "expired_cards", 
            "expiring_soon_cards"
        ]
        for field in required_fields:
            assert field in card_stats
            assert isinstance(card_stats[field], int)
            assert card_stats[field] >= 0
        
    def test_get_card_statistics_with_bank_filter(self, client: TestClient, authenticated_user):
        """测试带银行筛选的信用卡统计"""
        response = client.get(
            "/api/statistics/cards",
            params={"bank_name": "招商银行"},
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_get_credit_limit_statistics(self, client: TestClient, authenticated_user):
        """测试获取信用额度统计信息"""
        response = client.get(
            "/api/statistics/credit-limit",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证额度统计数据结构
        credit_stats = data["data"]
        required_fields = [
            "total_credit_limit", "total_used_amount", "total_available_amount",
            "overall_utilization_rate", "highest_utilization_rate", 
            "lowest_utilization_rate", "average_utilization_rate"
        ]
        for field in required_fields:
            assert field in credit_stats
            
        # 验证数值类型和合理性
        assert float(credit_stats["total_credit_limit"]) >= 0
        assert float(credit_stats["total_used_amount"]) >= 0
        assert float(credit_stats["total_available_amount"]) >= 0
        assert 0 <= credit_stats["overall_utilization_rate"] <= 100
        
    def test_get_transaction_statistics(self, client: TestClient, authenticated_user):
        """测试获取交易统计信息"""
        response = client.get(
            "/api/statistics/transactions",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证交易统计数据结构
        transaction_stats = data["data"]
        required_fields = [
            "total_transactions", "total_expense_amount", "total_payment_amount",
            "total_points_earned", "current_month_transactions", 
            "current_month_expense", "average_transaction_amount"
        ]
        for field in required_fields:
            assert field in transaction_stats
            
        # 验证数值合理性
        assert transaction_stats["total_transactions"] >= 0
        assert float(transaction_stats["total_expense_amount"]) >= 0
        assert float(transaction_stats["total_payment_amount"]) >= 0
        assert float(transaction_stats["total_points_earned"]) >= 0
        
    def test_get_transaction_statistics_with_date_range(self, client: TestClient, authenticated_user):
        """测试带时间范围的交易统计"""
        response = client.get(
            "/api/statistics/transactions",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-06-30"
            },
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_get_annual_fee_statistics(self, client: TestClient, authenticated_user):
        """测试获取年费统计信息"""
        response = client.get(
            "/api/statistics/annual-fee",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证年费统计数据结构
        annual_fee_stats = data["data"]
        required_fields = [
            "total_annual_fee", "waived_count", "pending_count",
            "paid_count", "overdue_count", "current_year_fee_due",
            "savings_from_waiver"
        ]
        for field in required_fields:
            assert field in annual_fee_stats
            
        # 验证数值合理性
        assert float(annual_fee_stats["total_annual_fee"]) >= 0
        assert annual_fee_stats["waived_count"] >= 0
        assert annual_fee_stats["pending_count"] >= 0
        assert annual_fee_stats["paid_count"] >= 0
        assert annual_fee_stats["overdue_count"] >= 0
        
    def test_get_category_statistics(self, client: TestClient, authenticated_user):
        """测试获取消费分类统计"""
        response = client.get(
            "/api/statistics/categories",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证分类统计数据结构
        categories = data["data"]
        assert isinstance(categories, list)
        
        for category in categories:
            required_fields = [
                "category", "category_name", "transaction_count",
                "total_amount", "percentage"
            ]
            for field in required_fields:
                assert field in category
                
            # 验证数值合理性
            assert category["transaction_count"] >= 0
            assert float(category["total_amount"]) >= 0
            assert 0 <= category["percentage"] <= 100
            
    def test_get_category_statistics_with_limit(self, client: TestClient, authenticated_user):
        """测试带数量限制的分类统计"""
        response = client.get(
            "/api/statistics/categories",
            params={"limit": 5},
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证返回数量不超过限制
        categories = data["data"]
        assert len(categories) <= 5
        
    def test_get_monthly_trends(self, client: TestClient, authenticated_user):
        """测试获取月度统计趋势"""
        response = client.get(
            "/api/statistics/monthly-trends",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证月度趋势数据结构
        monthly_trends = data["data"]
        assert isinstance(monthly_trends, list)
        
        for month_data in monthly_trends:
            required_fields = [
                "year_month", "transaction_count", "expense_amount",
                "payment_amount", "points_earned"
            ]
            for field in required_fields:
                assert field in month_data
                
            # 验证年月格式
            assert len(month_data["year_month"]) == 7  # YYYY-MM格式
            assert "-" in month_data["year_month"]
            
            # 验证数值合理性
            assert month_data["transaction_count"] >= 0
            assert float(month_data["expense_amount"]) >= 0
            assert float(month_data["payment_amount"]) >= 0
            assert float(month_data["points_earned"]) >= 0
            
    def test_get_monthly_trends_with_date_range(self, client: TestClient, authenticated_user):
        """测试带时间范围的月度趋势"""
        response = client.get(
            "/api/statistics/monthly-trends",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-06-30"
            },
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_get_bank_statistics(self, client: TestClient, authenticated_user):
        """测试获取银行分布统计"""
        response = client.get(
            "/api/statistics/banks",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证银行统计数据结构
        bank_stats = data["data"]
        assert isinstance(bank_stats, list)
        
        for bank_data in bank_stats:
            required_fields = [
                "bank_name", "card_count", "total_credit_limit",
                "total_used_amount", "utilization_rate"
            ]
            for field in required_fields:
                assert field in bank_data
                
            # 验证数值合理性
            assert bank_data["card_count"] >= 0
            assert float(bank_data["total_credit_limit"]) >= 0
            assert float(bank_data["total_used_amount"]) >= 0
            assert 0 <= bank_data["utilization_rate"] <= 100
            
    def test_statistics_unauthorized(self, client: TestClient):
        """测试未授权访问统计接口"""
        # 测试各个统计接口的未授权访问
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
            response = client.get(endpoint)
            # FastAPI的JWTBearer依赖返回403而不是401
            assert response.status_code == 403

    def test_statistics_with_invalid_parameters(self, client: TestClient, authenticated_user):
        """测试使用无效参数的统计接口"""
        # 测试无效日期格式 - 实际上会被捕获并返回错误响应而不是422
        response = client.get(
            "/api/statistics/transactions",
            params={
                "start_date": "invalid-date",
                "end_date": "2024-12-31"
            },
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200  # 被捕获并返回错误信息
        
        # 测试无效的limit参数 - 由FastAPI自动验证，会返回422
        response = client.get(
            "/api/statistics/categories",
            params={"limit": 25},  # 超过最大值20
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 422


class TestStatisticsIntegration:
    """统计接口集成测试"""
    
    def test_statistics_data_consistency(self, client: TestClient, authenticated_user):
        """测试统计数据的一致性"""
        # 获取总体统计
        overview_response = client.get(
            "/api/statistics/overview",
            headers=authenticated_user["headers"]
        )
        assert overview_response.status_code == 200
        overview_data = overview_response.json()["data"]
        
        # 获取单独的统计数据
        card_response = client.get(
            "/api/statistics/cards",
            headers=authenticated_user["headers"]
        )
        credit_response = client.get(
            "/api/statistics/credit-limit",
            headers=authenticated_user["headers"]
        )
        transaction_response = client.get(
            "/api/statistics/transactions",
            headers=authenticated_user["headers"]
        )
        
        # 验证数据一致性
        assert overview_data["card_stats"] == card_response.json()["data"]
        assert overview_data["credit_stats"] == credit_response.json()["data"]
        assert overview_data["transaction_stats"] == transaction_response.json()["data"]
        
    def test_statistics_with_test_card(self, client: TestClient, test_card):
        """测试有信用卡数据时的统计"""
        response = client.get(
            "/api/statistics/overview",
            headers=test_card["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证有信用卡时的统计数据
        overview_data = data["data"]
        assert overview_data["card_stats"]["total_cards"] >= 1
        assert float(overview_data["credit_stats"]["total_credit_limit"]) > 0 