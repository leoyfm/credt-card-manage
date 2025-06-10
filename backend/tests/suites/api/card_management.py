"""
信用卡管理API测试套件

使用新测试框架v2.0进行信用卡管理功能的全面测试
包括CRUD操作、权限验证、业务逻辑验证等
"""

import pytest
from tests.framework import (
    test_suite, api_test, with_user, with_cards, 
    performance_test, stress_test
)


@test_suite("信用卡管理API")
class CardManagementTests:
    """信用卡管理功能测试套件"""
    
    @api_test
    @with_user
    def test_create_card_success(self, api, user):
        """测试成功创建信用卡"""
        card_data = {
            "card_name": "招商银行信用卡",
            "bank_name": "招商银行",
            "card_number": "6225123456789012",
            "credit_limit": 50000.00,
            "expiry_month": 12,
            "expiry_year": 2027,
            "billing_date": 15,
            "due_date": 5
        }
        
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().with_data(
            card_name="招商银行信用卡",
            bank_name="招商银行",
            credit_limit=50000.00
        )
    
    @api_test
    @with_user
    def test_create_card_validation_error(self, api, user):
        """测试创建信用卡参数验证"""
        invalid_data = {
            "card_name": "",  # 空名称
            "credit_limit": -1000  # 负额度
        }
        
        api.post("/api/v1/user/cards/create", data=invalid_data).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=3)
    def test_get_cards_list(self, api, user, cards):
        """测试获取信用卡列表"""
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=3,
            items_type="card"
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_get_card_details(self, api, user, cards):
        """测试获取信用卡详情"""
        card = cards[0] if isinstance(cards, list) else cards
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            id=card['id'],
            card_name=card['card_name']
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_update_card_success(self, api, user, cards):
        """测试成功更新信用卡"""
        card = cards[0] if isinstance(cards, list) else cards
        update_data = {
            "card_name": "更新后的信用卡名称",
            "credit_limit": 80000.00
        }
        
        api.put(f"/api/v1/user/cards/{card['id']}/update", data=update_data).should.succeed()
        
        # 验证更新生效
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            card_name="更新后的信用卡名称",
            credit_limit=80000.00
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_update_card_status(self, api, user, cards):
        """测试更新信用卡状态"""
        card = cards[0] if isinstance(cards, list) else cards
        
        api.put(f"/api/v1/user/cards/{card['id']}/status", data={
            "status": "frozen"
        }).should.succeed()
        
        # 验证状态更新
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            status="frozen"
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_delete_card_success(self, api, user, cards):
        """测试成功删除信用卡"""
        card = cards[0] if isinstance(cards, list) else cards
        
        api.delete(f"/api/v1/user/cards/{card['id']}/delete").should.succeed()
        
        # 验证卡片已删除
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.fail(404)
    
    @api_test
    @with_user
    def test_access_nonexistent_card(self, api, user):
        """测试访问不存在的信用卡"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        api.get(f"/api/v1/user/cards/{fake_id}/details").should.fail(404)
    
    @api_test
    @with_user
    @with_cards(count=5, bank="招商银行")
    def test_cards_filtering(self, api, user, cards):
        """测试信用卡筛选功能"""
        # 按银行筛选
        api.get("/api/v1/user/cards/list?bank_name=招商银行").should.succeed().with_pagination(
            total_items=5
        )
        
        # 按状态筛选
        api.get("/api/v1/user/cards/list?status=active").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=25)
    def test_cards_pagination(self, api, user, cards):
        """测试信用卡分页功能"""
        # 第一页
        api.get("/api/v1/user/cards/list?page=1&page_size=10").should.succeed().with_pagination(
            current_page=1,
            total_items=25
        )
        
        # 第二页
        api.get("/api/v1/user/cards/list?page=2&page_size=10").should.succeed()


@test_suite("信用卡权限测试")
class CardPermissionTests:
    """信用卡权限验证测试套件"""
    
    @api_test
    @with_user
    def test_unauthorized_access_card(self, api, user):
        """测试未授权访问他人信用卡"""
        # 这里应该使用其他用户的卡片ID
        other_card_id = "11111111-1111-1111-1111-111111111111"
        api.get(f"/api/v1/user/cards/{other_card_id}/details").should.fail(403)
    
    @api_test
    def test_unauthenticated_access(self, api):
        """测试未认证访问信用卡接口"""
        api.get("/api/v1/user/cards/list").should.fail(401)


@test_suite("信用卡性能测试")
class CardPerformanceTests:
    """信用卡管理性能测试套件"""
    
    @performance_test
    @with_user
    @with_cards(count=10)
    def test_cards_list_performance(self, api, user, cards):
        """测试信用卡列表性能"""
        api.get("/api/v1/user/cards/list").should.succeed().complete_within(seconds=0.5)
    
    @performance_test
    @with_user
    def test_card_creation_performance(self, api, user):
        """测试信用卡创建性能"""
        card_data = {
            "card_name": "性能测试卡",
            "bank_name": "测试银行",
            "card_number": "6225000000000000",
            "credit_limit": 50000.00,
            "expiry_month": 12,
            "expiry_year": 2027
        }
        
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().complete_within(seconds=1.0)
    
    @stress_test(concurrent_users=20, duration=30)
    @with_user
    def test_cards_concurrent_access(self, api, user):
        """测试信用卡并发访问"""
        api.get("/api/v1/user/cards/list").should.succeed()


@test_suite("信用卡业务逻辑测试")
class CardBusinessLogicTests:
    """信用卡业务逻辑测试套件"""
    
    @api_test
    @with_user
    def test_card_number_encryption(self, api, user):
        """测试信用卡号加密存储"""
        card_data = {
            "card_name": "测试加密卡",
            "card_number": "6225123456789012",
            "credit_limit": 50000.00,
            "expiry_month": 12,
            "expiry_year": 2027
        }
        
        response = api.post("/api/v1/user/cards/create", data=card_data).should.succeed()
        
        # 验证返回的卡号是脱敏的
        card = response.data
        assert "*" in card["card_number"], "信用卡号应该被脱敏"
    
    @api_test
    @with_user
    def test_card_limit_validation(self, api, user):
        """测试信用额度验证"""
        # 测试负额度
        api.post("/api/v1/user/cards/create", data={
            "card_name": "测试卡",
            "credit_limit": -1000
        }).should.fail(422)
        
        # 测试过大额度
        api.post("/api/v1/user/cards/create", data={
            "card_name": "测试卡", 
            "credit_limit": 10000000  # 1千万
        }).should.fail(422)
    
    @api_test
    @with_user
    def test_expiry_date_validation(self, api, user):
        """测试有效期验证"""
        # 测试过期的有效期
        api.post("/api/v1/user/cards/create", data={
            "card_name": "过期测试卡",
            "expiry_month": 12,
            "expiry_year": 2020  # 已过期
        }).should.fail(422)
        
        # 测试无效月份
        api.post("/api/v1/user/cards/create", data={
            "card_name": "无效月份卡",
            "expiry_month": 13,  # 无效月份
            "expiry_year": 2027
        }).should.fail(422)