import pytest
from tests.utils.api import APIClient
from tests.utils.assert_utils import assert_response
from tests.factories.user_factory import build_user

BASE = "/api/v1/public/auth"

class TestAuthAPI:
    def test_register_success(self):
        user = build_user()
        api = APIClient()
        resp = api.post(f"{BASE}/register", user)
        assert_response(resp).success().with_data(username=user["username"])

    def test_register_duplicate(self):
        user = build_user()
        api = APIClient()
        api.post(f"{BASE}/register", user)
        resp = api.post(f"{BASE}/register", user)
        assert_response(resp).fail()

    def test_register_username_exists(self):
        user = build_user()
        api = APIClient()
        api.post(f"{BASE}/register", user)
        user2 = user.copy()
        user2["email"] = "apitest_user2b@ex.com"
        resp = api.post(f"{BASE}/register", user2)
        assert_response(resp).fail()

    def test_register_email_exists(self):
        user1 = build_user()
        user2 = build_user(email=user1["email"])
        api = APIClient()
        api.post(f"{BASE}/register", user1)
        resp = api.post(f"{BASE}/register", user2)
        assert_response(resp).fail()

    def test_register_invalid_email(self):
        api = APIClient()
        resp = api.post(f"{BASE}/register", {
            "username": "apitest_user5",
            "email": "not-an-email",
            "password": "TestPass123456"
        })
        assert_response(resp).fail(status_code=422)

    def test_register_weak_password(self):
        api = APIClient()
        resp = api.post(f"{BASE}/register", {
            "username": "apitest_user6",
            "email": "apitest_user6@ex.com",
            "password": "123"
        })
        assert resp.status_code in (200, 400, 422)

    def test_register_missing_fields(self):
        api = APIClient()
        resp = api.post(f"{BASE}/register", {
            "username": "abc"
        })
        assert_response(resp).fail(status_code=422)

    def test_login_success(self, user_and_api):
        api, user = user_and_api
        resp = api.post(f"{BASE}/login/username", {
            "username": user["username"],
            "password": user["password"]
        })
        assert_response(resp).success().with_data(username=user["username"])

    def test_login_wrong_password(self, user_and_api):
        api, user = user_and_api
        resp = api.post(f"{BASE}/login/username", {
            "username": user["username"],
            "password": "WrongPass123"
        })
        assert_response(resp).fail()

    def test_login_user_not_exist(self):
        api = APIClient()
        resp = api.post(f"{BASE}/login/username", {
            "username": "not_exist_user",
            "password": "AnyPass123"
        })
        assert_response(resp).fail()

    def test_login_missing_fields(self):
        api = APIClient()
        resp = api.post(f"{BASE}/login/username", {
            "username": "abc"
        })
        assert_response(resp).fail(status_code=422)

    def test_refresh_token_success(self, user_and_api):
        api, user = user_and_api
        reg = api.post(f"{BASE}/login/username", {
            "username": user["username"],
            "password": user["password"]
        })
        tokens = reg.json().get("data", {})
        resp = api.post(f"{BASE}/refresh-token", {
            "refresh_token": tokens.get("refresh_token")
        })
        assert_response(resp).success()

    def test_refresh_token_invalid(self):
        api = APIClient()
        resp = api.post(f"{BASE}/refresh-token", {
            "refresh_token": "invalidtoken"
        })
        assert_response(resp).fail(status_code=401)

    def test_refresh_token_wrong_type(self, user_and_api):
        api, user = user_and_api
        reg = api.post(f"{BASE}/login/username", {
            "username": user["username"],
            "password": user["password"]
        })
        tokens = reg.json().get("data", {})
        resp = api.post(f"{BASE}/refresh-token", {
            "refresh_token": tokens.get("access_token")
        })
        assert_response(resp).fail(status_code=401)

    def test_refresh_token_missing(self):
        api = APIClient()
        resp = api.post(f"{BASE}/refresh-token", {})
        assert_response(resp).fail(status_code=422) 