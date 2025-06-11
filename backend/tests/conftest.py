import pytest
from tests.factories.user_factory import build_user
from tests.utils.api import APIClient

@pytest.fixture
def user_and_api():
    user = build_user()
    api = APIClient()
    api.post("/api/v1/public/auth/register", user)
    resp = api.post("/api/v1/public/auth/login/username", {
        "username": user["username"],
        "password": user["password"]
    })
    token = None
    try:
        token = resp.json().get("data", {}).get("access_token")
    except Exception:
        pass
    if token:
        api.set_auth(token)
    return api, user 