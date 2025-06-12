"""
用户功能API测试 - 集成测试
"""
import pytest
from tests.utils.api import APIClient
from tests.utils.assert_utils import assert_response
from tests.factories.user_factory import build_user

BASE = "/api/v1/user/profile"

class TestUserAPI:
    """用户资料管理API测试"""

    def test_get_user_info_success(self, user_and_api):
        """测试获取用户信息成功"""
        api, user = user_and_api
        resp = api.get(f"{BASE}/info")
        assert_response(resp).success().with_data(
            username=user["username"],
            email=user["email"]
        )

    def test_get_user_info_without_auth(self):
        """测试未认证获取用户信息失败"""
        api = APIClient()
        resp = api.get(f"{BASE}/info")
        assert_response(resp).fail(status_code=403)

    def test_update_user_profile_success(self, user_and_api):
        """测试更新用户资料成功"""
        api, user = user_and_api
        update_data = {
            "nickname": "新昵称",
            "phone": "13800000000",
            "timezone": "Asia/Shanghai"
        }
        resp = api.put(f"{BASE}/update", update_data)
        assert_response(resp).success().with_data(nickname="新昵称")

    def test_update_user_profile_without_auth(self):
        """测试未认证更新用户资料失败"""
        api = APIClient()
        update_data = {"nickname": "新昵称"}
        resp = api.put(f"{BASE}/update", update_data)
        assert_response(resp).fail(status_code=403)

    def test_change_password_success(self, user_and_api):
        """测试修改密码成功"""
        api, user = user_and_api
        password_data = {
            "current_password": user["password"],
            "new_password": "NewPass123456",
            "confirm_password": "NewPass123456"
        }
        resp = api.post(f"{BASE}/change-password", password_data)
        assert_response(resp).success()

    def test_change_password_wrong_current(self, user_and_api):
        """测试当前密码错误"""
        api, user = user_and_api
        password_data = {
            "current_password": "WrongPassword",
            "new_password": "NewPass123456",
            "confirm_password": "NewPass123456"
        }
        resp = api.post(f"{BASE}/change-password", password_data)
        assert_response(resp).fail(status_code=400)

    def test_change_password_mismatch(self, user_and_api):
        """测试新密码不匹配"""
        api, user = user_and_api
        password_data = {
            "current_password": user["password"],
            "new_password": "NewPass123456",
            "confirm_password": "DifferentPass123456"
        }
        resp = api.post(f"{BASE}/change-password", password_data)
        assert_response(resp).fail(status_code=400)

    def test_get_login_logs_success(self, user_and_api):
        """测试获取登录日志成功"""
        api, user = user_and_api
        resp = api.get(f"{BASE}/login-logs?page=1&page_size=10")
        assert_response(resp).success()
        # 检查分页结构
        data = resp.json()
        assert "pagination" in data
        assert data["pagination"]["current_page"] == 1

    def test_get_login_logs_pagination(self, user_and_api):
        """测试登录日志分页"""
        api, user = user_and_api
        resp = api.get(f"{BASE}/login-logs?page=2&page_size=5")
        assert_response(resp).success()

    def test_logout_success(self, user_and_api):
        """测试退出登录成功"""
        api, user = user_and_api
        resp = api.post(f"{BASE}/logout")
        assert_response(resp).success()

    def test_delete_account_success(self, user_and_api):
        """测试账户注销成功"""
        api, user = user_and_api
        deletion_data = {
            "password": user["password"],
            "reason": "测试注销"
        }
        resp = api.delete(f"{BASE}/account", deletion_data)
        assert_response(resp).success()

    def test_delete_account_wrong_password(self, user_and_api):
        """测试账户注销密码错误"""
        api, user = user_and_api
        deletion_data = {
            "password": "WrongPassword",
            "reason": "测试注销"
        }
        resp = api.delete(f"{BASE}/account", deletion_data)
        assert_response(resp).fail(status_code=400)

    def test_get_wechat_bindings_success(self, user_and_api):
        """测试获取微信绑定成功"""
        api, user = user_and_api
        resp = api.get(f"{BASE}/wechat-bindings")
        assert_response(resp).success()
        # 新用户应该没有微信绑定
        data = resp.json()
        assert isinstance(data["data"], list)

    def test_get_user_statistics_success(self, user_and_api):
        """测试获取用户统计成功"""
        api, user = user_and_api
        resp = api.get(f"{BASE}/statistics")
        assert_response(resp).success()
        # 验证统计字段存在
        data = resp.json()["data"]
        required_fields = [
            "total_cards", "active_cards", "total_transactions",
            "total_spending", "this_month_spending", "credit_utilization",
            "total_points_earned", "total_cashback_earned"
        ]
        for field in required_fields:
            assert field in data

    def test_user_profile_complete_flow(self):
        """测试用户资料管理完整流程"""
        # 1. 注册用户
        user = build_user()
        api = APIClient()
        register_resp = api.post("/api/v1/public/auth/register", user)
        assert_response(register_resp).success()

        # 2. 登录获取token
        login_resp = api.post("/api/v1/public/auth/login/username", {
            "username": user["username"],
            "password": user["password"]
        })
        assert_response(login_resp).success()
        token = login_resp.json()["data"]["access_token"]
        api.set_auth(token)

        # 3. 获取用户信息
        info_resp = api.get(f"{BASE}/info")
        assert_response(info_resp).success().with_data(username=user["username"])

        # 4. 更新用户资料
        update_data = {"nickname": "完整流程测试用户", "phone": "13812345678"}
        update_resp = api.put(f"{BASE}/update", update_data)
        assert_response(update_resp).success().with_data(nickname="完整流程测试用户")

        # 5. 获取登录日志
        logs_resp = api.get(f"{BASE}/login-logs")
        assert_response(logs_resp).success()

        # 6. 获取统计信息
        stats_resp = api.get(f"{BASE}/statistics")
        assert_response(stats_resp).success()

        # 7. 退出登录
        logout_resp = api.post(f"{BASE}/logout")
        assert_response(logout_resp).success() 