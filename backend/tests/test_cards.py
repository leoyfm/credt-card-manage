"""
信用卡接口测试

测试信用卡相关的API接口，包括：
- 信用卡CRUD操作
- 年费管理集成测试  
- 认证和权限测试
- 边界情况和错误处理
- 分页和搜索功能
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from typing import Dict, Any


class TestCardCRUD:
    """测试信用卡CRUD操作"""

    def test_create_card_success(self, client: TestClient, authenticated_user: Dict[str, Any], test_card_data: Dict[str, Any]):
        """测试成功创建信用卡"""
        response = client.post(
            "/api/cards/",
            json=test_card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["message"] == "创建信用卡成功"
        
        # 验证返回的信用卡数据
        card = result["data"]
        assert card["card_name"] == test_card_data["card_name"]
        assert card["bank_name"] == test_card_data["bank_name"]
        assert card["card_number"] == test_card_data["card_number"]
        assert card["card_type"] == test_card_data["card_type"]
        assert float(card["credit_limit"]) == test_card_data["credit_limit"]
        assert card["expiry_month"] == test_card_data["expiry_month"]
        assert card["expiry_year"] == test_card_data["expiry_year"]
        assert card["billing_day"] == test_card_data["billing_day"]
        assert card["due_day"] == test_card_data["due_day"]

    def test_create_card_with_annual_fee(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试创建带年费管理的信用卡"""
        card_data = {
            "card_name": "招商银行经典白金卡",
            "bank_name": "招商银行", 
            "card_number": "6225881234567890",
            "card_type": "visa",
            "credit_limit": 100000.00,
            "expiry_month": 12,
            "expiry_year": 2027,
            "billing_day": 5,
            "due_day": 25,
            "used_amount": 0.0,
            "annual_fee_enabled": True,
            "fee_type": "transaction_count",
            "base_fee": 200.00,
            "waiver_condition_value": 12,
            "annual_fee_month": 3,
            "annual_fee_day": 15,
            "fee_description": "年内刷卡满12次可减免年费"
        }
        
        response = client.post(
            "/api/cards/",
            json=card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        # 验证年费规则
        card = result["data"]
        assert card["has_annual_fee"] is True

    def test_get_cards_list(self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]):
        """测试获取信用卡列表"""
        response = client.get(
            "/api/cards/",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "items" in result["data"]
        assert "pagination" in result["data"]
        
        # 验证分页信息
        pagination = result["data"]["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 20
        assert pagination["total"] >= 1

    def test_get_card_detail(self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]):
        """测试获取信用卡详情"""
        card_id = test_card["id"]
        
        response = client.get(
            f"/api/cards/{card_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["id"] == card_id
        assert result["data"]["card_name"] == test_card["card_name"]

    def test_update_card(self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]):
        """测试更新信用卡信息"""
        card_id = test_card["id"]
        update_data = {
            "card_name": "更新后的卡片名称",
            "credit_limit": 80000.00,
            "used_amount": 15000.00
        }
        
        response = client.put(
            f"/api/cards/{card_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        # 验证更新后的数据
        updated_card = result["data"]
        assert updated_card["card_name"] == update_data["card_name"]
        assert float(updated_card["credit_limit"]) == update_data["credit_limit"]
        assert float(updated_card["used_amount"]) == update_data["used_amount"]

    def test_delete_card(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试删除信用卡"""
        # 先创建一张信用卡
        card_data = {
            "card_name": "待删除的测试卡片",
            "bank_name": "测试银行",
            "card_number": "9876543210123456",
            "card_type": "mastercard",
            "credit_limit": 30000.00,
            "expiry_month": 6,
            "expiry_year": 2026,
            "billing_day": 10,
            "due_day": 30,
            "used_amount": 0.0,
            "annual_fee_enabled": False
        }
        
        create_response = client.post(
            "/api/cards/",
            json=card_data,
            headers=authenticated_user["headers"]
        )
        assert create_response.status_code == 200
        card_id = create_response.json()["data"]["id"]
        
        # 删除信用卡
        delete_response = client.delete(
            f"/api/cards/{card_id}",
            headers=authenticated_user["headers"]
        )
        
        assert delete_response.status_code == 200
        result = delete_response.json()
        assert result["success"] is True
        assert "删除成功" in result["message"]


class TestCardAuth:
    """测试信用卡接口的认证和权限"""

    def test_create_card_without_auth(self, client: TestClient, test_card_data: Dict[str, Any]):
        """测试无认证创建信用卡"""
        response = client.post("/api/cards/", json=test_card_data)
        assert response.status_code == 403

    def test_get_cards_without_auth(self, client: TestClient):
        """测试无认证获取信用卡列表"""
        response = client.get("/api/cards/")
        assert response.status_code == 403

    def test_get_card_detail_without_auth(self, client: TestClient):
        """测试无认证获取信用卡详情"""
        card_id = str(uuid4())
        response = client.get(f"/api/cards/{card_id}")
        assert response.status_code == 403

    def test_update_card_without_auth(self, client: TestClient):
        """测试无认证更新信用卡"""
        card_id = str(uuid4())
        update_data = {"card_name": "更新测试"}
        response = client.put(f"/api/cards/{card_id}", json=update_data)
        assert response.status_code == 403

    def test_delete_card_without_auth(self, client: TestClient):
        """测试无认证删除信用卡"""
        card_id = str(uuid4())
        response = client.delete(f"/api/cards/{card_id}")
        assert response.status_code == 403


class TestCardValidation:
    """测试信用卡数据验证"""

    def test_create_card_missing_required_fields(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试创建信用卡缺少必需字段"""
        incomplete_data = {
            "card_name": "测试卡片",
            # 缺少必需的字段
        }
        
        response = client.post(
            "/api/cards/",
            json=incomplete_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_card_invalid_card_type(self, client: TestClient, authenticated_user: Dict[str, Any], test_card_data: Dict[str, Any]):
        """测试创建信用卡使用无效的卡片类型"""
        test_card_data["card_type"] = "invalid_type"
        
        response = client.post(
            "/api/cards/",
            json=test_card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_card_invalid_credit_limit(self, client: TestClient, authenticated_user: Dict[str, Any], test_card_data: Dict[str, Any]):
        """测试创建信用卡使用无效的信用额度"""
        test_card_data["credit_limit"] = -1000.00
        
        response = client.post(
            "/api/cards/",
            json=test_card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_card_invalid_expiry_date(self, client: TestClient, authenticated_user: Dict[str, Any], test_card_data: Dict[str, Any]):
        """测试创建信用卡使用无效的到期日期"""
        test_card_data["expiry_month"] = 13  # 无效月份
        
        response = client.post(
            "/api/cards/",
            json=test_card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_card_cross_month_due_day(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试跨月还款日（账单日晚于还款日的情况）"""
        import random
        # 生成唯一的纯数字信用卡号
        unique_suffix = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        unique_card_number = f"6225{unique_suffix}"
        
        card_data = {
            "card_name": "跨月还款测试卡",
            "bank_name": "测试银行",
            "card_number": unique_card_number,
            "card_type": "visa",
            "credit_limit": 50000.00,
            "expiry_month": 12,
            "expiry_year": 2027,
            "billing_day": 25,  # 每月25日出账单
            "due_day": 2,       # 次月2日还款
            "used_amount": 0.0,
            "annual_fee_enabled": True,
            "fee_type": "transaction_count",
            "base_fee": 200.00,
            "waiver_condition_value": 12,
            "annual_fee_month": 3,
            "annual_fee_day": 15,
            "fee_description": "年内刷卡满12次可减免年费"
        }
        
        response = client.post(
            "/api/cards/",
            json=card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        # 验证跨月还款日配置正确
        card = result["data"]
        assert card["billing_day"] == 25
        assert card["due_day"] == 2


class TestCardPagination:
    """测试信用卡分页和搜索"""

    def test_get_cards_with_pagination(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试分页获取信用卡列表"""
        response = client.get(
            "/api/cards/?page=1&page_size=5",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        pagination = result["data"]["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 5

    def test_get_cards_with_keyword_search(self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]):
        """测试关键词搜索信用卡"""
        response = client.get(
            "/api/cards/?keyword=测试",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_get_cards_with_large_page_size(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试使用超大页面大小"""
        response = client.get(
            "/api/cards/?page=1&page_size=1000",  # 超过最大限制100
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_cards_with_invalid_page(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试使用无效的页码"""
        response = client.get(
            "/api/cards/?page=0",  # 页码必须>=1
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error


class TestCardEdgeCases:
    """测试信用卡接口的边界情况"""

    def test_get_card_not_found(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试获取不存在的信用卡"""
        non_existent_id = str(uuid4())
        
        response = client.get(
            f"/api/cards/{non_existent_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "不存在" in result["message"]

    def test_update_card_not_found(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试更新不存在的信用卡"""
        non_existent_id = str(uuid4())
        update_data = {"card_name": "不存在的卡片"}
        
        response = client.put(
            f"/api/cards/{non_existent_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "不存在" in result["message"]

    def test_delete_card_not_found(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试删除不存在的信用卡"""
        non_existent_id = str(uuid4())
        
        response = client.delete(
            f"/api/cards/{non_existent_id}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "不存在" in result["message"]

    def test_update_card_invalid_uuid(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试使用无效的UUID格式"""
        invalid_id = "not-a-valid-uuid"
        update_data = {"card_name": "测试"}
        
        response = client.put(
            f"/api/cards/{invalid_id}",
            json=update_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 422  # Validation error


class TestCardBasicEndpoints:
    """测试信用卡基础接口（不含年费管理）"""

    def test_get_cards_basic(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试获取信用卡基础列表"""
        response = client.get(
            "/api/cards/basic",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "items" in result["data"]
        assert "pagination" in result["data"]

    def test_create_card_basic(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试创建基础信用卡（不含年费）"""
        card_data = {
            "card_name": "基础测试卡片",
            "bank_name": "测试银行",
            "card_number": "1111222233334444",
            "card_type": "unionpay",
            "credit_limit": 20000.00,
            "expiry_month": 8,
            "expiry_year": 2025,
            "billing_day": 15,
            "due_day": 25,
            "used_amount": 0.0
        }
        
        response = client.post(
            "/api/cards/basic",
            json=card_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["card_name"] == card_data["card_name"]


@pytest.mark.performance
class TestCardPerformance:
    """测试信用卡接口的性能表现"""

    def test_create_multiple_cards_performance(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试批量创建信用卡的性能"""
        import time
        
        start_time = time.time()
        created_cards = []
        
        # 创建5张信用卡进行性能测试
        for i in range(5):
            card_data = {
                "card_name": f"性能测试卡{i}",
                "bank_name": f"测试银行{i}",
                "card_number": f"1111{i:04d}22223333",
                "card_type": "visa",
                "credit_limit": 50000.00 + i * 10000,
                "expiry_month": 8,
                "expiry_year": 2025,
                "billing_day": 15,
                "due_day": 25,
                "used_amount": 0.0
            }
            
            response = client.post(
                "/api/cards/basic",
                json=card_data,
                headers=authenticated_user["headers"]
            )
            
            assert response.status_code == 200
            created_cards.append(response.json()["data"]["id"])
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 平均每张卡的创建时间应该在合理范围内（比如不超过2秒）
        avg_time_per_card = duration / 5
        assert avg_time_per_card < 2.0, f"创建单张信用卡平均耗时 {avg_time_per_card:.2f}s，性能不达标"

    def test_list_cards_performance(self, client: TestClient, authenticated_user: Dict[str, Any]):
        """测试列表查询性能"""
        import time
        
        # 测试获取信用卡列表的性能
        start_time = time.time()
        
        response = client.get(
            "/api/cards/?page=1&page_size=20",
            headers=authenticated_user["headers"]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        # 列表查询应该在1秒内完成
        assert duration < 1.0, f"信用卡列表查询耗时 {duration:.2f}s，性能不达标" 