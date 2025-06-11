import pytest
from app.services.auth_service import AuthService
from app.models.schemas.auth import RegisterRequest, LoginRequest
from sqlalchemy.orm import Session
from tests.utils.db import create_test_session

@pytest.fixture
def db():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

class TestAuthService:
    def test_register_and_authenticate(self, db: Session):
        reg_data = RegisterRequest(
            username="testuser",
            email="testuser@example.com",
            password="TestPass123456",
            nickname="测试用户"
        )
        user = AuthService.register(db, reg_data)
        assert user.username == "testuser"
        login_data = LoginRequest(
            username="testuser",
            password="TestPass123456"
        )
        user2 = AuthService.authenticate(db, login_data)
        assert user2.id == user.id

    def test_register_duplicate(self, db: Session):
        reg_data = RegisterRequest(
            username="dupuser",
            email="dupuser@example.com",
            password="TestPass123456",
            nickname="重复用户"
        )
        AuthService.register(db, reg_data)
        with pytest.raises(Exception):
            AuthService.register(db, reg_data) 