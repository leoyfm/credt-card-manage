#!/usr/bin/env python3
"""
信用卡模块单元测试

测试信用卡相关的API接口，包括：
- 信用卡CRUD操作（基础版本和集成年费版本）
- 年费管理集成测试
- 认证和权限验证
- 数据验证和边界情况
- 分页和搜索功能
- 错误处理和异常情况
"""

import pytest
import uuid
from decimal import Decimal
from typing import Dict, Any
from tests.base_test import FastAPITestClient, BaseAPITest

# ==================== 测试数据生成器 ====================

class CardTestDataGenerator:
    """信用卡测试数据生成器"""
    
    @staticmethod
    def generate_test_card_data(suffix: str = "") -> Dict[str, Any]:
        """生成基础信用卡测试数据"""
        import time
        import random
        
        # 生成13位纯数字卡号
        timestamp = str(int(time.time() * 1000))[-7:]  # 取时间戳后7位
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        return {
            "bank_name": f"测试银行{suffix}",
            "card_name": f"测试信用卡{suffix}",
            "card_number": f"622588{timestamp}{random_digits}",  # 622588 + 7位时间戳 + 6位随机数 = 19位
            "card_type": "visa",
            "credit_limit": 50000.00,
            "used_amount": 3500.50,
            "billing_day": 5,
            "due_day": 25,
            "expiry_month": 10,
            "expiry_year": 2027,
            "card_color": "#1890ff",
            "status": "active",
            "is_active": True,
            "notes": f"测试备注{suffix}"
        }
    
    @staticmethod
    def generate_test_card_with_annual_fee_data(suffix: str = "") -> Dict[str, Any]:
        """生成包含年费的信用卡测试数据"""
        base_data = CardTestDataGenerator.generate_test_card_data(suffix)
        base_data.update({
            "annual_fee_enabled": True,
            "fee_type": "transaction_count",
            "base_fee": 200.00,
            "waiver_condition_value": 12,
            "annual_fee_month": 2,
            "annual_fee_day": 18,
            "fee_description": f"测试年费规则{suffix}"
        })
        return base_data


# ==================== 单元测试类 ====================

@pytest.mark.unit
class TestCardsUnit:
    """信用卡单元测试"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.user_headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        # 测试数据生成器
        self.data_gen = CardTestDataGenerator()
    
    # ==================== 基础信用卡CRUD测试 ====================
    
    def test_01_create_card_basic_success(self):
        """测试成功创建基础信用卡"""
        card_data = self.data_gen.generate_test_card_data("基础")
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回的信用卡数据
        assert data["card_name"] == card_data["card_name"]
        assert data["bank_name"] == card_data["bank_name"]
        assert data["card_number"] == card_data["card_number"]
        assert data["card_type"] == card_data["card_type"]
        assert float(data["credit_limit"]) == card_data["credit_limit"]
        assert data["expiry_month"] == card_data["expiry_month"]
        assert data["expiry_year"] == card_data["expiry_year"]
        assert data["billing_day"] == card_data["billing_day"]
        assert data["due_day"] == card_data["due_day"]
        assert data["status"] == card_data["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # 保存创建的卡片ID用于后续测试
        self.created_card_id = data["id"]
    
    def test_02_create_card_with_annual_fee_success(self):
        """测试成功创建带年费的信用卡"""
        card_data = self.data_gen.generate_test_card_with_annual_fee_data("年费")
        
        response = self.client.post(
            "/api/cards/",
            json=card_data,
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证基础信用卡信息
        assert data["card_name"] == card_data["card_name"]
        assert data["bank_name"] == card_data["bank_name"]
        assert data["has_annual_fee"] is True
        
        # 验证年费规则信息
        if "annual_fee_rule" in data and data["annual_fee_rule"]:
            annual_fee_rule = data["annual_fee_rule"]
            assert annual_fee_rule["fee_type"] == card_data["fee_type"]
            assert float(annual_fee_rule["base_fee"]) == card_data["base_fee"]
            assert float(annual_fee_rule["waiver_condition_value"]) == card_data["waiver_condition_value"]
        
        # 保存创建的卡片ID用于后续测试
        self.created_card_with_fee_id = data["id"]
    
    def test_03_get_cards_basic_list(self):
        """测试获取基础信用卡列表"""
        response = self.client.get(
            "/api/cards/basic",
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        self.api_test.assert_pagination_response(data)
        
        # 验证列表结构
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
    
    def test_04_get_cards_with_annual_fee_list(self):
        """测试获取带年费信息的信用卡列表"""
        response = self.client.get(
            "/api/cards/",
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        self.api_test.assert_pagination_response(data)
        
        # 验证列表结构
        assert "items" in data
        assert "pagination" in data
        assert isinstance(data["items"], list)
        
        # 如果有数据，验证年费字段
        if data["items"]:
            first_card = data["items"][0]
            assert "has_annual_fee" in first_card
            assert "annual_fee_amount" in first_card
            assert "fee_type_display" in first_card
            assert "current_year_fee_status" in first_card
    
    def test_05_search_cards_by_keyword(self):
        """测试通过关键词搜索信用卡"""
        # 先创建一张测试卡片
        card_data = self.data_gen.generate_test_card_data("搜索测试")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        self.api_test.assert_api_success(create_response)
        
        # 搜索测试
        response = self.client.get(
            "/api/cards/basic?keyword=搜索测试",
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        self.api_test.assert_pagination_response(data)
        
        # 验证搜索结果
        assert data["pagination"]["total"] >= 1
        
        # 验证搜索结果包含关键词
        found_match = False
        for card in data["items"]:
            if "搜索测试" in card.get("bank_name", "") or "搜索测试" in card.get("card_name", ""):
                found_match = True
                break
        assert found_match, "搜索结果应包含匹配的卡片"
    
    def test_06_get_card_detail_success(self):
        """测试获取信用卡详情"""
        # 先创建一张卡片
        card_data = self.data_gen.generate_test_card_with_annual_fee_data("详情测试")
        create_response = self.client.post(
            "/api/cards/",
            json=card_data,
            headers=self.user_headers
        )
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        # 获取详情
        response = self.client.get(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        
        # 验证详情数据
        assert data["id"] == card_id
        assert data["card_name"] == card_data["card_name"]
        assert data["bank_name"] == card_data["bank_name"]
        assert "has_annual_fee" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_07_update_card_success(self):
        """测试更新信用卡信息"""
        # 先创建一张卡片
        card_data = self.data_gen.generate_test_card_data("更新测试")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        # 更新信息
        update_data = {
            "card_name": "更新后的卡片名称",
            "credit_limit": 80000.00,
            "notes": "更新后的备注"
        }
        
        response = self.client.put(
            f"/api/cards/{card_id}",
            json=update_data,
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        
        # 验证更新结果
        assert data["card_name"] == update_data["card_name"]
        assert float(data["credit_limit"]) == update_data["credit_limit"]
        assert data["notes"] == update_data["notes"]
        # 未更新的字段应保持原值
        assert data["bank_name"] == card_data["bank_name"]
        assert data["card_number"] == card_data["card_number"]
    
    def test_08_update_card_with_annual_fee(self):
        """测试更新带年费的信用卡信息"""
        # 先创建一张带年费的卡片
        card_data = self.data_gen.generate_test_card_with_annual_fee_data("年费更新测试")
        create_response = self.client.post(
            "/api/cards/",
            json=card_data,
            headers=self.user_headers
        )
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        # 更新年费信息
        update_data = {
            "card_name": "更新后的年费卡片",
            "annual_fee_enabled": True,
            "fee_type": "transaction_amount",
            "base_fee": 300.00,
            "waiver_condition_value": 50000,
            "fee_description": "更新后的年费规则"
        }
        
        response = self.client.put(
            f"/api/cards/{card_id}",
            json=update_data,
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        
        # 验证更新结果
        assert data["card_name"] == update_data["card_name"]
        assert data["has_annual_fee"] is True
        
        # 验证年费规则更新
        if "annual_fee_rule" in data and data["annual_fee_rule"]:
            annual_fee_rule = data["annual_fee_rule"]
            assert annual_fee_rule["fee_type"] == update_data["fee_type"]
            assert float(annual_fee_rule["base_fee"]) == update_data["base_fee"]
    
    def test_09_delete_card_success(self):
        """测试删除信用卡"""
        # 先创建一张卡片
        card_data = self.data_gen.generate_test_card_data("删除测试")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        # 删除卡片
        response = self.client.delete(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_success(response)
        
        # 验证删除后无法获取
        get_response = self.client.get(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        self.api_test.assert_api_error(get_response, expected_status=404)
    
    # ==================== 数据验证测试 ====================
    
    def test_10_create_card_invalid_card_number(self):
        """测试创建信用卡时卡号格式无效"""
        card_data = self.data_gen.generate_test_card_data("无效卡号")
        card_data["card_number"] = "invalid-card-number"
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    def test_11_create_card_duplicate_card_number(self):
        """测试创建重复卡号的信用卡"""
        card_data = self.data_gen.generate_test_card_data("重复卡号")
        
        # 创建第一张卡片
        response1 = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        self.api_test.assert_api_success(response1)
        
        # 尝试创建相同卡号的卡片
        response2 = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response2, expected_status=422)
    
    def test_12_create_card_invalid_expiry_date(self):
        """测试创建信用卡时有效期无效"""
        card_data = self.data_gen.generate_test_card_data("过期日期")
        card_data["expiry_year"] = 2020  # 过去的年份
        card_data["expiry_month"] = 1
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    def test_13_create_card_invalid_credit_limit(self):
        """测试创建信用卡时信用额度无效"""
        card_data = self.data_gen.generate_test_card_data("无效额度")
        card_data["credit_limit"] = -1000  # 负数额度
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    def test_14_create_card_invalid_billing_due_day(self):
        """测试创建信用卡时账单日/还款日无效"""
        card_data = self.data_gen.generate_test_card_data("无效日期")
        card_data["billing_day"] = 35  # 超过31天
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    def test_15_create_card_annual_fee_invalid_data(self):
        """测试创建年费卡片时年费数据无效"""
        card_data = self.data_gen.generate_test_card_with_annual_fee_data("无效年费")
        card_data["annual_fee_enabled"] = True
        card_data["fee_type"] = "transaction_count"
        card_data["base_fee"] = -100  # 负数年费
        
        response = self.client.post(
            "/api/cards/",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    # ==================== 权限验证测试 ====================
    
    def test_16_create_card_without_auth(self):
        """测试未认证用户创建信用卡"""
        card_data = self.data_gen.generate_test_card_data("无权限")
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data
        )
        
        # 应该返回401未授权
        assert response.status_code in [401, 403]
    
    def test_17_get_other_user_card(self):
        """测试获取其他用户的信用卡"""
        # 创建另一个用户
        other_user = self.api_test.setup_test_user()
        other_headers = {"Authorization": f"Bearer {other_user['token']}"}
        
        # 用其他用户创建卡片
        card_data = self.data_gen.generate_test_card_data("其他用户")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=other_headers
        )
        other_card = self.api_test.assert_api_success(create_response)
        
        # 用当前用户尝试获取其他用户的卡片
        response = self.client.get(
            f"/api/cards/{other_card['id']}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
    
    def test_18_update_other_user_card(self):
        """测试更新其他用户的信用卡"""
        # 创建另一个用户和卡片
        other_user = self.api_test.setup_test_user()
        other_headers = {"Authorization": f"Bearer {other_user['token']}"}
        
        card_data = self.data_gen.generate_test_card_data("其他用户更新")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=other_headers
        )
        other_card = self.api_test.assert_api_success(create_response)
        
        # 用当前用户尝试更新其他用户的卡片
        update_data = {"card_name": "恶意更新"}
        response = self.client.put(
            f"/api/cards/{other_card['id']}",
            json=update_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
    
    def test_19_delete_other_user_card(self):
        """测试删除其他用户的信用卡"""
        # 创建另一个用户和卡片
        other_user = self.api_test.setup_test_user()
        other_headers = {"Authorization": f"Bearer {other_user['token']}"}
        
        card_data = self.data_gen.generate_test_card_data("其他用户删除")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=other_headers
        )
        other_card = self.api_test.assert_api_success(create_response)
        
        # 用当前用户尝试删除其他用户的卡片
        response = self.client.delete(
            f"/api/cards/{other_card['id']}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
    
    # ==================== 分页和搜索测试 ====================
    
    def test_20_pagination_with_different_page_sizes(self):
        """测试不同页面大小的分页"""
        # 创建多张卡片用于分页测试
        for i in range(5):
            card_data = self.data_gen.generate_test_card_data(f"分页{i}")
            response = self.client.post(
                "/api/cards/basic",
                json=card_data,
                headers=self.user_headers
            )
            self.api_test.assert_api_success(response)
        
        # 测试不同页面大小
        for page_size in [2, 3, 5]:
            response = self.client.get(
                f"/api/cards/basic?page=1&page_size={page_size}",
                headers=self.user_headers
            )
            
            data = self.api_test.assert_api_success(response)
            self.api_test.assert_pagination_response(data)
            
            # 验证页面大小
            assert len(data["items"]) <= page_size
            assert data["pagination"]["page_size"] == page_size
    
    def test_21_search_with_empty_keyword(self):
        """测试空关键词搜索"""
        response = self.client.get(
            "/api/cards/basic?keyword=",
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        self.api_test.assert_pagination_response(data)
        
        # 空关键词应返回所有记录
        assert isinstance(data["items"], list)
    
    def test_22_search_with_nonexistent_keyword(self):
        """测试不存在的关键词搜索"""
        response = self.client.get(
            "/api/cards/basic?keyword=不存在的关键词xyz123",
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        self.api_test.assert_pagination_response(data)
        
        # 应该返回空列表
        assert data["pagination"]["total"] == 0
        assert len(data["items"]) == 0
    
    def test_23_invalid_page_parameters(self):
        """测试无效的分页参数"""
        # 页码为0
        response = self.client.get(
            "/api/cards/basic?page=0",
            headers=self.user_headers
        )
        self.api_test.assert_api_error(response, expected_status=422)
        
        # 页面大小超过限制
        response = self.client.get(
            "/api/cards/basic?page_size=200",
            headers=self.user_headers
        )
        self.api_test.assert_api_error(response, expected_status=422)
    
    # ==================== 边界情况和异常测试 ====================
    
    def test_24_get_nonexistent_card(self):
        """测试获取不存在的信用卡"""
        fake_id = str(uuid.uuid4())
        response = self.client.get(
            f"/api/cards/{fake_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
    
    def test_25_update_nonexistent_card(self):
        """测试更新不存在的信用卡"""
        fake_id = str(uuid.uuid4())
        update_data = {"card_name": "不存在的卡片"}
        
        response = self.client.put(
            f"/api/cards/{fake_id}",
            json=update_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
    
    def test_26_delete_nonexistent_card(self):
        """测试删除不存在的信用卡"""
        fake_id = str(uuid.uuid4())
        
        response = self.client.delete(
            f"/api/cards/{fake_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
    
    def test_27_invalid_uuid_format(self):
        """测试无效的UUID格式"""
        invalid_id = "invalid-uuid-format"
        
        response = self.client.get(
            f"/api/cards/{invalid_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    def test_28_empty_required_fields(self):
        """测试必填字段为空"""
        card_data = self.data_gen.generate_test_card_data("必填字段")
        card_data["bank_name"] = ""  # 空的必填字段
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422)
    
    def test_29_create_card_with_max_length_fields(self):
        """测试创建信用卡时字段长度达到最大值"""
        card_data = self.data_gen.generate_test_card_data("最大长度")
        card_data["bank_name"] = "A" * 50  # 最大长度
        card_data["card_name"] = "B" * 100  # 最大长度
        card_data["notes"] = "C" * 500  # 最大长度
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        data = self.api_test.assert_api_success(response)
        assert data["bank_name"] == card_data["bank_name"]
        assert data["card_name"] == card_data["card_name"]
        assert data["notes"] == card_data["notes"]
    
    def test_30_create_card_with_exceed_length_fields(self):
        """测试创建信用卡时字段长度超过最大值"""
        card_data = self.data_gen.generate_test_card_data("超长字段")
        card_data["bank_name"] = "A" * 51  # 超过最大长度
        
        response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=422) 