"""
用户数据库模型 - 包含用户模块的4个表
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class User(Base):
    """
    用户表 (users) - 15字段
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱地址")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), nullable=True, comment="昵称")
    phone = Column(String(20), nullable=True, comment="手机号")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    timezone = Column(String(50), default='Asia/Shanghai', comment="时区")
    language = Column(String(10), default='zh-CN', comment="语言偏好")
    currency = Column(String(10), default='CNY', comment="默认货币")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    email_verified_at = Column(DateTime(timezone=True), nullable=True, comment="邮箱验证时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系字段
    verification_codes = relationship("VerificationCode", back_populates="user", cascade="all, delete-orphan")
    login_logs = relationship("LoginLog", back_populates="user")
    wechat_bindings = relationship("WechatBinding", back_populates="user", cascade="all, delete-orphan")
    credit_cards = relationship("CreditCard", back_populates="user", cascade="all, delete-orphan")

class VerificationCode(Base):
    """
    验证码表 (verification_codes) - 7字段
    """
    __tablename__ = "verification_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="验证码ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    code = Column(String(10), nullable=False, comment="验证码")
    code_type = Column(String(20), nullable=False, comment="验证码类型")  # email_verify, password_reset, phone_verify
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    is_used = Column(Boolean, default=False, comment="是否已使用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系字段
    user = relationship("User", back_populates="verification_codes")

class LoginLog(Base):
    """
    登录日志表 (login_logs) - 9字段
    """
    __tablename__ = "login_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="日志ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="用户ID")
    login_type = Column(String(20), nullable=False, comment="登录类型")  # username, phone, wechat
    login_method = Column(String(20), nullable=False, comment="登录方式")  # password, code, oauth
    ip_address = Column(INET, nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    location = Column(String(100), nullable=True, comment="地理位置")
    is_success = Column(Boolean, default=True, comment="是否成功")
    failure_reason = Column(String(100), nullable=True, comment="失败原因")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系字段
    user = relationship("User", back_populates="login_logs")

class WechatBinding(Base):
    """
    微信绑定表 (wechat_bindings) - 9字段
    """
    __tablename__ = "wechat_bindings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="绑定ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    openid = Column(String(100), unique=True, nullable=False, comment="微信OpenID")
    unionid = Column(String(100), nullable=True, comment="微信UnionID")
    nickname = Column(String(100), nullable=True, comment="微信昵称")
    avatar_url = Column(String(500), nullable=True, comment="微信头像")
    is_active = Column(Boolean, default=True, comment="是否激活")
    bound_at = Column(DateTime(timezone=True), server_default=func.now(), comment="绑定时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系字段
    user = relationship("User", back_populates="wechat_bindings") 