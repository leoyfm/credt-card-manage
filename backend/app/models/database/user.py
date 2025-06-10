"""
用户模块数据库模型

定义用户认证相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM, INET
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """
    用户数据库模型
    
    定义users表结构，存储用户基本信息和认证数据。
    """
    __tablename__ = "users"

    # 基本信息
    username = Column(
        String(50), 
        unique=True, 
        nullable=False,
        comment="用户名，全局唯一"
    )
    
    email = Column(
        String(100), 
        unique=True, 
        nullable=False,
        comment="邮箱地址，全局唯一"
    )
    
    password_hash = Column(
        String(255), 
        nullable=False,
        comment="密码哈希值"
    )

    # 个人信息
    nickname = Column(
        String(50),
        comment="用户昵称"
    )
    
    phone = Column(
        String(20),
        unique=True,
        comment="手机号码，全局唯一"
    )
    
    avatar_url = Column(
        String(500),
        comment="头像URL"
    )

    # 状态信息
    is_active = Column(
        Boolean, 
        default=True,
        comment="账户是否激活"
    )
    
    is_verified = Column(
        Boolean, 
        default=False,
        comment="是否已验证（邮箱或手机号）"
    )
    
    is_admin = Column(
        Boolean, 
        default=False,
        comment="是否为管理员"
    )

    # 用户偏好设置
    timezone = Column(
        String(50),
        default='Asia/Shanghai',
        comment="时区设置"
    )
    
    language = Column(
        String(10),
        default='zh-CN',
        comment="语言偏好"
    )
    
    currency = Column(
        String(10),
        default='CNY',
        comment="默认货币"
    )

    # 登录信息
    last_login_at = Column(
        DateTime(timezone=True),
        comment="最后登录时间"
    )
    
    email_verified_at = Column(
        DateTime(timezone=True),
        comment="邮箱验证时间"
    )

    # 关联关系
    verification_codes = relationship("VerificationCode", back_populates="user", cascade="all, delete-orphan")
    wechat_bindings = relationship("WechatBinding", back_populates="user", cascade="all, delete-orphan")
    login_logs = relationship("LoginLog", back_populates="user")
    credit_cards = relationship("CreditCard", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user")
    reminder_settings = relationship("ReminderSetting", back_populates="user", cascade="all, delete-orphan")
    user_statistics = relationship("UserStatistics", back_populates="user", cascade="all, delete-orphan")
    recommendation_records = relationship("RecommendationRecord", back_populates="user", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_phone', 'phone'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )


class VerificationCode(BaseModel):
    """
    验证码数据库模型
    
    定义verification_codes表结构，存储短信/邮件验证码。
    """
    __tablename__ = "verification_codes"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    code = Column(
        String(10),
        nullable=False,
        comment="验证码"
    )
    
    code_type = Column(
        String(20),
        nullable=False,
        comment="验证码类型：email_verify, password_reset, phone_verify"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="过期时间"
    )
    
    is_used = Column(
        Boolean,
        default=False,
        comment="是否已使用"
    )

    # 关联关系
    user = relationship("User", back_populates="verification_codes")

    # 索引
    __table_args__ = (
        Index('idx_verification_codes_user_id', 'user_id'),
        Index('idx_verification_codes_code', 'code'),
        Index('idx_verification_codes_type', 'code_type'),
        Index('idx_verification_codes_expires', 'expires_at'),
        Index('idx_verification_codes_used', 'is_used'),
    )


class LoginLog(BaseModel):
    """
    登录日志数据库模型
    
    定义login_logs表结构，记录用户登录历史。
    """
    __tablename__ = "login_logs"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        comment="用户ID"
    )
    
    login_type = Column(
        String(20),
        nullable=False,
        comment="登录类型：username, phone, wechat"
    )
    
    login_method = Column(
        String(20),
        nullable=False,
        comment="登录方式：password, code, oauth"
    )
    
    ip_address = Column(
        INET,
        comment="IP地址"
    )
    
    user_agent = Column(
        Text,
        comment="用户代理字符串"
    )
    
    location = Column(
        String(100),
        comment="地理位置"
    )
    
    is_success = Column(
        Boolean,
        default=True,
        comment="是否成功"
    )
    
    failure_reason = Column(
        String(100),
        comment="失败原因"
    )

    # 关联关系
    user = relationship("User", back_populates="login_logs")

    # 索引
    __table_args__ = (
        Index('idx_login_logs_user_id', 'user_id'),
        Index('idx_login_logs_user_time', 'user_id', 'created_at'),
        Index('idx_login_logs_ip', 'ip_address'),
        Index('idx_login_logs_success', 'is_success'),
    )


class WechatBinding(BaseModel):
    """
    微信绑定数据库模型
    
    定义wechat_bindings表结构，存储用户微信绑定信息。
    """
    __tablename__ = "wechat_bindings"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    openid = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="微信OpenID，应用内唯一"
    )
    
    unionid = Column(
        String(100),
        unique=True,
        comment="微信UnionID，同一开发者账号下唯一"
    )
    
    nickname = Column(
        String(100),
        comment="微信昵称"
    )
    
    avatar_url = Column(
        String(500),
        comment="微信头像URL"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="绑定是否有效"
    )
    
    bound_at = Column(
        DateTime(timezone=True),
        server_default='now()',
        comment="绑定时间"
    )

    # 关联关系
    user = relationship("User", back_populates="wechat_bindings")

    # 索引
    __table_args__ = (
        Index('idx_wechat_bindings_user_id', 'user_id'),
        Index('idx_wechat_bindings_openid', 'openid'),
        Index('idx_wechat_bindings_unionid', 'unionid'),
        Index('idx_wechat_bindings_active', 'is_active'),
    ) 