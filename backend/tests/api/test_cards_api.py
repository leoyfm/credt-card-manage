"""信用卡API测试示例

展示如何使用数据工厂创建测试数据
"""
import pytest
from tests.framework.clients.api import APIClient
from tests.utils.assert_utils import assert_response
from tests.factories.user_factory import build_user, build_simple_user
from tests.factories.card_factory import (
    build_card, build_simple_card, build_premium_card, 
    build_template_card, build_cards_batch
)
from tests.factories.transaction_factory import (
    build_transaction, build_template_transaction, build_transactions_batch
)


class TestCardsAPI:
    """信用卡API测试类"""
    
    def test_create_card_success(self, user_and_api):
        """测试创建信用卡成功"""
        api, user = user_and_api
        
        # 使用数据工厂创建信用卡数据
        card_data = build_simple_card(
            card_name="测试招商银行信用卡",
            bank_name="招商银行"
        )
        
        resp = api.post("/api/v1/user/cards/create", card_data)
        assert_response(resp).success().with_data(
            card_name=card_data["card_name"],
            bank_name=card_data["bank_name"]
        )
    
    def test_create_premium_card(self, user_and_api):
        """测试创建高端信用卡"""
        api, user = user_and_api
        
        # 使用高端卡工厂
        card_data = build_premium_card(
            card_name="浦发银行AE白金卡",
            bank_name="浦发银行"
        )
        
        resp = api.post("/api/v1/user/cards/create", card_data)
        assert_response(resp).success()
        
        # 验证高端卡特有属性
        data = resp.json()["data"]
        assert data["card_level"] == "无限卡"
        assert float(data["credit_limit"]) >= 1000000.0
    
    def test_create_template_card(self, user_and_api):
        """测试使用模板创建信用卡"""
        api, user = user_and_api
        
        # 使用预定义模板
        card_data = build_template_card("招商经典白金")
        
        resp = api.post("/api/v1/user/cards/create", card_data)
        assert_response(resp).success().with_data(
            bank_name="招商银行",
            card_level="白金卡"
        )
    
    def test_get_cards_list(self, user_and_api):
        """测试获取信用卡列表"""
        api, user = user_and_api
        
        # 批量创建多张卡
        cards_data = build_cards_batch(count=3)
        for card_data in cards_data:
            api.post("/api/v1/user/cards/create", card_data)
        
        # 获取列表
        resp = api.get("/api/v1/user/cards/list")
        assert_response(resp).success()
        
        data = resp.json()["data"]
        assert len(data) >= 3  # 至少有3张卡
    
    def test_create_card_with_invalid_data(self, user_and_api):
        """测试创建信用卡失败 - 无效数据"""
        api, user = user_and_api
        
        # 创建无效的卡片数据
        invalid_card = {
            "card_name": "",  # 空名称
            "credit_limit": -1000  # 负数额度
        }
        
        resp = api.post("/api/v1/user/cards/create", invalid_card)
        assert_response(resp).fail()
    
    def test_update_card(self, user_and_api):
        """测试更新信用卡信息"""
        api, user = user_and_api
        
        # 先创建一张卡
        card_data = build_simple_card()
        create_resp = api.post("/api/v1/user/cards/create", card_data)
        card_id = create_resp.json()["data"]["id"]
        
        # 更新卡片信息
        update_data = {
            "card_name": "更新后的卡片名称",
            "credit_limit": "80000.00"
        }
        
        resp = api.put(f"/api/v1/user/cards/{card_id}/update", update_data)
        assert_response(resp).success().with_data(
            card_name=update_data["card_name"]
        )
    
    def test_delete_card(self, user_and_api):
        """测试删除信用卡"""
        api, user = user_and_api
        
        # 先创建一张卡
        card_data = build_simple_card()
        create_resp = api.post("/api/v1/user/cards/create", card_data)
        card_id = create_resp.json()["data"]["id"]
        
        # 删除卡片
        resp = api.delete(f"/api/v1/user/cards/{card_id}/delete")
        assert_response(resp).success()
        
        # 验证卡片已删除
        get_resp = api.get(f"/api/v1/user/cards/{card_id}/details")
        assert_response(get_resp).fail(status_code=404)
    
    def test_card_with_transactions(self, user_and_api):
        """测试带交易记录的信用卡"""
        api, user = user_and_api
        
        # 创建信用卡
        card_data = build_simple_card()
        create_resp = api.post("/api/v1/user/cards/create", card_data)
        card_id = create_resp.json()["data"]["id"]
        
        # 为这张卡创建交易记录
        transactions_data = build_transactions_batch(count=5)
        for transaction_data in transactions_data:
            transaction_data["card_id"] = card_id
            api.post("/api/v1/user/transactions/create", transaction_data)
        
        # 获取卡片详情，应该包含交易统计
        resp = api.get(f"/api/v1/user/cards/{card_id}/details")
        assert_response(resp).success()
        
        # 可以验证交易相关的统计信息
        data = resp.json()["data"]
        # 这里可以根据实际API响应结构进行验证
    
    def test_create_different_card_types(self, user_and_api):
        """测试创建不同类型的信用卡"""
        api, user = user_and_api
        
        # 测试不同的预定义模板
        templates = ["招商经典白金", "建行龙卡", "浦发AE白"]
        
        for template_name in templates:
            card_data = build_template_card(template_name)
            resp = api.post("/api/v1/user/cards/create", card_data)
            assert_response(resp).success()
            
            # 验证每种卡的特有属性
            data = resp.json()["data"]
            if template_name == "招商经典白金":
                assert data["bank_name"] == "招商银行"
                assert data["card_network"] == "VISA"
            elif template_name == "建行龙卡":
                assert data["bank_name"] == "建设银行"
                assert data["card_network"] == "银联"
            elif template_name == "浦发AE白":
                assert data["bank_name"] == "浦发银行"
                assert data["card_network"] == "American Express"


class TestCardsPermissions:
    """信用卡权限测试类"""
    
    def test_cannot_access_other_user_cards(self):
        """测试无法访问其他用户的信用卡"""
        # 创建两个用户
        user1_data = build_simple_user()
        user2_data = build_simple_user()
        
        api1 = APIClient()
        api2 = APIClient()
        
        # 注册并登录两个用户
        api1.post("/api/v1/public/auth/register", user1_data)
        login1_resp = api1.post("/api/v1/public/auth/login/username", {
            "username": user1_data["username"],
            "password": user1_data["password"]
        })
        api1.set_auth(login1_resp.json()["data"]["access_token"])
        
        api2.post("/api/v1/public/auth/register", user2_data)
        login2_resp = api2.post("/api/v1/public/auth/login/username", {
            "username": user2_data["username"],
            "password": user2_data["password"]
        })
        api2.set_auth(login2_resp.json()["data"]["access_token"])
        
        # 用户1创建信用卡
        card_data = build_simple_card()
        create_resp = api1.post("/api/v1/user/cards/create", card_data)
        card_id = create_resp.json()["data"]["id"]
        
        # 用户2尝试访问用户1的信用卡，应该失败
        resp = api2.get(f"/api/v1/user/cards/{card_id}/details")
        assert_response(resp).fail(status_code=403)
    
    def test_unauthenticated_access_denied(self):
        """测试未认证用户无法访问信用卡接口"""
        api = APIClient()  # 未设置认证令牌
        
        resp = api.get("/api/v1/user/cards/list")
        assert_response(resp).fail(status_code=401)


@pytest.fixture
def user_and_api():
    """创建用户并返回已认证的API客户端"""
    user = build_simple_user()
    api = APIClient()
    
    # 注册用户
    api.post("/api/v1/public/auth/register", user)
    
    # 登录获取令牌
    login_resp = api.post("/api/v1/public/auth/login/username", {
        "username": user["username"],
        "password": user["password"]
    })
    
    token = login_resp.json()["data"]["access_token"]
    api.set_auth(token)
    
    return api, user 