"""
用户服务单元测试 - 直连测试数据库
"""
import pytest
import bcrypt
from unittest.mock import Mock
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.user_service import UserService
from app.models.database.user import User, LoginLog
from app.models.schemas.user import (
    UserProfileUpdateRequest,
    ChangePasswordRequest,
    AccountDeletionRequest
)
from app.core.exceptions.custom import (
    AuthenticationError, ValidationError, ResourceNotFoundError
)
from tests.utils.db import create_test_session

@pytest.fixture
def db_session():
    """测试数据库会话"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def user_service(db_session: Session):
    """用户服务实例"""
    return UserService(db_session)

@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户"""
    import uuid
    timestamp = str(uuid.uuid4())[:8]
    
    password = "TestPass123456"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # 为每个测试创建唯一的用户名和邮箱
    username = f"testuser_{timestamp}"
    email = f"testuser_{timestamp}@example.com"
    
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password.decode('utf-8'),
        nickname="测试用户",
        phone="13800000000"
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # 为测试方便，添加原始密码属性
    user._original_password = password
    return user

class TestUserService:
    """用户服务测试类"""

    def test_get_user_profile_success(self, user_service: UserService, test_user: User):
        """测试获取用户资料成功"""
        profile = user_service.get_user_profile(str(test_user.id))
        
        assert profile.username == test_user.username
        assert profile.email == test_user.email
        assert profile.nickname == test_user.nickname
        assert profile.phone == test_user.phone

    def test_get_user_profile_not_found(self, user_service: UserService):
        """测试获取不存在用户的资料"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_profile(fake_id)
        
        assert exc_info.value.status_code == 404
        assert "用户不存在" in str(exc_info.value.detail)

    def test_update_user_profile_success(self, user_service: UserService, test_user: User):
        """测试更新用户资料成功"""
        update_data = UserProfileUpdateRequest(
            nickname="更新后的昵称",
            phone="13912345678",
            timezone="Asia/Tokyo"
        )
        
        updated_profile = user_service.update_user_profile(str(test_user.id), update_data)
        
        assert updated_profile.nickname == "更新后的昵称"
        assert updated_profile.phone == "13912345678"
        assert updated_profile.timezone == "Asia/Tokyo"

    def test_update_user_profile_partial(self, user_service: UserService, test_user: User):
        """测试部分更新用户资料"""
        update_data = UserProfileUpdateRequest(nickname="新昵称")
        
        updated_profile = user_service.update_user_profile(str(test_user.id), update_data)
        
        assert updated_profile.nickname == "新昵称"
        assert updated_profile.phone == test_user.phone  # 保持原值

    def test_change_password_success(self, user_service: UserService, test_user: User):
        """测试修改密码成功"""
        password_data = ChangePasswordRequest(
            current_password=test_user._original_password,
            new_password="NewPass123456",
            confirm_password="NewPass123456"
        )
        
        result = user_service.change_password(str(test_user.id), password_data)
        
        assert result is True
        
        # 验证密码已更改
        db_session = user_service.db
        user = db_session.query(User).filter(User.id == test_user.id).first()
        assert bcrypt.checkpw("NewPass123456".encode('utf-8'), user.password_hash.encode('utf-8'))

    def test_change_password_wrong_current(self, user_service: UserService, test_user: User):
        """测试当前密码错误"""
        password_data = ChangePasswordRequest(
            current_password="WrongPassword",
            new_password="NewPass123456",
            confirm_password="NewPass123456"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            user_service.change_password(str(test_user.id), password_data)
        
        assert exc_info.value.status_code == 401
        assert "当前密码错误" in str(exc_info.value.detail["message"])

    def test_change_password_mismatch(self, user_service: UserService, test_user: User):
        """测试新密码不匹配"""
        password_data = ChangePasswordRequest(
            current_password=test_user._original_password,
            new_password="NewPass123456",
            confirm_password="DifferentPass123456"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            user_service.change_password(str(test_user.id), password_data)
        
        assert exc_info.value.status_code == 422
        assert "新密码与确认密码不匹配" in str(exc_info.value.detail["message"])

    def test_get_user_login_logs(self, user_service: UserService, test_user: User, db_session: Session):
        """测试获取用户登录日志"""
        # 创建一些测试登录日志
        for i in range(25):
            log = LoginLog(
                user_id=test_user.id,
                login_type="username",
                login_method="password",
                ip_address=f"192.168.1.{i+1}",
                is_success=True
            )
            db_session.add(log)
        db_session.commit()
        
        # 测试分页
        logs, total = user_service.get_user_login_logs(str(test_user.id), page=1, page_size=10)
        
        assert len(logs) == 10
        assert total == 25
        assert logs[0].login_type == "username"

    def test_get_user_login_logs_pagination(self, user_service: UserService, test_user: User, db_session: Session):
        """测试登录日志分页"""
        # 创建测试数据
        for i in range(15):
            log = LoginLog(
                user_id=test_user.id,
                login_type="username",
                login_method="password",
                is_success=True
            )
            db_session.add(log)
        db_session.commit()
        
        # 测试第二页
        logs, total = user_service.get_user_login_logs(str(test_user.id), page=2, page_size=10)
        
        assert len(logs) == 5  # 第二页应该有5条记录
        assert total == 15

    def test_delete_user_account_success(self, user_service: UserService, test_user: User):
        """测试账户注销成功"""
        deletion_data = AccountDeletionRequest(
            password=test_user._original_password,
            reason="测试注销"
        )
        
        result = user_service.delete_user_account(str(test_user.id), deletion_data)
        
        assert result is True
        
        # 验证用户被设置为非活跃状态
        db_session = user_service.db
        user = db_session.query(User).filter(User.id == test_user.id).first()
        assert user.is_active is False

    def test_delete_user_account_wrong_password(self, user_service: UserService, test_user: User):
        """测试账户注销密码错误"""
        deletion_data = AccountDeletionRequest(
            password="WrongPassword",
            reason="测试注销"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            user_service.delete_user_account(str(test_user.id), deletion_data)
        
        assert exc_info.value.status_code == 401
        assert "密码错误" in str(exc_info.value.detail["message"])

    def test_record_login_log_success(self, user_service: UserService, test_user: User):
        """测试记录登录日志成功"""
        result = user_service.create_login_log(
            user_id=str(test_user.id),
            login_type="username",
            login_method="password",
            ip_address="192.168.1.100",
            user_agent="TestAgent",
            location="测试地点",
            is_success=True
        )
        
        # 验证返回的是LoginLogResponse对象
        assert result is not None
        assert result.login_type == "username"
        assert result.ip_address == "192.168.1.100"
        assert result.is_success is True
        
        # 验证日志已记录到数据库
        db_session = user_service.db
        log = db_session.query(LoginLog).filter(LoginLog.user_id == test_user.id).first()
        assert log is not None
        assert log.login_type == "username"
        assert log.ip_address == "192.168.1.100"

    def test_record_login_log_failure(self, user_service: UserService):
        """测试记录登录失败日志"""
        result = user_service.create_login_log(
            user_id=None,  # 失败登录可能没有用户ID
            login_type="username",
            login_method="password",
            ip_address="192.168.1.100",
            is_success=False,
            failure_reason="用户不存在"
        )
        
        # 验证返回的是LoginLogResponse对象
        assert result is not None
        assert result.login_type == "username"
        assert result.ip_address == "192.168.1.100"
        assert result.is_success is False
        assert result.failure_reason == "用户不存在"

    def test_get_user_statistics(self, user_service: UserService, test_user: User):
        """测试获取用户统计信息"""
        stats = user_service.get_user_statistics(str(test_user.id))
        
        # 验证统计字段存在且类型正确
        assert hasattr(stats, 'total_cards')
        assert hasattr(stats, 'active_cards')
        assert hasattr(stats, 'total_transactions')
        assert hasattr(stats, 'total_spending')
        assert isinstance(stats.total_cards, int)
        assert isinstance(stats.total_spending, float)

    def test_get_user_wechat_bindings(self, user_service: UserService, test_user: User):
        """测试获取用户微信绑定"""
        bindings = user_service.get_wechat_bindings(str(test_user.id))
        
        # 新用户应该没有微信绑定
        assert isinstance(bindings, list)
        assert len(bindings) == 0 