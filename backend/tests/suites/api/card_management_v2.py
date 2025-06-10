"""信用卡管理API测试套件 v2.0

使用新测试框架的信用卡管理测试
"""

from tests.framework import (
    test_suite, api_test, with_user, with_cards, 
    with_user_and_cards, performance_test
)
from tests.framework.factories import CardFactory


@test_suite("信用卡管理API v2")
class CardManagementTestsV2:
    """信用卡管理API测试套件"""
    
    # ============= 信用卡创建测试 =============
    
    @api_test
    @with_user
    def test_create_card_success(self, api, user):
        """测试创建信用卡成功"""
        card_data = CardFactory().build()
        
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().with_data(
            card_name=card_data["card_name"],
            bank_name=card_data["bank_name"],
            credit_limit=card_data["credit_limit"]
        )
    
    @api_test
    @with_user
    def test_create_card_with_cmb_bank(self, api, user):
        """测试创建招商银行信用卡"""
        card_data = CardFactory().cmb().build()
        
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().with_data(
            bank_name="招商银行",
            card_network="VISA"
        )
    
    @api_test
    @with_user
    def test_create_card_invalid_data(self, api, user):
        """测试创建信用卡 - 无效数据"""
        card_data = {
            "card_name": "",  # 空名称
            "bank_name": "测试银行",
            "credit_limit": -1000  # 负数额度
        }
        
        api.post("/api/v1/user/cards/create", data=card_data).should.fail(422).with_error("VALIDATION_ERROR")
    
    @api_test
    @with_user
    def test_create_card_duplicate_number(self, api, user):
        """测试创建重复卡号的信用卡"""
        card_data = CardFactory().build()
        
        # 第一次创建成功
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed()
        
        # 第二次创建相同卡号应该失败
        api.post("/api/v1/user/cards/create", data=card_data).should.fail(409).with_error("CARD_EXISTS")
    
    # ============= 信用卡查询测试 =============
    
    @api_test
    @with_user_and_cards(count=3)
    def test_get_cards_list(self, api, user, cards):
        """测试获取信用卡列表"""
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=3,
            items_type="card"
        )
    
    @api_test
    @with_user_and_cards(count=1)
    def test_get_card_details(self, api, user, cards):
        """测试获取信用卡详情"""
        card = cards[0] if isinstance(cards, list) else cards
        
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            id=card["id"],
            card_name=card["card_name"],
            bank_name=card["bank_name"]
        )
    
    @api_test
    @with_user
    def test_get_nonexistent_card(self, api, user):
        """测试获取不存在的信用卡"""
        fake_card_id = "00000000-0000-0000-0000-000000000000"
        
        api.get(f"/api/v1/user/cards/{fake_card_id}/details").should.fail(404).with_error("CARD_NOT_FOUND")
    
    @api_test
    @with_user_and_cards(count=5, bank_name="招商银行")
    def test_get_cards_list_with_filter(self, api, user, cards):
        """测试带筛选的信用卡列表"""
        api.get("/api/v1/user/cards/list?bank_name=招商银行").should.succeed().with_pagination(
            total_items=5
        )
    
    # ============= 信用卡更新测试 =============
    
    @api_test
    @with_user_and_cards(count=1)
    def test_update_card_success(self, api, user, cards):
        """测试更新信用卡成功"""
        card = cards[0] if isinstance(cards, list) else cards
        
        update_data = {
            "card_name": "更新后的卡片名称",
            "credit_limit": 80000
        }
        
        api.put(f"/api/v1/user/cards/{card['id']}/update", data=update_data).should.succeed()
        
        # 验证更新成功
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            card_name="更新后的卡片名称",
            credit_limit=80000
        )
    
    @api_test
    @with_user_and_cards(count=1)
    def test_update_card_status(self, api, user, cards):
        """测试更新信用卡状态"""
        card = cards[0] if isinstance(cards, list) else cards
        
        status_data = {"status": "frozen"}
        
        api.put(f"/api/v1/user/cards/{card['id']}/status", data=status_data).should.succeed()
        
        # 验证状态更新
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            status="frozen"
        )
    
    @api_test
    @with_user_and_cards(count=1)
    def test_update_card_invalid_status(self, api, user, cards):
        """测试更新信用卡 - 无效状态"""
        card = cards[0] if isinstance(cards, list) else cards
        
        status_data = {"status": "invalid_status"}
        
        api.put(f"/api/v1/user/cards/{card['id']}/status", data=status_data).should.fail(422).with_error("VALIDATION_ERROR")
    
    # ============= 信用卡删除测试 =============
    
    @api_test
    @with_user_and_cards(count=1)
    def test_delete_card_success(self, api, user, cards):
        """测试删除信用卡成功"""
        card = cards[0] if isinstance(cards, list) else cards
        
        api.delete(f"/api/v1/user/cards/{card['id']}/delete").should.succeed()
        
        # 验证卡片已删除
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.fail(404).with_error("CARD_NOT_FOUND")
    
    @api_test
    @with_user
    def test_delete_nonexistent_card(self, api, user):
        """测试删除不存在的信用卡"""
        fake_card_id = "00000000-0000-0000-0000-000000000000"
        
        api.delete(f"/api/v1/user/cards/{fake_card_id}/delete").should.fail(404).with_error("CARD_NOT_FOUND")
    
    # ============= 主卡设置测试 =============
    
    @api_test
    @with_user_and_cards(count=3)
    def test_set_primary_card(self, api, user, cards):
        """测试设置主卡"""
        card = cards[0]
        
        # 设置为主卡
        primary_data = {"is_primary": True}
        api.put(f"/api/v1/user/cards/{card['id']}/update", data=primary_data).should.succeed()
        
        # 验证主卡设置成功
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().with_data(
            is_primary=True
        )
        
        # 验证其他卡片不再是主卡
        for other_card in cards[1:]:
            api.get(f"/api/v1/user/cards/{other_card['id']}/details").should.succeed().with_data(
                is_primary=False
            )
    
    # ============= 权限验证测试 =============
    
    @api_test
    def test_unauthorized_access_to_cards(self, api):
        """测试未认证访问信用卡接口"""
        api.clear_auth()
        api.get("/api/v1/user/cards/list").should.fail(401).with_error("AUTH_REQUIRED")
    
    @api_test
    @with_user_and_cards(count=1, username="user1")
    @with_user(username="user2")
    def test_access_other_user_cards(self, api, user1_cards, user2):
        """测试访问其他用户的信用卡"""
        user1_card = user1_cards[0]
        
        # 切换到user2的认证
        api.login_as_user(user2)
        
        # 尝试访问user1的信用卡应该失败
        api.get(f"/api/v1/user/cards/{user1_card['id']}/details").should.fail(403).with_error("PERMISSION_DENIED")
    
    # ============= 业务流程测试 =============
    
    @api_test
    @with_user
    def test_complete_card_lifecycle(self, api, user):
        """测试信用卡完整生命周期"""
        # 1. 创建信用卡
        card_data = CardFactory().cmb().build()
        create_response = api.post("/api/v1/user/cards/create", data=card_data).should.succeed()
        card_id = create_response.data["data"]["id"]
        
        # 2. 查看卡片详情
        api.get(f"/api/v1/user/cards/{card_id}/details").should.succeed().with_data(
            bank_name="招商银行"
        )
        
        # 3. 更新卡片信息
        update_data = {"card_name": "我的主力卡"}
        api.put(f"/api/v1/user/cards/{card_id}/update", data=update_data).should.succeed()
        
        # 4. 设置为主卡
        primary_data = {"is_primary": True}
        api.put(f"/api/v1/user/cards/{card_id}/update", data=primary_data).should.succeed()
        
        # 5. 冻结卡片
        freeze_data = {"status": "frozen"}
        api.put(f"/api/v1/user/cards/{card_id}/status", data=freeze_data).should.succeed()
        
        # 6. 验证最终状态
        api.get(f"/api/v1/user/cards/{card_id}/details").should.succeed().with_data(
            card_name="我的主力卡",
            is_primary=True,
            status="frozen",
            bank_name="招商银行"
        )
    
    @api_test
    @with_user
    def test_create_multiple_bank_cards(self, api, user):
        """测试创建多家银行信用卡"""
        banks = ["招商银行", "工商银行", "建设银行"]
        card_ids = []
        
        for bank in banks:
            card_data = CardFactory().build()
            card_data["bank_name"] = bank
            card_data["card_name"] = f"{bank}信用卡"
            
            response = api.post("/api/v1/user/cards/create", data=card_data).should.succeed()
            card_ids.append(response.data["data"]["id"])
        
        # 验证所有卡片都已创建
        cards_response = api.get("/api/v1/user/cards/list").should.succeed()
        assert len(cards_response.data["data"]) == 3
        
        # 验证每张卡片的银行信息
        for i, bank in enumerate(banks):
            api.get(f"/api/v1/user/cards/{card_ids[i]}/details").should.succeed().with_data(
                bank_name=bank,
                card_name=f"{bank}信用卡"
            )
    
    # ============= 性能测试 =============
    
    @performance_test
    @with_user_and_cards(count=10)
    def test_cards_list_performance(self, api, user, cards):
        """测试信用卡列表性能"""
        api.get("/api/v1/user/cards/list").should.succeed().complete_within(seconds=1.0)
    
    @performance_test
    @with_user_and_cards(count=1)
    def test_card_details_performance(self, api, user, cards):
        """测试信用卡详情性能"""
        card = cards[0] if isinstance(cards, list) else cards
        api.get(f"/api/v1/user/cards/{card['id']}/details").should.succeed().complete_within(seconds=0.5)
    
    @performance_test
    @with_user
    def test_card_creation_performance(self, api, user):
        """测试信用卡创建性能"""
        card_data = CardFactory().build()
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().complete_within(seconds=2.0)
    
    # ============= 边界条件测试 =============
    
    @api_test
    @with_user
    def test_create_card_with_maximum_credit_limit(self, api, user):
        """测试创建最大信用额度的信用卡"""
        card_data = CardFactory().build()
        card_data["credit_limit"] = 9999999.99  # 最大额度
        
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().with_data(
            credit_limit=9999999.99
        )
    
    @api_test
    @with_user
    def test_create_card_with_minimum_credit_limit(self, api, user):
        """测试创建最小信用额度的信用卡"""
        card_data = CardFactory().build()
        card_data["credit_limit"] = 1000.00  # 最小额度
        
        api.post("/api/v1/user/cards/create", data=card_data).should.succeed().with_data(
            credit_limit=1000.00
        )
    
    @api_test
    @with_user
    def test_create_card_with_invalid_expiry_date(self, api, user):
        """测试创建过期日期无效的信用卡"""
        card_data = CardFactory().build()
        card_data["expiry_year"] = 2020  # 过期年份
        card_data["expiry_month"] = 12
        
        api.post("/api/v1/user/cards/create", data=card_data).should.fail(422).with_error("VALIDATION_ERROR")
    
    # ============= 分页测试 =============
    
    @api_test
    @with_user_and_cards(count=25)
    def test_cards_list_pagination(self, api, user, cards):
        """测试信用卡列表分页"""
        # 第一页
        page1_response = api.get("/api/v1/user/cards/list?page=1&page_size=10").should.succeed()
        assert len(page1_response.data["data"]) == 10
        assert page1_response.data["pagination"]["current_page"] == 1
        assert page1_response.data["pagination"]["total"] == 25
        assert page1_response.data["pagination"]["has_next"] is True
        
        # 第二页  
        page2_response = api.get("/api/v1/user/cards/list?page=2&page_size=10").should.succeed()
        assert len(page2_response.data["data"]) == 10
        assert page2_response.data["pagination"]["current_page"] == 2
        assert page2_response.data["pagination"]["has_prev"] is True
        
        # 最后一页
        page3_response = api.get("/api/v1/user/cards/list?page=3&page_size=10").should.succeed()
        assert len(page3_response.data["data"]) == 5  # 剩余5张卡
        assert page3_response.data["pagination"]["has_next"] is False 