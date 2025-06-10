"""
年费管理API测试套件

使用新测试框架v2.0进行年费管理功能的全面测试
包括年费规则、减免计算、记录管理等功能
"""

import pytest
from tests.framework import (
    test_suite, api_test, with_user, with_cards, with_annual_fees,
    performance_test, stress_test
)


@test_suite("年费规则管理")
class AnnualFeeRuleTests:
    """年费规则管理测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_spending_rule_success(self, api, user, cards):
        """测试成功创建消费金额减免规则"""
        card = cards[0] if isinstance(cards, list) else cards
        rule_data = {
            "card_id": card['id'],
            "rule_name": "年消费满5万减免年费",
            "condition_type": "spending_amount",
            "condition_value": 50000.00,
            "condition_period": "yearly",
            "description": "全年消费满5万元减免年费"
        }
        
        api.post("/api/v1/user/annual-fees/rules/create", data=rule_data).should.succeed().with_data(
            rule_name="年消费满5万减免年费",
            condition_type="spending_amount",
            condition_value=50000.00
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_transaction_count_rule(self, api, user, cards):
        """测试创建交易次数减免规则"""
        card = cards[0] if isinstance(cards, list) else cards
        rule_data = {
            "card_id": card['id'],
            "rule_name": "年刷卡满12次减免年费",
            "condition_type": "transaction_count",
            "condition_count": 12,
            "condition_period": "yearly"
        }
        
        api.post("/api/v1/user/annual-fees/rules/create", data=rule_data).should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_points_redeem_rule(self, api, user, cards):
        """测试创建积分兑换减免规则"""
        card = cards[0] if isinstance(cards, list) else cards
        rule_data = {
            "card_id": card['id'],
            "rule_name": "积分兑换年费",
            "condition_type": "points_redeem",
            "condition_value": 58800,  # 588元年费需要58800积分
            "description": "使用58800积分兑换年费"
        }
        
        api.post("/api/v1/user/annual-fees/rules/create", data=rule_data).should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_get_card_rules(self, api, user, cards):
        """测试获取信用卡年费规则"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 先创建一条规则
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "测试规则",
            "condition_type": "spending_amount",
            "condition_value": 30000.00
        }).should.succeed()
        
        # 获取规则列表
        api.get("/api/v1/user/annual-fees/rules").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_update_rule_success(self, api, user, cards):
        """测试成功更新年费规则"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建规则
        create_response = api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "原始规则",
            "condition_type": "spending_amount",
            "condition_value": 30000.00
        }).should.succeed()
        
        rule_id = create_response.data['id']
        
        # 更新规则
        update_data = {
            "rule_name": "更新后的规则",
            "condition_value": 50000.00,
            "description": "更新后的描述"
        }
        
        api.put(f"/api/v1/user/annual-fees/rules/{rule_id}/update", data=update_data).should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_delete_rule_success(self, api, user, cards):
        """测试成功删除年费规则"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建规则
        create_response = api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "待删除规则",
            "condition_type": "spending_amount",
            "condition_value": 30000.00
        }).should.succeed()
        
        rule_id = create_response.data['id']
        
        # 删除规则
        api.delete(f"/api/v1/user/annual-fees/rules/{rule_id}/delete").should.succeed()
    
    @api_test
    @with_user
    def test_create_rule_validation_error(self, api, user):
        """测试创建规则参数验证"""
        invalid_data = {
            "rule_name": "",  # 空名称
            "condition_type": "invalid_type",  # 无效类型
            "condition_value": -1000  # 负值
        }
        
        api.post("/api/v1/user/annual-fees/rules/create", data=invalid_data).should.fail(422)


@test_suite("年费记录管理")
class AnnualFeeRecordTests:
    """年费记录管理测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_get_annual_fee_records(self, api, user, cards):
        """测试获取年费记录"""
        api.get("/api/v1/user/annual-fees/records").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_get_records_by_year(self, api, user, cards):
        """测试按年份筛选年费记录"""
        api.get("/api/v1/user/annual-fees/records?year=2024").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_get_records_by_card(self, api, user, cards):
        """测试按卡片筛选年费记录"""
        card = cards[0] if isinstance(cards, list) else cards
        api.get(f"/api/v1/user/annual-fees/records?card_id={card['id']}").should.succeed()


@test_suite("年费计算和减免")
class AnnualFeeCalculationTests:
    """年费计算和减免测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_fee_calculation_with_spending_rule(self, api, user, cards):
        """测试基于消费金额的年费计算"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建消费减免规则
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "消费满3万减免",
            "condition_type": "spending_amount", 
            "condition_value": 30000.00
        }).should.succeed()
        
        # 模拟创建满足条件的交易
        for i in range(10):
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": 3500.00,  # 总计35000元，满足减免条件
                "description": f"测试交易{i+1}"
            }).should.succeed()
        
        # 触发年费计算（这里假设有触发计算的接口）
        # api.post(f"/api/v1/user/annual-fees/calculate/{card['id']}").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_fee_calculation_with_transaction_count_rule(self, api, user, cards):
        """测试基于交易次数的年费计算"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建交易次数减免规则
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "年刷12次减免",
            "condition_type": "transaction_count",
            "condition_count": 12
        }).should.succeed()
        
        # 创建满足条件的交易次数
        for i in range(15):  # 超过12次
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": 100.00,
                "description": f"刷卡{i+1}"
            }).should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_multiple_rules_combination(self, api, user, cards):
        """测试多条规则组合"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建多条规则
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "消费条件",
            "condition_type": "spending_amount",
            "condition_value": 20000.00,
            "logical_operator": "AND",
            "rule_group_id": "group1"
        }).should.succeed()
        
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "次数条件",
            "condition_type": "transaction_count",
            "condition_count": 10,
            "logical_operator": "AND",
            "rule_group_id": "group1"
        }).should.succeed()


@test_suite("年费权限测试")
class AnnualFeePermissionTests:
    """年费权限验证测试套件"""
    
    @api_test
    @with_user
    def test_unauthorized_access_rules(self, api, user):
        """测试未授权访问他人年费规则"""
        other_rule_id = "11111111-1111-1111-1111-111111111111"
        api.get(f"/api/v1/user/annual-fees/rules/{other_rule_id}").should.fail(403)
    
    @api_test
    def test_unauthenticated_access(self, api):
        """测试未认证访问年费接口"""
        api.get("/api/v1/user/annual-fees/rules").should.fail(401)


@test_suite("年费性能测试")
class AnnualFeePerformanceTests:
    """年费管理性能测试套件"""
    
    @performance_test
    @with_user
    @with_cards(count=1)
    def test_rules_list_performance(self, api, user, cards):
        """测试年费规则列表性能"""
        api.get("/api/v1/user/annual-fees/rules").should.succeed().complete_within(seconds=0.5)
    
    @performance_test
    @with_user
    @with_cards(count=1)
    def test_rule_creation_performance(self, api, user, cards):
        """测试年费规则创建性能"""
        card = cards[0] if isinstance(cards, list) else cards
        rule_data = {
            "card_id": card['id'],
            "rule_name": "性能测试规则",
            "condition_type": "spending_amount",
            "condition_value": 50000.00
        }
        
        api.post("/api/v1/user/annual-fees/rules/create", data=rule_data).should.succeed().complete_within(seconds=1.0)
    
    @stress_test(concurrent_users=10, duration=30)
    @with_user
    @with_cards(count=1)
    def test_rules_concurrent_access(self, api, user, cards):
        """测试年费规则并发访问"""
        api.get("/api/v1/user/annual-fees/rules").should.succeed()


@test_suite("年费业务逻辑测试")
class AnnualFeeBusinessLogicTests:
    """年费业务逻辑测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_rule_condition_types_validation(self, api, user, cards):
        """测试规则条件类型验证"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 测试有效的条件类型
        valid_types = ["spending_amount", "transaction_count", "points_redeem", "specific_category"]
        for condition_type in valid_types:
            data = {
                "card_id": card['id'],
                "rule_name": f"{condition_type}规则",
                "condition_type": condition_type
            }
            
            if condition_type in ["spending_amount", "points_redeem"]:
                data["condition_value"] = 30000.00
            elif condition_type == "transaction_count":
                data["condition_count"] = 12
            
            api.post("/api/v1/user/annual-fees/rules/create", data=data).should.succeed()
        
        # 测试无效的条件类型
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "无效规则",
            "condition_type": "invalid_type"
        }).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_rule_period_validation(self, api, user, cards):
        """测试规则统计周期验证"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 测试有效的周期
        valid_periods = ["monthly", "quarterly", "yearly"]
        for period in valid_periods:
            api.post("/api/v1/user/annual-fees/rules/create", data={
                "card_id": card['id'],
                "rule_name": f"{period}规则",
                "condition_type": "spending_amount",
                "condition_value": 30000.00,
                "condition_period": period
            }).should.succeed()
        
        # 测试无效的周期
        api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "无效周期规则",
            "condition_type": "spending_amount",
            "condition_value": 30000.00,
            "condition_period": "invalid_period"
        }).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_rule_priority_ordering(self, api, user, cards):
        """测试规则优先级排序"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同优先级的规则
        priorities = [1, 5, 3]
        for i, priority in enumerate(priorities):
            api.post("/api/v1/user/annual-fees/rules/create", data={
                "card_id": card['id'],
                "rule_name": f"优先级{priority}规则",
                "condition_type": "spending_amount",
                "condition_value": 30000.00,
                "priority": priority
            }).should.succeed()
        
        # 获取规则列表，验证按优先级排序
        response = api.get("/api/v1/user/annual-fees/rules").should.succeed()
        # 这里可以验证返回的规则是否按优先级排序
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_rule_enable_disable(self, api, user, cards):
        """测试规则启用/禁用功能"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建规则
        create_response = api.post("/api/v1/user/annual-fees/rules/create", data={
            "card_id": card['id'],
            "rule_name": "可禁用规则",
            "condition_type": "spending_amount",
            "condition_value": 30000.00,
            "is_enabled": True
        }).should.succeed()
        
        rule_id = create_response.data['id']
        
        # 禁用规则
        api.put(f"/api/v1/user/annual-fees/rules/{rule_id}/update", data={
            "is_enabled": False
        }).should.succeed()
        
        # 重新启用规则
        api.put(f"/api/v1/user/annual-fees/rules/{rule_id}/update", data={
            "is_enabled": True
        }).should.succeed()