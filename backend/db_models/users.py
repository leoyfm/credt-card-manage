"""
用户数据库模型

定义用户认证相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

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
    
    phone = Column(
        String(20), 
        unique=True,
        comment="手机号码，全局唯一"
    )
    
    password_hash = Column(
        String(128), 
        nullable=False,
        comment="密码哈希值"
    )

    # 个人信息
    nickname = Column(
        String(50),
        comment="用户昵称"
    )
    
    avatar_url = Column(
        String(500),
        comment="头像URL"
    )
    
    gender = Column(
        ENUM('male', 'female', 'unknown', name='gender_enum'),
        default='unknown',
        comment="性别：male-男性，female-女性，unknown-未知"
    )
    
    birthday = Column(
        DateTime,
        comment="生日"
    )
    
    bio = Column(
        Text,
        comment="个人简介"
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

    # 登录信息
    login_count = Column(
        String(20),
        default="0",
        comment="登录次数"
    )
    
    last_login_at = Column(
        DateTime,
        comment="最后登录时间"
    )
    
    last_login_ip = Column(
        String(45),
        comment="最后登录IP地址"
    )

    # 关联关系
    verification_codes = relationship("VerificationCode", back_populates="user")
    wechat_bindings = relationship("WechatBinding", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

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

    phone_or_email = Column(
        String(100),
        nullable=False,
        comment="手机号或邮箱地址"
    )
    
    code = Column(
        String(10),
        nullable=False,
        comment="验证码"
    )
    
    code_type = Column(
        ENUM('login', 'register', 'reset_password', 'bind_phone', name='code_type_enum'),
        nullable=False,
        comment="验证码类型"
    )
    
    expires_at = Column(
        DateTime,
        nullable=False,
        comment="过期时间"
    )
    
    is_used = Column(
        Boolean,
        default=False,
        comment="是否已使用"
    )
    
    ip_address = Column(
        String(45),
        comment="请求IP地址"
    )

    # 用户关联（可选，用于统计）
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        comment="关联用户ID"
    )
    
    user = relationship("User", back_populates="verification_codes")

    # 索引
    __table_args__ = (
        Index('idx_verification_codes_phone_email', 'phone_or_email'),
        Index('idx_verification_codes_code', 'code'),
        Index('idx_verification_codes_type', 'code_type'),
        Index('idx_verification_codes_expires', 'expires_at'),
        Index('idx_verification_codes_used', 'is_used'),
    )


class WechatBinding(BaseModel):
    """
    微信绑定数据库模型
    
    定义wechat_bindings表结构，存储用户微信绑定信息。
    """
    __tablename__ = "wechat_bindings"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        comment="关联用户ID"
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
    
    sex = Column(
        ENUM('male', 'female', 'unknown', name='wechat_sex_enum'),
        default='unknown',
        comment="微信性别信息"
    )
    
    country = Column(
        String(50),
        comment="国家"
    )
    
    province = Column(
        String(50),
        comment="省份"
    )
    
    city = Column(
        String(50),
        comment="城市"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="绑定是否有效"
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


class UserSession(BaseModel):
    """
    用户会话数据库模型
    
    定义user_sessions表结构，存储用户登录会话信息（可选）。
    """
    __tablename__ = "user_sessions"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False,
        comment="关联用户ID"
    )
    
    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="会话令牌"
    )
    
    device_info = Column(
        Text,
        comment="设备信息（JSON格式）"
    )
    
    ip_address = Column(
        String(45),
        comment="登录IP地址"
    )
    
    user_agent = Column(
        Text,
        comment="用户代理字符串"
    )
    
    expires_at = Column(
        DateTime,
        nullable=False,
        comment="会话过期时间"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="会话是否有效"
    )
    
    last_activity_at = Column(
        DateTime,
        default=func.now(),
        comment="最后活动时间"
    )

    # 关联关系
    user = relationship("User")

    # 索引
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_token', 'session_token'),
        Index('idx_user_sessions_expires', 'expires_at'),
        Index('idx_user_sessions_active', 'is_active'),
    )


class LoginLog(BaseModel):
    """
    登录日志数据库模型
    
    定义login_logs表结构，记录用户登录历史。
    """
    __tablename__ = "login_logs"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        comment="关联用户ID"
    )
    
    login_type = Column(
        ENUM('username_password', 'phone_password', 'phone_code', 'wechat', name='login_type_enum'),
        nullable=False,
        comment="登录方式"
    )
    
    ip_address = Column(
        String(45),
        comment="登录IP地址"
    )
    
    user_agent = Column(
        Text,
        comment="用户代理字符串"
    )
    
    device_info = Column(
        Text,
        comment="设备信息（JSON格式）"
    )
    
    is_success = Column(
        Boolean,
        default=True,
        comment="登录是否成功"
    )
    
    failure_reason = Column(
        String(200),
        comment="失败原因"
    )
    
    location = Column(
        String(200),
        comment="登录地理位置"
    )

    # 关联关系
    user = relationship("User")

    # 索引
    __table_args__ = (
        Index('idx_login_logs_user_id', 'user_id'),
        Index('idx_login_logs_type', 'login_type'),
        Index('idx_login_logs_success', 'is_success'),
        Index('idx_login_logs_created_at', 'created_at'),
        Index('idx_login_logs_ip', 'ip_address'),
    ) 