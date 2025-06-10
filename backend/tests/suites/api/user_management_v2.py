"""用户管理API测试套件 v2.0

使用新测试框架的用户管理测试
"""

from tests.framework import (
    test_suite, api_test, with_user, with_admin_user,
    performance_test, stress_test
)


@test_suite("用户管理API v2")
class UserManagementTestsV2:
    """用户管理API测试套件"""
    
    # ============= 用户注册测试 =============
    
    @api_test
    def test_user_registration_success(self, api):
        """测试用户注册成功"""
        user_data = {
            "username": "newuser123",
            "email": "newuser123@example.com", 
            "password": "TestPass123456",
            "nickname": "新用户"
        }
        
        api.post("/api/v1/public/auth/register", data=user_data).should.succeed().with_data(
            username="newuser123",
            email="newuser123@example.com"
        )
    
    @api_test
    def test_user_registration_duplicate_username(self, api):
        """测试用户名重复注册"""
        # 第一次注册成功
        user_data = {
            "username": "duplicate_user",
            "email": "first@example.com",
            "password": "TestPass123456"
        }
        api.post("/api/v1/public/auth/register", data=user_data).should.succeed()
        
        # 第二次注册相同用户名应该失败
        user_data["email"] = "second@example.com"
        api.post("/api/v1/public/auth/register", data=user_data).should.fail(409).with_error("USER_EXISTS")
    
    @api_test
    def test_user_registration_invalid_email(self, api):
        """测试无效邮箱注册"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPass123456"
        }
        
        api.post("/api/v1/public/auth/register", data=user_data).should.fail(422).with_error("VALIDATION_ERROR")
    
    # ============= 用户登录测试 =============
    
    @api_test
    @with_user
    def test_user_login_success(self, api, user):
        """测试用户登录成功"""
        # 清除之前的认证
        api.clear_auth()
        
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        
        api.post("/api/v1/public/auth/login/username", data=login_data).should.succeed().with_data(
            access_token__exists=True,
            user__username=user["username"]
        )
    
    @api_test
    @with_user
    def test_user_login_wrong_password(self, api, user):
        """测试错误密码登录"""
        api.clear_auth()
        
        login_data = {
            "username": user["username"],
            "password": "wrong_password"
        }
        
        api.post("/api/v1/public/auth/login/username", data=login_data).should.fail(401).with_error("AUTH_INVALID")
    
    @api_test
    def test_user_login_nonexistent_user(self, api):
        """测试不存在用户登录"""
        login_data = {
            "username": "nonexistent_user",
            "password": "TestPass123456"
        }
        
        api.post("/api/v1/public/auth/login/username", data=login_data).should.fail(401).with_error("USER_NOT_FOUND")
    
    # ============= 用户资料测试 =============
    
    @api_test
    @with_user
    def test_get_user_profile(self, api, user):
        """测试获取用户资料"""
        api.get("/api/v1/user/profile/info").should.succeed().with_data(
            username=user["username"],
            email=user["email"],
            nickname=user.get("nickname")
        )
    
    @api_test
    @with_user
    def test_update_user_profile(self, api, user):
        """测试更新用户资料"""
        update_data = {
            "nickname": "更新后的昵称",
            "timezone": "Asia/Shanghai"
        }
        
        api.put("/api/v1/user/profile/update", data=update_data).should.succeed()
        
        # 验证更新成功
        api.get("/api/v1/user/profile/info").should.succeed().with_data(
            nickname="更新后的昵称",
            timezone="Asia/Shanghai"
        )
    
    @api_test
    @with_user
    def test_change_password(self, api, user):
        """测试修改密码"""
        change_data = {
            "old_password": user["password"],
            "new_password": "NewTestPass123456"
        }
        
        api.post("/api/v1/user/profile/change-password", data=change_data).should.succeed()
        
        # 验证新密码可以登录
        api.clear_auth()
        login_data = {
            "username": user["username"],
            "password": "NewTestPass123456"
        }
        api.post("/api/v1/public/auth/login/username", data=login_data).should.succeed()
    
    @api_test
    @with_user
    def test_change_password_wrong_old_password(self, api, user):
        """测试修改密码 - 错误的旧密码"""
        change_data = {
            "old_password": "wrong_password",
            "new_password": "NewTestPass123456"
        }
        
        api.post("/api/v1/user/profile/change-password", data=change_data).should.fail(400).with_error("INVALID_PASSWORD")
    
    # ============= 管理员功能测试 =============
    
    @api_test
    @with_admin_user
    def test_admin_get_users_list(self, api, admin):
        """测试管理员获取用户列表"""
        api.get("/api/v1/admin/users/list?page=1&page_size=10").should.succeed().with_pagination(
            items_type="user"
        )
    
    @api_test
    @with_admin_user
    @with_user
    def test_admin_get_user_details(self, api, admin, user):
        """测试管理员获取用户详情"""
        api.get(f"/api/v1/admin/users/{user['id']}/details").should.succeed().with_data(
            username=user["username"],
            email=user["email"]
        )
    
    @api_test
    @with_admin_user
    @with_user
    def test_admin_update_user_status(self, api, admin, user):
        """测试管理员更新用户状态"""
        update_data = {"is_active": False}
        
        api.put(f"/api/v1/admin/users/{user['id']}/status", data=update_data).should.succeed()
        
        # 验证用户状态已更新
        api.get(f"/api/v1/admin/users/{user['id']}/details").should.succeed().with_data(
            is_active=False
        )
    
    @api_test
    @with_user
    def test_user_cannot_access_admin_endpoints(self, api, user):
        """测试普通用户无法访问管理员接口"""
        api.get("/api/v1/admin/users/list").should.fail(403).with_error("PERMISSION_DENIED")
    
    # ============= 权限验证测试 =============
    
    @api_test
    def test_unauthorized_access_to_user_endpoints(self, api):
        """测试未认证访问用户接口"""
        api.clear_auth()
        api.get("/api/v1/user/profile/info").should.fail(401).with_error("AUTH_REQUIRED")
    
    @api_test
    @with_user
    def test_access_other_user_data(self, api, user):
        """测试访问其他用户数据（应该被拒绝）"""
        # 尝试访问一个不存在的用户ID（模拟其他用户）
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        api.get(f"/api/v1/admin/users/{fake_user_id}/details").should.fail(403).with_error("PERMISSION_DENIED")
    
    # ============= 性能测试 =============
    
    @performance_test
    @with_user
    def test_user_profile_performance(self, api, user):
        """测试用户资料接口性能"""
        api.get("/api/v1/user/profile/info").should.succeed().complete_within(seconds=0.5)
    
    @performance_test
    @with_admin_user
    def test_admin_users_list_performance(self, api, admin):
        """测试管理员用户列表性能"""
        api.get("/api/v1/admin/users/list?page=1&page_size=50").should.succeed().complete_within(seconds=1.0)
    
    @stress_test(iterations=50)
    @with_user
    def test_login_stress(self, api, user):
        """测试登录接口压力"""
        api.clear_auth()
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        api.post("/api/v1/public/auth/login/username", data=login_data).should.succeed()
    
    # ============= 边界条件测试 =============
    
    @api_test
    def test_registration_with_minimum_password_length(self, api):
        """测试最小密码长度注册"""
        user_data = {
            "username": "minpass_user",
            "email": "minpass@example.com",
            "password": "12345678"  # 8位最小长度
        }
        
        api.post("/api/v1/public/auth/register", data=user_data).should.succeed()
    
    @api_test
    def test_registration_with_too_short_password(self, api):
        """测试密码过短注册"""
        user_data = {
            "username": "shortpass_user",
            "email": "shortpass@example.com", 
            "password": "1234567"  # 7位，低于最小长度
        }
        
        api.post("/api/v1/public/auth/register", data=user_data).should.fail(422).with_error("VALIDATION_ERROR")
    
    @api_test
    def test_registration_with_long_username(self, api):
        """测试超长用户名注册"""
        user_data = {
            "username": "a" * 51,  # 超过50字符限制
            "email": "longname@example.com",
            "password": "TestPass123456"
        }
        
        api.post("/api/v1/public/auth/register", data=user_data).should.fail(422).with_error("VALIDATION_ERROR")
    
    # ============= 数据一致性测试 =============
    
    @api_test
    @with_user
    def test_user_data_consistency_after_update(self, api, user):
        """测试用户数据更新后的一致性"""
        # 更新昵称
        update_data = {"nickname": "一致性测试昵称"}
        api.put("/api/v1/user/profile/update", data=update_data).should.succeed()
        
        # 从不同接口验证数据一致性
        profile_response = api.get("/api/v1/user/profile/info").should.succeed()
        
        # 验证昵称已更新
        assert profile_response.data["data"]["nickname"] == "一致性测试昵称" 