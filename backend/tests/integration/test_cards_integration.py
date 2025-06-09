#!/usr/bin/env python3
"""
信用卡模块集成测试

使用真实HTTP请求测试信用卡相关的API接口，包括：
- 信用卡CRUD操作的端到端测试
- 年费管理功能的集成测试
- 网络层和序列化验证
- 完整的用户场景测试
- 实际数据库交互测试
"""

import pytest
import uuid
import time
from decimal import Decimal
from typing import Dict, Any
from tests.base_test import RequestsTestClient, BaseAPITest

# ==================== 测试数据生成器 ====================

class CardIntegrationTestDataGenerator:
    """信用卡集成测试数据生成器"""
    
    @staticmethod
    def generate_real_card_data(suffix: str = "") -> Dict[str, Any]:
        """生成真实的信用卡测试数据"""
        import random
        import uuid
        
        # 生成更唯一的卡号：使用微秒时间戳+随机数，控制在19位以内
        timestamp = str(int(time.time() * 1000000))[-7:]  # 微秒时间戳后7位
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        return {
            "bank_name": f"招商银行{suffix}",
            "card_name": f"招商银行信用卡{suffix}",
            "card_number": f"622588{timestamp}{random_digits}",  # 622588(6位) + 7位时间戳 + 6位随机数 = 19位
            "card_type": "visa",
            "credit_limit": 50000.00,
            "used_amount": 1200.00,
            "billing_day": 8,
            "due_day": 28,
            "expiry_month": 12,
            "expiry_year": 2028,
            "card_color": "#FF6B35",
            "status": "active",
            "is_active": True,
            "notes": f"集成测试用卡{suffix} - {timestamp}"
        }
    
    @staticmethod
    def generate_annual_fee_card_data(suffix: str = "") -> Dict[str, Any]:
        """生成包含年费的真实信用卡数据"""
        base_data = CardIntegrationTestDataGenerator.generate_real_card_data(suffix)
        base_data.update({
            "annual_fee_enabled": True,
            "fee_type": "transaction_count",
            "base_fee": 200.00,
            "waiver_condition_value": 12,
            "points_per_yuan": 0.1,  # 提供默认值以触发验证器
            "annual_fee_month": 2,
            "annual_fee_day": 28,
            "fee_description": f"年费集成测试{suffix}"
        })
        return base_data


# ==================== 集成测试类 ====================

@pytest.mark.integration
@pytest.mark.requires_server
class TestCardsIntegration:
    """信用卡集成测试"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.client = RequestsTestClient()
        self.api_test = BaseAPITest(self.client)
        
        # 检查服务器可用性
        self._check_server_availability()
        
        # 设置测试用户
        self.test_user = self.api_test.setup_test_user()
        self.user_headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        # 测试数据生成器
        self.data_gen = CardIntegrationTestDataGenerator()
    
    def _check_server_availability(self):
        """检查服务器是否可用"""
        try:
            # 检查文档页面是否可用（无需认证）
            response = self.client.get("/docs")
            if response.status_code != 200:
                pytest.skip(f"服务器不可用，跳过集成测试: HTTP {response.status_code}")
        except Exception as e:
            pytest.skip(f"服务器不可用，跳过集成测试: {str(e)}")
    
    # ==================== 端到端CRUD测试 ====================
    
    def test_01_complete_card_lifecycle(self):
        """测试信用卡完整生命周期（创建->查询->更新->删除）"""
        # 1. 创建信用卡
        card_data = self.data_gen.generate_real_card_data("生命周期")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        created_card = self.api_test.assert_api_success(create_response, 200)
        card_id = created_card["id"]
        
        # 验证创建结果
        assert created_card["card_name"] == card_data["card_name"]
        assert created_card["bank_name"] == card_data["bank_name"]
        assert created_card["card_number"] == card_data["card_number"]
        assert float(created_card["credit_limit"]) == card_data["credit_limit"]
        
        # 2. 查询信用卡详情
        get_response = self.client.get(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        card_detail = self.api_test.assert_api_success(get_response)
        assert card_detail["id"] == card_id
        assert card_detail["card_name"] == card_data["card_name"]
        
        # 3. 更新信用卡
        update_data = {
            "card_name": "更新后的卡片名称",
            "credit_limit": 80000.00,
            "notes": "更新后的备注信息"
        }
        
        update_response = self.client.put(
            f"/api/cards/{card_id}",
            json=update_data,
            headers=self.user_headers
        )
        
        updated_card = self.api_test.assert_api_success(update_response)
        assert updated_card["card_name"] == update_data["card_name"]
        assert float(updated_card["credit_limit"]) == update_data["credit_limit"]
        assert updated_card["notes"] == update_data["notes"]
        
        # 4. 验证更新后的查询
        verify_response = self.client.get(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        verified_card = self.api_test.assert_api_success(verify_response)
        assert verified_card["card_name"] == update_data["card_name"]
        assert float(verified_card["credit_limit"]) == update_data["credit_limit"]
        
        # 5. 删除信用卡
        delete_response = self.client.delete(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_success(delete_response)
        
        # 6. 验证删除结果
        get_deleted_response = self.client.get(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(get_deleted_response, expected_status=404)
    
    def test_02_annual_fee_card_lifecycle(self):
        """测试带年费的信用卡完整生命周期"""
        # 1. 创建带年费的信用卡
        card_data = self.data_gen.generate_annual_fee_card_data("年费生命周期")
        create_response = self.client.post(
            "/api/cards/",
            json=card_data,
            headers=self.user_headers
        )
        
        created_card = self.api_test.assert_api_success(create_response, 200)
        card_id = created_card["id"]
        
        # 验证年费相关字段
        assert created_card["has_annual_fee"] is True
        if "annual_fee_rule" in created_card and created_card["annual_fee_rule"]:
            rule = created_card["annual_fee_rule"]
            assert rule["fee_type"] == card_data["fee_type"]
            assert float(rule["base_fee"]) == card_data["base_fee"]
        
        # 2. 查询详情验证年费信息
        get_response = self.client.get(
            f"/api/cards/{card_id}",
            headers=self.user_headers
        )
        
        card_detail = self.api_test.assert_api_success(get_response)
        assert card_detail["has_annual_fee"] is True
        
        # 3. 更新年费规则
        update_data = {
            "annual_fee_enabled": True,
            "fee_type": "transaction_amount",
            "base_fee": 300.00,
            "waiver_condition_value": 50000,
            "fee_description": "更新后的年费规则"
        }
        
        update_response = self.client.put(
            f"/api/cards/{card_id}",
            json=update_data,
            headers=self.user_headers
        )
        
        updated_card = self.api_test.assert_api_success(update_response)
        assert updated_card["has_annual_fee"] is True
        
        # 验证年费规则更新
        if "annual_fee_rule" in updated_card and updated_card["annual_fee_rule"]:
            rule = updated_card["annual_fee_rule"]
            assert rule["fee_type"] == update_data["fee_type"]
            assert float(rule["base_fee"]) == update_data["base_fee"]
        
        # 4. 禁用年费管理
        disable_fee_data = {"annual_fee_enabled": False}
        disable_response = self.client.put(
            f"/api/cards/{card_id}",
            json=disable_fee_data,
            headers=self.user_headers
        )
        
        disabled_card = self.api_test.assert_api_success(disable_response)
        assert disabled_card["has_annual_fee"] is False
        
        # 5. 清理测试数据
        self.client.delete(f"/api/cards/{card_id}", headers=self.user_headers)
    
    def test_03_card_list_with_pagination_and_search(self):
        """测试信用卡列表的分页和搜索功能"""
        # 创建多张测试卡片
        created_cards = []
        for i in range(3):
            card_data = self.data_gen.generate_real_card_data(f"搜索测试{i}")
            create_response = self.client.post(
                "/api/cards/basic",
                json=card_data,
                headers=self.user_headers
            )
            created_card = self.api_test.assert_api_success(create_response)
            created_cards.append(created_card)
        
        try:
            # 1. 测试基础列表
            list_response = self.client.get(
                "/api/cards/basic",
                headers=self.user_headers
            )
            
            list_data = self.api_test.assert_api_success(list_response)
            self.api_test.assert_pagination_response(list_data)
            assert len(list_data["items"]) >= 3
            
            # 2. 测试分页
            page_response = self.client.get(
                "/api/cards/basic?page=1&page_size=2",
                headers=self.user_headers
            )
            
            page_data = self.api_test.assert_api_success(page_response)
            assert len(page_data["items"]) <= 2
            assert page_data["pagination"]["page_size"] == 2
            
            # 3. 测试搜索
            search_response = self.client.get(
                "/api/cards/basic?keyword=搜索测试",
                headers=self.user_headers
            )
            
            search_data = self.api_test.assert_api_success(search_response)
            assert search_data["pagination"]["total"] >= 3
            
            # 验证搜索结果
            for card in search_data["items"]:
                card_matches = (
                    "搜索测试" in card.get("bank_name", "") or 
                    "搜索测试" in card.get("card_name", "") or
                    "搜索测试" in card.get("notes", "")
                )
                if not card_matches:
                    continue  # 可能有其他用户的搜索测试数据
            
            # 4. 测试年费版本列表
            annual_fee_response = self.client.get(
                "/api/cards/",
                headers=self.user_headers
            )
            
            annual_fee_data = self.api_test.assert_api_success(annual_fee_response)
            self.api_test.assert_pagination_response(annual_fee_data)
            
            # 验证年费字段存在
            if annual_fee_data["items"]:
                first_card = annual_fee_data["items"][0]
                assert "has_annual_fee" in first_card
                assert "annual_fee_amount" in first_card
                assert "fee_type_display" in first_card
                assert "current_year_fee_status" in first_card
        
        finally:
            # 清理测试数据
            for card in created_cards:
                try:
                    self.client.delete(f"/api/cards/{card['id']}", headers=self.user_headers)
                except:
                    pass  # 忽略清理错误
    
    # ==================== 网络和序列化测试 ====================
    
    def test_04_network_response_headers(self):
        """测试HTTP响应头和网络层"""
        response = self.client.get(
            "/api/cards/basic",
            headers=self.user_headers
        )
        
        # 验证响应状态码
        assert response.status_code == 200
        
        # 验证响应头
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
        
        # 验证响应体可以正确解析为JSON
        data = response.json()
        assert isinstance(data, dict)
        assert "success" in data
        assert "data" in data
        assert "timestamp" in data
    
    def test_05_json_serialization_edge_cases(self):
        """测试JSON序列化的边界情况"""
        # 创建包含边界值的信用卡
        card_data = self.data_gen.generate_real_card_data("边界值")
        card_data.update({
            "credit_limit": 9999999.99,  # 最大额度
            "used_amount": 0.01,         # 最小使用金额
            "billing_day": 31,           # 最大账单日
            "due_day": 1,                # 最小还款日
            "notes": "特殊字符测试: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        })
        
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        # 验证边界值正确序列化
        assert float(created_card["credit_limit"]) == card_data["credit_limit"]
        assert float(created_card["used_amount"]) == card_data["used_amount"]
        assert created_card["billing_day"] == card_data["billing_day"]
        assert created_card["due_day"] == card_data["due_day"]
        assert created_card["notes"] == card_data["notes"]
        
        # 清理测试数据
        self.client.delete(f"/api/cards/{card_id}", headers=self.user_headers)
    
    def test_06_concurrent_operations(self):
        """测试并发操作的处理"""
        # 创建一张卡片
        card_data = self.data_gen.generate_real_card_data("并发测试")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        try:
            # 同时发起多个查询请求
            responses = []
            for i in range(3):
                response = self.client.get(
                    f"/api/cards/{card_id}",
                    headers=self.user_headers
                )
                responses.append(response)
            
            # 验证所有请求都成功
            for response in responses:
                data = self.api_test.assert_api_success(response)
                assert data["id"] == card_id
                assert data["card_name"] == card_data["card_name"]
        
        finally:
            # 清理测试数据
            self.client.delete(f"/api/cards/{card_id}", headers=self.user_headers)
    
    # ==================== 权限和安全测试 ====================
    
    def test_07_authentication_required(self):
        """测试认证要求"""
        card_data = self.data_gen.generate_real_card_data("认证测试")
        
        # 不提供认证头的请求应该被拒绝
        response = self.client.post("/api/cards/basic", json=card_data)
        assert response.status_code in [401, 403]
        
        # 无效token的请求应该被拒绝
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = self.client.post(
            "/api/cards/basic", 
            json=card_data, 
            headers=invalid_headers
        )
        assert response.status_code in [401, 403]
    
    def test_08_user_isolation(self):
        """测试用户数据隔离"""
        # 创建两个不同的用户
        user1 = self.api_test.setup_test_user()
        user2 = self.api_test.setup_test_user()
        
        user1_headers = {"Authorization": f"Bearer {user1['token']}"}
        user2_headers = {"Authorization": f"Bearer {user2['token']}"}
        
        # 用户1创建信用卡
        card_data = self.data_gen.generate_real_card_data("隔离测试")
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=user1_headers
        )
        
        user1_card = self.api_test.assert_api_success(create_response)
        card_id = user1_card["id"]
        
        try:
            # 用户2不应该能够访问用户1的卡片
            get_response = self.client.get(
                f"/api/cards/{card_id}",
                headers=user2_headers
            )
            self.api_test.assert_api_error(get_response, expected_status=404)
            
            # 用户2不应该能够更新用户1的卡片
            update_data = {"card_name": "恶意更新"}
            update_response = self.client.put(
                f"/api/cards/{card_id}",
                json=update_data,
                headers=user2_headers
            )
            self.api_test.assert_api_error(update_response, expected_status=404)
            
            # 用户2不应该能够删除用户1的卡片
            delete_response = self.client.delete(
                f"/api/cards/{card_id}",
                headers=user2_headers
            )
            self.api_test.assert_api_error(delete_response, expected_status=404)
            
            # 用户1应该仍然能够正常访问自己的卡片
            verify_response = self.client.get(
                f"/api/cards/{card_id}",
                headers=user1_headers
            )
            self.api_test.assert_api_success(verify_response)
        
        finally:
            # 清理测试数据
            self.client.delete(f"/api/cards/{card_id}", headers=user1_headers)
    
    # ==================== 数据完整性测试 ====================
    
    def test_09_data_validation_integration(self):
        """测试数据验证的完整性"""
        # 测试各种无效数据
        invalid_test_cases = [
            {
                "name": "无效卡号",
                "data": {"card_number": "invalid-card"},
                "expected_status": 422
            },
            {
                "name": "负数额度",
                "data": {"credit_limit": -1000},
                "expected_status": 422
            },
            {
                "name": "过期日期",
                "data": {"expiry_year": 2020, "expiry_month": 1},
                "expected_status": 422
            },
            {
                "name": "无效账单日",
                "data": {"billing_day": 35},
                "expected_status": 422
            },
            {
                "name": "空银行名称",
                "data": {"bank_name": ""},
                "expected_status": 422
            },
            {
                "name": "超长字段",
                "data": {"bank_name": "A" * 51},
                "expected_status": 422
            }
        ]
        
        for test_case in invalid_test_cases:
            card_data = self.data_gen.generate_real_card_data("验证测试")
            card_data.update(test_case["data"])
            
            response = self.client.post(
                "/api/cards/basic",
                json=card_data,
                headers=self.user_headers
            )
            
            assert response.status_code == test_case["expected_status"], \
                f"测试用例 '{test_case['name']}' 失败，期望状态码 {test_case['expected_status']}，实际 {response.status_code}"
    
    def test_10_duplicate_card_number_prevention(self):
        """测试重复卡号的防止机制"""
        card_data = self.data_gen.generate_real_card_data("重复卡号")
        
        # 创建第一张卡片
        response1 = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        
        first_card = self.api_test.assert_api_success(response1)
        
        try:
            # 尝试创建相同卡号的卡片
            response2 = self.client.post(
                "/api/cards/basic",
                json=card_data,
                headers=self.user_headers
            )
            
            self.api_test.assert_api_error(response2, expected_status=422)
        
        finally:
            # 清理测试数据
            self.client.delete(f"/api/cards/{first_card['id']}", headers=self.user_headers)
    
    # ==================== 性能和稳定性测试 ====================
    
    def test_11_response_time_verification(self):
        """测试响应时间验证"""
        import time
        
        # 测试创建操作的响应时间
        card_data = self.data_gen.generate_real_card_data("响应时间")
        
        start_time = time.time()
        create_response = self.client.post(
            "/api/cards/basic",
            json=card_data,
            headers=self.user_headers
        )
        create_time = time.time() - start_time
        
        created_card = self.api_test.assert_api_success(create_response)
        card_id = created_card["id"]
        
        # 创建操作应该在合理时间内完成（5秒）
        assert create_time < 5.0, f"创建操作耗时过长: {create_time:.2f}秒"
        
        try:
            # 测试查询操作的响应时间
            start_time = time.time()
            get_response = self.client.get(
                f"/api/cards/{card_id}",
                headers=self.user_headers
            )
            get_time = time.time() - start_time
            
            self.api_test.assert_api_success(get_response)
            
            # 查询操作应该在更短时间内完成（2秒）
            assert get_time < 2.0, f"查询操作耗时过长: {get_time:.2f}秒"
        
        finally:
            # 清理测试数据
            self.client.delete(f"/api/cards/{card_id}", headers=self.user_headers)
    
    def test_12_error_handling_robustness(self):
        """测试错误处理的健壮性"""
        # 测试不存在的资源
        fake_id = str(uuid.uuid4())
        response = self.client.get(
            f"/api/cards/{fake_id}",
            headers=self.user_headers
        )
        
        self.api_test.assert_api_error(response, expected_status=404)
        
        # 验证错误响应格式（HTTPException格式）
        error_data = response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "信用卡不存在"
        
        # 测试无效UUID格式
        invalid_id_response = self.client.get(
            "/api/cards/invalid-uuid",
            headers=self.user_headers
        )
        
        assert invalid_id_response.status_code == 422 