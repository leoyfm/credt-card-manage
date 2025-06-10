"""认证相关的Pydantic模型"""

from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
from enum import Enum

class CodeType(str, Enum):
    """验证码类型枚举"""
    LOGIN = "login"
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"
    CHANGE_PHONE = "change_phone"
    BIND_WECHAT = "bind_wechat"

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名", example="testuser2024")
    email: str = Field(..., description="邮箱地址", example="user@example.com")
    password: str = Field(..., min_length=8, max_length=30, description="密码", example="Password123")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称", example="测试用户")
    phone: Optional[str] = Field(None, description="手机号", example="13800138000")
    verification_code: Optional[str] = Field(None, description="验证码", example="123456")

class LoginRequest(BaseModel):
    """登录请求基类"""
    remember_me: bool = Field(False, description="是否记住登录状态")

class UsernamePasswordLogin(LoginRequest):
    """用户名密码登录"""
    username: str = Field(..., description="用户名或邮箱", example="testuser2024")
    password: str = Field(..., description="密码", example="Password123")

class PhonePasswordLogin(LoginRequest):
    """手机号密码登录"""
    phone: str = Field(..., description="手机号", example="13800138000")
    password: str = Field(..., description="密码", example="Password123")

class PhoneCodeLogin(LoginRequest):
    """手机号验证码登录"""
    phone: str = Field(..., description="手机号", example="13800138000")
    code: str = Field(..., description="验证码", example="123456")

class WechatLoginRequest(LoginRequest):
    """微信登录请求"""
    code: str = Field(..., description="微信临时代码", example="wx_code_123456")
    state: Optional[str] = Field(None, description="状态参数", example="state_123")

class UserProfile(BaseModel):
    """用户资料"""
    id: Union[str, int] = Field(..., description="用户ID", example="489f8b55-5e75-4f18-982f-fca23b9d3ee4")
    username: str = Field(..., description="用户名", example="testuser2024")
    email: str = Field(..., description="邮箱", example="user@example.com")
    nickname: Optional[str] = Field(None, description="昵称", example="测试用户")
    phone: Optional[str] = Field(None, description="手机号", example="13800138000")
    is_active: bool = Field(True, description="是否激活")
    is_admin: bool = Field(False, description="是否管理员")
    created_at: Union[datetime, str] = Field(..., description="创建时间")
    last_login_at: Optional[Union[datetime, str]] = Field(None, description="最后登录时间")

class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)", example=86400)
    user: UserProfile = Field(..., description="用户信息")

class UserUpdateRequest(BaseModel):
    """用户资料更新请求"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称", example="新昵称")
    email: Optional[str] = Field(None, description="邮箱地址", example="new@example.com")
    phone: Optional[str] = Field(None, description="手机号", example="13900139000")

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码", example="OldPassword123")
    new_password: str = Field(..., min_length=8, max_length=30, description="新密码", example="NewPassword123")

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    phone: str = Field(..., description="手机号", example="13800138000")
    code: str = Field(..., description="验证码", example="123456")
    new_password: str = Field(..., min_length=8, max_length=30, description="新密码", example="NewPassword123")

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号", example="13800138000")
    code_type: CodeType = Field(..., description="验证码类型", example=CodeType.LOGIN)

class VerifyCodeRequest(BaseModel):
    """验证验证码请求"""
    phone: str = Field(..., description="手机号", example="13800138000")
    code: str = Field(..., description="验证码", example="123456")
    code_type: CodeType = Field(..., description="验证码类型", example=CodeType.LOGIN)

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌", example="refresh_token_123456")

class LogoutRequest(BaseModel):
    """登出请求"""
    all_devices: bool = Field(False, description="是否登出所有设备") 