"""
交易接口测试

测试交易记录相关的所有API接口。
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
from fastapi.testclient import TestClient
from uuid import uuid4

from tests.conftest import create_test_transaction, assert_response_success, assert_response_error


class TestTransactionCRUD:
    """交易CRUD操作测试"""

    def test_create_transaction_success(
        self, client: TestClient, authenticated_user: Dict[str, Any], 
        test_card: Dict[str, Any], test_transaction_data: Dict[str, Any]
    ):
        """测试创建交易记录成功"""
        test_transaction_data["card_id"] = test_card["id"]
        
        response = client.post(
            "/api/transactions/",
            json=test_transaction_data,
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response, 200)
        
        # 验证返回数据
        assert data["card_id"] == test_card["id"]
        assert data["transaction_type"] == test_transaction_data["transaction_type"]
        assert float(data["amount"]) == test_transaction_data["amount"]
        assert data["merchant_name"] == test_transaction_data["merchant_name"]
        assert data["category"] == test_transaction_data["category"]
        assert data["status"] == test_transaction_data["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_transaction_invalid_card(
        self, client: TestClient, authenticated_user: Dict[str, Any], 
        test_transaction_data: Dict[str, Any]
    ):
        """测试创建交易记录时信用卡ID无效"""
        test_transaction_data["card_id"] = str(uuid4())
        
        response = client.post(
            "/api/transactions/",
            json=test_transaction_data,
            headers=authenticated_user["headers"]
        )
        
        assert_response_error(response, 500)  # 无效卡ID导致服务器错误

    def test_create_transaction_missing_required_fields(
        self, client: TestClient, authenticated_user: Dict[str, Any]
    ):
        """测试创建交易记录时缺少必填字段"""
        incomplete_data = {
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00"
        }
        
        response = client.post(
            "/api/transactions/",
            json=incomplete_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # 验证错误

    def test_create_transaction_invalid_amount(
        self, client: TestClient, authenticated_user: Dict[str, Any],
        test_card: Dict[str, Any], test_transaction_data: Dict[str, Any]
    ):
        """测试创建交易记录时金额无效"""
        test_transaction_data["card_id"] = test_card["id"]
        test_transaction_data["amount"] = -100.00  # 负数金额
        
        response = client.post(
            "/api/transactions/",
            json=test_transaction_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # 验证错误

    def test_get_transactions_list(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试获取交易记录列表"""
        # 创建几条测试交易记录
        for i in range(3):
            create_test_transaction(
                client, 
                authenticated_user["headers"], 
                test_card["id"],
                {
                    "transaction_type": "expense",
                    "amount": 100.00 + i * 50,
                    "transaction_date": "2024-06-08T14:30:00",
                    "merchant_name": f"测试商户{i+1}",
                    "description": f"测试交易{i+1}",
                    "category": "dining",
                    "status": "completed"
                }
            )
        
        response = client.get(
            "/api/transactions/",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        
        # 验证分页结构
        assert "items" in data
        assert "pagination" in data
        assert len(data["items"]) == 3
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["current_page"] == 1
        assert data["pagination"]["page_size"] == 20

    def test_get_transactions_with_filters(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试带筛选条件的交易记录列表"""
        # 创建不同类型的交易记录
        create_test_transaction(client, authenticated_user["headers"], test_card["id"], {
            "transaction_type": "expense",
            "amount": 200.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "星巴克",
            "category": "dining",
            "status": "completed"
        })
        
        create_test_transaction(client, authenticated_user["headers"], test_card["id"], {
            "transaction_type": "expense",
            "amount": 500.00,
            "transaction_date": "2024-06-08T15:30:00",
            "merchant_name": "苹果商店",
            "category": "shopping",
            "status": "completed"
        })
        
        # 测试按分类筛选
        response = client.get(
            "/api/transactions/?category=dining",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert len(data["items"]) == 1
        assert data["items"][0]["category"] == "dining"
        
        # 测试按金额范围筛选
        response = client.get(
            "/api/transactions/?min_amount=300&max_amount=600",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert len(data["items"]) == 1
        assert float(data["items"][0]["amount"]) == 500.00

    def test_get_transactions_with_keyword_search(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试关键词搜索交易记录"""
        create_test_transaction(client, authenticated_user["headers"], test_card["id"], {
            "transaction_type": "expense",
            "amount": 200.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "星巴克咖啡",
            "description": "购买咖啡",
            "category": "dining",
            "status": "completed"
        })
        
        # 搜索商户名称
        response = client.get(
            "/api/transactions/?keyword=星巴克",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert len(data["items"]) == 1
        assert "星巴克" in data["items"][0]["merchant_name"]

    def test_get_transaction_detail(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试获取交易记录详情"""
        transaction = create_test_transaction(
            client, authenticated_user["headers"], test_card["id"]
        )
        
        response = client.get(
            f"/api/transactions/{transaction['id']}",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert data["id"] == transaction["id"]
        assert data["card_id"] == test_card["id"]

    def test_get_transaction_not_found(
        self, client: TestClient, authenticated_user: Dict[str, Any]
    ):
        """测试获取不存在的交易记录"""
        fake_id = uuid4()
        response = client.get(
            f"/api/transactions/{fake_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False

    def test_update_transaction(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试更新交易记录"""
        transaction = create_test_transaction(
            client, authenticated_user["headers"], test_card["id"]
        )
        
        update_data = {
            "amount": 250.00,
            "merchant_name": "更新后的商户",
            "description": "更新后的描述",
            "category": "shopping"
        }
        
        response = client.put(
            f"/api/transactions/{transaction['id']}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert float(data["amount"]) == 250.00
        assert data["merchant_name"] == "更新后的商户"
        assert data["description"] == "更新后的描述"
        assert data["category"] == "shopping"

    def test_update_transaction_not_found(
        self, client: TestClient, authenticated_user: Dict[str, Any]
    ):
        """测试更新不存在的交易记录"""
        fake_id = uuid4()
        update_data = {"amount": 250.00}
        
        response = client.put(
            f"/api/transactions/{fake_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False

    def test_delete_transaction(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试删除交易记录"""
        transaction = create_test_transaction(
            client, authenticated_user["headers"], test_card["id"]
        )
        
        response = client.delete(
            f"/api/transactions/{transaction['id']}",
            headers=authenticated_user["headers"]
        )
        
        assert_response_success(response)
        
        # 验证交易记录已被删除
        response = client.get(
            f"/api/transactions/{transaction['id']}",
            headers=authenticated_user["headers"]
        )
        
        result = response.json()
        assert result["success"] is False

    def test_delete_transaction_not_found(
        self, client: TestClient, authenticated_user: Dict[str, Any]
    ):
        """测试删除不存在的交易记录"""
        fake_id = uuid4()
        
        response = client.delete(
            f"/api/transactions/{fake_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False


class TestTransactionStatistics:
    """交易统计接口测试"""

    def test_get_transaction_statistics(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试获取交易统计概览"""
        # 创建多条不同类型的交易记录
        transactions = [
            {"transaction_type": "expense", "amount": 200.00, "category": "dining"},
            {"transaction_type": "expense", "amount": 500.00, "category": "shopping"},
            {"transaction_type": "payment", "amount": 1000.00, "category": "other"},
            {"transaction_type": "refund", "amount": 50.00, "category": "shopping"},
        ]
        
        for trans in transactions:
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], trans
            )
        
        response = client.get(
            "/api/transactions/statistics/overview",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        
        # 验证统计数据结构
        assert "total_transactions" in data
        assert "total_amount" in data
        assert "expense_amount" in data
        assert "income_amount" in data
        assert "points_earned" in data
        assert data["total_transactions"] == 4

    def test_get_category_statistics(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试获取分类消费统计"""
        # 创建不同分类的交易记录
        categories = ["dining", "shopping", "transport"]
        for i, category in enumerate(categories):
            for j in range(2):  # 每个分类创建2条记录
                create_test_transaction(
                    client, authenticated_user["headers"], test_card["id"], {
                        "transaction_type": "expense",
                        "amount": 100.00 * (i + 1),
                        "category": category
                    }
                )
        
        response = client.get(
            "/api/transactions/statistics/categories",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        
        # 验证分类统计数据
        assert isinstance(data, list)
        assert len(data) >= 3  # 至少有3个分类
        
        for category_stat in data:
            assert "category" in category_stat
            assert "category_display" in category_stat
            assert "transaction_count" in category_stat
            assert "total_amount" in category_stat
            assert "average_amount" in category_stat
            assert "percentage" in category_stat

    def test_get_monthly_trend(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试获取月度交易趋势"""
        # 创建不同月份的交易记录
        months = ["2024-01-15", "2024-02-15", "2024-03-15"]
        for month in months:
            for i in range(2):  # 每个月创建2条记录
                create_test_transaction(
                    client, authenticated_user["headers"], test_card["id"], {
                        "transaction_type": "expense",
                        "amount": 200.00,
                        "transaction_date": f"{month}T14:30:00"
                    }
                )
        
        response = client.get(
            "/api/transactions/statistics/monthly-trend?year=2024",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        
        # 验证月度趋势数据
        assert isinstance(data, list)
        
        for trend in data:
            assert "year" in trend
            assert "month" in trend
            assert "transaction_count" in trend
            assert "total_amount" in trend
            assert "expense_amount" in trend
            assert "income_amount" in trend
            assert trend["year"] == 2024


class TestTransactionAuth:
    """交易接口权限测试"""

    def test_create_transaction_without_auth(self, client: TestClient, test_transaction_data: Dict[str, Any]):
        """测试未认证时创建交易记录"""
        response = client.post("/api/transactions/", json=test_transaction_data)
        assert response.status_code in [401, 403]  # 可能返回401或403

    def test_get_transactions_without_auth(self, client: TestClient):
        """测试未认证时获取交易记录列表"""
        response = client.get("/api/transactions/")
        assert response.status_code in [401, 403]  # 可能返回401或403

    def test_get_transaction_detail_without_auth(self, client: TestClient):
        """测试未认证时获取交易记录详情"""
        fake_id = uuid4()
        response = client.get(f"/api/transactions/{fake_id}")
        assert response.status_code in [401, 403]  # 可能返回401或403

    def test_update_transaction_without_auth(self, client: TestClient):
        """测试未认证时更新交易记录"""
        fake_id = uuid4()
        response = client.put(f"/api/transactions/{fake_id}", json={"amount": 100.00})
        assert response.status_code in [401, 403]  # 可能返回401或403

    def test_delete_transaction_without_auth(self, client: TestClient):
        """测试未认证时删除交易记录"""
        fake_id = uuid4()
        response = client.delete(f"/api/transactions/{fake_id}")
        assert response.status_code in [401, 403]  # 可能返回401或403

    def test_statistics_without_auth(self, client: TestClient):
        """测试未认证时获取统计信息"""
        endpoints = [
            "/api/transactions/statistics/overview",
            "/api/transactions/statistics/categories",
            "/api/transactions/statistics/monthly-trend"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403]  # 可能返回401或403


class TestTransactionEdgeCases:
    """交易接口边界情况测试"""

    def test_create_installment_transaction(
        self, client: TestClient, authenticated_user: Dict[str, Any], 
        test_card: Dict[str, Any], test_transaction_data: Dict[str, Any]
    ):
        """测试创建分期交易记录"""
        test_transaction_data["card_id"] = test_card["id"]
        test_transaction_data["is_installment"] = True
        test_transaction_data["installment_count"] = 12
        test_transaction_data["amount"] = 3000.00
        
        response = client.post(
            "/api/transactions/",
            json=test_transaction_data,
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response, 200)
        assert data["is_installment"] is True
        assert data["installment_count"] == 12

    def test_create_transaction_large_amount(
        self, client: TestClient, authenticated_user: Dict[str, Any], 
        test_card: Dict[str, Any], test_transaction_data: Dict[str, Any]
    ):
        """测试创建大金额交易记录"""
        test_transaction_data["card_id"] = test_card["id"]
        test_transaction_data["amount"] = 99999.99
        
        response = client.post(
            "/api/transactions/",
            json=test_transaction_data,
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response, 200)
        assert float(data["amount"]) == 99999.99

    def test_get_transactions_pagination(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试交易记录分页"""
        # 创建25条交易记录
        for i in range(25):
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], {
                    "transaction_type": "expense",
                    "amount": 100.00 + i,
                    "merchant_name": f"商户{i+1}"
                }
            )
        
        # 测试第一页
        response = client.get(
            "/api/transactions/?page=1&page_size=10",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert len(data["items"]) == 10
        assert data["pagination"]["current_page"] == 1
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["total_pages"] == 3
        
        # 测试第二页
        response = client.get(
            "/api/transactions/?page=2&page_size=10",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert len(data["items"]) == 10
        assert data["pagination"]["current_page"] == 2

    def test_statistics_with_date_range(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试带时间范围的统计"""
        # 创建不同时间的交易记录
        dates = ["2024-01-15T14:30:00", "2024-06-15T14:30:00", "2024-12-15T14:30:00"]
        for date in dates:
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], {
                    "transaction_type": "expense",
                    "amount": 200.00,
                    "transaction_date": date
                }
            )
        
        # 测试指定时间范围的统计
        response = client.get(
            "/api/transactions/statistics/overview?start_date=2024-06-01T00:00:00&end_date=2024-06-30T23:59:59",
            headers=authenticated_user["headers"]
        )
        
        data = assert_response_success(response)
        assert data["total_transactions"] == 1 