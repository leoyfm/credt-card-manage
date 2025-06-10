"""
用户管理API测试套件

使用新测试框架的极简API，展示框架的强大功能。
"""

from tests.framework import (
    test_suite, api_test, test_scenario,
    with_user, with_cards, with_transactions, with_admin_user,
    performance_test, benchmark,
    tags, priority, description
)


@test_suite("用户管理API", description="测试用户相关的所有API接口")
class UserManagementTests:
    """用户管理API测试套件"""
    
    @api_test
    @tags("smoke", "auth")
    @priority(1)
    @description("测试用户注册功能")
    def test_user_registration(self, api):
        """测试用户注册"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "nickname": "新用户"
        }
        
        api.post("/api/v1/public/auth/register", data=user_data).should.succeed().with_data(
            username="newuser",
            email="newuser@example.com",
            nickname="新用户"
        )
    
    @api_test
    @with_user
    @tags("smoke", "auth")
    @priority(1)
    def test_user_login(self, api, user):
        """测试用户登录"""
        # 清除认证，测试登录流程
        api.clear_auth()
        
        api.post("/api/v1/public/auth/login/username", data={
            "username": user.username,
            "password": user.password
        }).should.succeed().with_data(
            access_token__exists=True,
            user__username=user.username,
            user__email=user.email
        )
    
    @api_test
    @with_user
    @tags("profile")
    def test_get_user_profile(self, api, user):
        """测试获取用户资料"""
        api.get("/api/v1/user/profile").should.succeed().with_data(
            username=user.username,
            email=user.email,
            nickname=user.nickname
        )
    
    @api_test
    @with_user
    @tags("profile")
    def test_update_user_profile(self, api, user):
        """测试更新用户资料"""
        updated_data = {
            "nickname": "更新后的昵称",
            "phone": "13800138000"
        }
        
        api.put("/api/v1/user/profile/update", data=updated_data).should.succeed()
        
        # 验证更新结果
        api.get("/api/v1/user/profile").should.succeed().with_data(
            nickname="更新后的昵称",
            phone="13800138000"
        )
    
    @api_test
    @with_user
    @with_cards(count=3, bank="招商银行")
    @tags("cards")
    def test_get_user_cards(self, api, user, cards):
        """测试获取用户信用卡列表"""
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=3,
            items_type="card"
        )
        
        # 验证所有卡片都是招商银行
        response = api.get("/api/v1/user/cards/list")
        for card in response.data:
            assert card["bank_name"] == "招商银行"
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=50)
    @tags("statistics")
    def test_user_statistics(self, api, user, cards, transactions):
        """测试用户统计信息"""
        api.get("/api/v1/user/statistics/overview").should.succeed().with_data(
            total_cards__gte=2,
            total_transactions__gte=50,
            total_spending__gt=0
        )
    
    @api_test
    @with_user
    @tags("settings")
    def test_change_password(self, api, user):
        """测试修改密码"""
        new_password = "NewSecurePass123"
        
        api.put("/api/v1/user/security/change-password", data={
            "old_password": user.password,
            "new_password": new_password,
            "confirm_password": new_password
        }).should.succeed()
        
        # 验证新密码可以登录
        api.clear_auth()
        api.post("/api/v1/public/auth/login/username", data={
            "username": user.username,
            "password": new_password
        }).should.succeed()
    
    @api_test
    @with_user
    @tags("error_handling")
    def test_invalid_profile_update(self, api, user):
        """测试无效的资料更新"""
        invalid_data = {
            "email": "invalid-email",  # 无效邮箱格式
            "phone": "123"             # 无效手机号
        }
        
        api.put("/api/v1/user/profile/update", data=invalid_data).should.fail(
            status_code=400
        ).with_error(
            error_code="VALIDATION_ERROR"
        )


@test_suite("用户管理性能测试", description="测试用户相关API的性能表现")
class UserManagementPerformanceTests:
    """用户管理性能测试"""
    
    @performance_test
    @benchmark(max_time=0.5)
    @with_user
    @tags("performance", "smoke")
    def test_profile_performance(self, api, user):
        """用户资料接口性能基准"""
        api.get("/api/v1/user/profile").should.succeed().complete_within(seconds=0.5)
    
    @performance_test
    @benchmark(max_time=1.0)
    @with_user
    @with_cards(count=20)
    @tags("performance")
    def test_cards_list_performance(self, api, user, cards):
        """信用卡列表接口性能测试"""
        api.get("/api/v1/user/cards/list", params={
            "page": 1,
            "page_size": 20
        }).should.succeed().complete_within(seconds=1.0)
    
    @performance_test
    @benchmark(max_time=2.0)
    @with_user
    @with_cards(count=5)
    @with_transactions(count=1000)
    @tags("performance", "heavy")
    def test_statistics_performance_with_large_data(self, api, user, cards, transactions):
        """大数据量下的统计接口性能"""
        api.get("/api/v1/user/statistics/overview").should.succeed().complete_within(seconds=2.0)


@test_scenario("用户完整工作流", description="模拟用户从注册到使用的完整流程")
class UserCompleteWorkflowScenario:
    """用户完整工作流场景测试"""
    
    @api_test
    @tags("scenario", "e2e")
    def test_complete_user_journey(self, api):
        """完整用户使用流程"""
        
        # 步骤1：用户注册
        user_data = {
            "username": "journey_user",
            "email": "journey@example.com", 
            "password": "JourneyPass123",
            "nickname": "旅程用户"
        }
        
        register_response = api.post("/api/v1/public/auth/register", data=user_data)
        register_response.should.succeed()
        
        # 步骤2：用户登录
        login_response = api.post("/api/v1/public/auth/login/username", data={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        login_response.should.succeed()
        
        # 设置认证
        api.set_auth(login_response.data["access_token"])
        
        # 步骤3：完善用户资料
        api.put("/api/v1/user/profile/update", data={
            "phone": "13800138000",
            "address": "测试地址"
        }).should.succeed()
        
        # 步骤4：添加信用卡
        card_data = {
            "card_name": "我的第一张信用卡",
            "bank_name": "招商银行",
            "card_number": "6225888888888888",
            "credit_limit": 100000.00,
            "expiry_month": 12,
            "expiry_year": 2028
        }
        
        card_response = api.post("/api/v1/user/cards/create", data=card_data)
        card_response.should.succeed()
        card_id = card_response.data["id"]
        
        # 步骤5：添加交易记录
        transaction_data = {
            "card_id": card_id,
            "amount": 299.99,
            "merchant_name": "超市购物",
            "category": "grocery",
            "transaction_type": "expense"
        }
        
        api.post("/api/v1/user/transactions/create", data=transaction_data).should.succeed()
        
        # 步骤6：查看统计信息
        api.get("/api/v1/user/statistics/overview").should.succeed().with_data(
            total_cards=1,
            total_transactions=1,
            total_spending=299.99
        )
        
        # 步骤7：设置年费规则
        annual_fee_data = {
            "card_id": card_id,
            "condition_type": "spending_amount",
            "condition_value": 50000,
            "description": "消费满5万免年费"
        }
        
        api.post("/api/v1/user/annual-fees/rules/create", data=annual_fee_data).should.succeed()
        
        # 步骤8：验证完整性
        api.get("/api/v1/user/profile").should.succeed().with_data(
            username="journey_user",
            phone="13800138000"
        )
        
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=1
        )


@test_suite("管理员用户管理", description="测试管理员对用户的管理功能")
class AdminUserManagementTests:
    """管理员用户管理测试"""
    
    @api_test
    @with_admin_user
    @tags("admin", "management")
    def test_admin_get_users_list(self, api, admin):
        """测试管理员获取用户列表"""
        api.get("/api/v1/admin/users/list").should.succeed().with_pagination()
    
    @api_test
    @with_admin_user
    @with_user
    @tags("admin", "management")
    def test_admin_update_user_status(self, api, admin, user):
        """测试管理员更新用户状态"""
        # 禁用用户
        api.put(f"/api/v1/admin/users/{user.id}/status", data={
            "is_active": False,
            "reason": "测试禁用"
        }).should.succeed()
        
        # 验证用户状态
        api.get(f"/api/v1/admin/users/{user.id}/details").should.succeed().with_data(
            is_active=False
        )
    
    @api_test
    @with_admin_user
    @tags("admin", "statistics")
    def test_admin_get_system_statistics(self, api, admin):
        """测试管理员获取系统统计"""
        api.get("/api/v1/admin/statistics/system").should.succeed().with_data(
            total_users__gte=0,
            active_users__gte=0,
            total_cards__gte=0,
            total_transactions__gte=0
        ) 