"""
用户数据库模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class User(Base):
    """
    用户表
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

    # 预留关系字段
    # cards = relationship("Card", back_populates="user")
    # login_logs = relationship("LoginLog", back_populates="user") 