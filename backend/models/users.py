"""
用户认证相关Pydantic模型

定义用户注册、登录、信息管理等相关的数据模型。
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
import re


class LoginType(str, Enum):
    """
    登录类型枚举
    
    定义不同的登录方式：
    - USERNAME_PASSWORD: 用户名密码登录
    - PHONE_PASSWORD: 手机号密码登录
    - PHONE_CODE: 手机号验证码登录
    - WECHAT: 微信登录
    """
    USERNAME_PASSWORD = "username_password"
    PHONE_PASSWORD = "phone_password"
    PHONE_CODE = "phone_code"
    WECHAT = "wechat"


class CodeType(str, Enum):
    """
    验证码类型枚举
    
    定义不同场景的验证码：
    - LOGIN: 登录验证码
    - REGISTER: 注册验证码
    - RESET_PASSWORD: 重置密码验证码
    - BIND_PHONE: 绑定手机号验证码
    """
    LOGIN = "login"
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"
    BIND_PHONE = "bind_phone"


class Gender(str, Enum):
    """
    性别枚举
    
    定义用户性别选项：
    - MALE: 男性
    - FEMALE: 女性
    - UNKNOWN: 未知/不愿透露
    """
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


# ==================== 用户注册相关模型 ====================

class UserRegisterRequest(BaseModel):
    """
    用户注册请求模型
    
    用于用户注册时的数据验证和文档生成。
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="用户名，3-20位字符，支持字母、数字、下划线",
        json_schema_extra={"example": "user123"}
    )
    
    email: EmailStr = Field(
        ...,
        description="邮箱地址，必须是有效的邮箱格式",
        json_schema_extra={"example": "user@example.com"}
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=30,
        description="密码，8-30位字符，建议包含字母、数字和特殊字符",
        json_schema_extra={"example": "password123"}
    )
    
    phone: Optional[str] = Field(
        None,
        description="手机号码，可选，中国大陆手机号格式",
        json_schema_extra={"example": "13800138000"}
    )
    
    nickname: Optional[str] = Field(
        None,
        max_length=50,
        description="昵称，可选，默认使用用户名",
        json_schema_extra={"example": "用户昵称"}
    )
    
    verification_code: Optional[str] = Field(
        None,
        min_length=6,
        max_length=6,
        description="手机验证码，提供手机号时必填",
        json_schema_extra={"example": "123456"}
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的中国大陆手机号')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """验证密码强度"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


# ==================== 用户登录相关模型 ====================

class UsernamePasswordLogin(BaseModel):
    """
    用户名密码登录请求模型
    
    支持用户名或邮箱登录。
    """
    username: str = Field(
        ...,
        description="用户名或邮箱地址",
        json_schema_extra={"example": "user123"}
    )
    
    password: str = Field(
        ...,
        description="用户密码",
        json_schema_extra={"example": "password123"}
    )
    
    remember_me: bool = Field(
        False,
        description="是否记住登录状态，影响令牌过期时间",
        json_schema_extra={"example": True}
    )


class PhonePasswordLogin(BaseModel):
    """
    手机号密码登录请求模型
    """
    phone: str = Field(
        ...,
        description="手机号码",
        json_schema_extra={"example": "13800138000"}
    )
    
    password: str = Field(
        ...,
        description="用户密码",
        json_schema_extra={"example": "password123"}
    )
    
    remember_me: bool = Field(
        False,
        description="是否记住登录状态",
        json_schema_extra={"example": True}
    )

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的中国大陆手机号')
        return v


class PhoneCodeLogin(BaseModel):
    """
    手机号验证码登录请求模型
    """
    phone: str = Field(
        ...,
        description="手机号码",
        json_schema_extra={"example": "13800138000"}
    )
    
    verification_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6位数字验证码",
        json_schema_extra={"example": "123456"}
    )

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的中国大陆手机号')
        return v

    @field_validator('verification_code')
    @classmethod
    def validate_code(cls, v):
        """验证验证码格式"""
        if not v.isdigit():
            raise ValueError('验证码必须是6位数字')
        return v


class WechatLoginRequest(BaseModel):
    """
    微信登录请求模型
    """
    code: str = Field(
        ...,
        description="微信授权码，由微信客户端获取",
        json_schema_extra={"example": "wx_auth_code_123456"}
    )
    
    user_info: Optional[Dict[str, Any]] = Field(
        None,
        description="可选的用户补充信息，如昵称等",
        json_schema_extra={"example": {"nickname": "微信用户", "avatar_url": "https://wx.qlogo.cn/mmopen/xxx"}}
    )


# ==================== 登录响应模型 ====================

class UserProfile(BaseModel):
    """
    用户资料模型
    
    返回用户的详细信息，用于API响应。
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="用户唯一标识符",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    username: str = Field(
        ...,
        description="用户名",
        json_schema_extra={"example": "user123"}
    )
    
    email: str = Field(
        ...,
        description="邮箱地址",
        json_schema_extra={"example": "user@example.com"}
    )
    
    phone: Optional[str] = Field(
        None,
        description="手机号码",
        json_schema_extra={"example": "13800138000"}
    )
    
    nickname: Optional[str] = Field(
        None,
        description="用户昵称",
        json_schema_extra={"example": "用户昵称"}
    )
    
    avatar_url: Optional[str] = Field(
        None,
        description="头像URL",
        json_schema_extra={"example": "https://example.com/avatar.jpg"}
    )
    
    gender: Gender = Field(
        Gender.UNKNOWN,
        description="性别",
        json_schema_extra={"example": "male"}
    )
    
    birthday: Optional[datetime] = Field(
        None,
        description="生日",
        json_schema_extra={"example": "1990-01-01T00:00:00"}
    )
    
    bio: Optional[str] = Field(
        None,
        description="个人简介",
        json_schema_extra={"example": "这是我的个人简介"}
    )
    
    is_active: bool = Field(
        True,
        description="账户是否激活",
        json_schema_extra={"example": True}
    )
    
    is_verified: bool = Field(
        False,
        description="是否已验证邮箱或手机号",
        json_schema_extra={"example": True}
    )
    
    is_admin: bool = Field(
        False,
        description="是否为管理员",
        json_schema_extra={"example": False}
    )
    
    login_count: str = Field(
        "0",
        description="登录次数",
        json_schema_extra={"example": "10"}
    )
    
    last_login_at: Optional[datetime] = Field(
        None,
        description="最后登录时间",
        json_schema_extra={"example": "2024-01-01T12:00:00"}
    )
    
    created_at: datetime = Field(
        ...,
        description="注册时间",
        json_schema_extra={"example": "2024-01-01T00:00:00"}
    )
    
    updated_at: datetime = Field(
        ...,
        description="最后更新时间",
        json_schema_extra={"example": "2024-01-01T12:00:00"}
    )


class LoginResponse(BaseModel):
    """
    登录响应模型
    
    登录成功后返回的数据结构。
    """
    access_token: str = Field(
        ...,
        description="JWT访问令牌，用于API认证",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    
    token_type: str = Field(
        "bearer",
        description="令牌类型，固定为bearer",
        json_schema_extra={"example": "bearer"}
    )
    
    expires_in: int = Field(
        ...,
        description="令牌过期时间（秒）",
        json_schema_extra={"example": 86400}
    )
    
    user: UserProfile = Field(
        ...,
        description="用户详细信息"
    )


# ==================== 验证码相关模型 ====================

class SendCodeRequest(BaseModel):
    """
    发送验证码请求模型
    """
    phone_or_email: str = Field(
        ...,
        description="手机号或邮箱地址",
        json_schema_extra={"example": "13800138000"}
    )
    
    code_type: CodeType = Field(
        ...,
        description="验证码类型",
        json_schema_extra={"example": CodeType.LOGIN}
    )

    @field_validator('phone_or_email')
    @classmethod
    def validate_phone_or_email(cls, v):
        """验证手机号或邮箱格式"""
        # 检查是否为手机号
        if re.match(r'^1[3-9]\d{9}$', v):
            return v
        # 检查是否为邮箱
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            return v
        raise ValueError('请输入有效的手机号或邮箱地址')


class VerifyCodeRequest(BaseModel):
    """
    验证验证码请求模型
    """
    phone_or_email: str = Field(
        ...,
        description="手机号或邮箱地址",
        json_schema_extra={"example": "13800138000"}
    )
    
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6位数字验证码",
        json_schema_extra={"example": "123456"}
    )
    
    code_type: CodeType = Field(
        ...,
        description="验证码类型",
        json_schema_extra={"example": CodeType.LOGIN}
    )


# ==================== 用户信息管理模型 ====================

class UserUpdateRequest(BaseModel):
    """
    用户信息更新请求模型
    
    支持部分字段更新，所有字段都是可选的。
    """
    nickname: Optional[str] = Field(
        None,
        max_length=50,
        description="用户昵称",
        json_schema_extra={"example": "新昵称"}
    )
    
    avatar_url: Optional[str] = Field(
        None,
        description="头像URL",
        json_schema_extra={"example": "https://example.com/new-avatar.jpg"}
    )
    
    gender: Optional[Gender] = Field(
        None,
        description="性别",
        json_schema_extra={"example": Gender.MALE}
    )
    
    birthday: Optional[datetime] = Field(
        None,
        description="生日",
        json_schema_extra={"example": "1990-01-01T00:00:00"}
    )
    
    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="个人简介",
        json_schema_extra={"example": "这是我的新个人简介"}
    )


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求模型
    """
    old_password: str = Field(
        ...,
        description="当前密码",
        json_schema_extra={"example": "old_password123"}
    )
    
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=30,
        description="新密码，8-30位字符",
        json_schema_extra={"example": "new_password123"}
    )

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class ResetPasswordRequest(BaseModel):
    """
    重置密码请求模型
    """
    phone_or_email: str = Field(
        ...,
        description="手机号或邮箱地址",
        json_schema_extra={"example": "13800138000"}
    )
    
    verification_code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6位数字验证码",
        json_schema_extra={"example": "123456"}
    )
    
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=30,
        description="新密码，8-30位字符",
        json_schema_extra={"example": "new_password123"}
    )

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


# ==================== 微信相关模型 ====================

class WechatBindingInfo(BaseModel):
    """
    微信绑定信息模型
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="绑定记录ID",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    user_id: UUID = Field(
        ...,
        description="用户ID",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    openid: str = Field(
        ...,
        description="微信OpenID",
        json_schema_extra={"example": "wx_openid_123456"}
    )
    
    unionid: Optional[str] = Field(
        None,
        description="微信UnionID",
        json_schema_extra={"example": "wx_unionid_123456"}
    )
    
    nickname: Optional[str] = Field(
        None,
        description="微信昵称",
        json_schema_extra={"example": "微信昵称"}
    )
    
    avatar_url: Optional[str] = Field(
        None,
        description="微信头像URL",
        json_schema_extra={"example": "https://wx.qlogo.cn/mmopen/xxx"}
    )
    
    sex: Gender = Field(
        Gender.UNKNOWN,
        description="微信性别信息",
        json_schema_extra={"example": Gender.MALE}
    )
    
    country: Optional[str] = Field(
        None,
        description="国家",
        json_schema_extra={"example": "中国"}
    )
    
    province: Optional[str] = Field(
        None,
        description="省份",
        json_schema_extra={"example": "广东"}
    )
    
    city: Optional[str] = Field(
        None,
        description="城市",
        json_schema_extra={"example": "深圳"}
    )
    
    is_active: bool = Field(
        True,
        description="绑定是否有效",
        json_schema_extra={"example": True}
    )
    
    created_at: datetime = Field(
        ...,
        description="绑定时间",
        json_schema_extra={"example": "2024-01-01T00:00:00"}
    )


# ==================== 令牌相关模型 ====================

class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求模型
    """
    refresh_token: str = Field(
        ...,
        description="刷新令牌",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )


class LogoutRequest(BaseModel):
    """
    登出请求模型
    """
    all_devices: bool = Field(
        False,
        description="是否登出所有设备",
        json_schema_extra={"example": False}
    )


# ==================== 登录日志模型 ====================

class LoginLogInfo(BaseModel):
    """
    登录日志信息模型
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(
        ...,
        description="日志记录ID",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    login_type: LoginType = Field(
        ...,
        description="登录方式",
        json_schema_extra={"example": LoginType.USERNAME_PASSWORD}
    )
    
    ip_address: Optional[str] = Field(
        None,
        description="登录IP地址",
        json_schema_extra={"example": "192.168.1.1"}
    )
    
    user_agent: Optional[str] = Field(
        None,
        description="用户代理字符串",
        json_schema_extra={"example": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    
    is_success: bool = Field(
        True,
        description="登录是否成功",
        json_schema_extra={"example": True}
    )
    
    failure_reason: Optional[str] = Field(
        None,
        description="失败原因",
        json_schema_extra={"example": "密码错误"}
    )
    
    location: Optional[str] = Field(
        None,
        description="登录地理位置",
        json_schema_extra={"example": "广东省深圳市"}
    )
    
    created_at: datetime = Field(
        ...,
        description="登录时间",
        json_schema_extra={"example": "2024-01-01T12:00:00"}
    )


# ==================== 用户统计模型 ====================

class UserStatsInfo(BaseModel):
    """
    用户统计信息模型
    """
    total_users: int = Field(
        ...,
        description="总用户数",
        json_schema_extra={"example": 1000}
    )
    
    active_users: int = Field(
        ...,
        description="活跃用户数",
        json_schema_extra={"example": 800}
    )
    
    verified_users: int = Field(
        ...,
        description="已验证用户数",
        json_schema_extra={"example": 600}
    )
    
    new_users_today: int = Field(
        ...,
        description="今日新增用户数",
        json_schema_extra={"example": 10}
    )
    
    login_count_today: int = Field(
        ...,
        description="今日登录次数",
        json_schema_extra={"example": 500}
    )

# 为了避免循环引用，在文件末尾更新模型
UserProfile.model_rebuild() 