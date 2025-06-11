"""
认证相关Pydantic模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    """
    用户注册请求模型
    """
    username: str = Field(..., description="用户名", example="testuser")
    email: EmailStr = Field(..., description="邮箱", example="testuser@example.com")
    password: str = Field(..., description="密码", example="TestPass123456")
    nickname: Optional[str] = Field(None, description="昵称", example="测试用户")

class LoginRequest(BaseModel):
    """
    用户名登录请求模型
    """
    username: str = Field(..., description="用户名", example="testuser")
    password: str = Field(..., description="密码", example="TestPass123456")

class TokenResponse(BaseModel):
    """
    令牌响应模型
    """
    access_token: str = Field(..., description="访问令牌", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="刷新令牌", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", description="令牌类型", example="bearer")

class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求模型
    """
    refresh_token: str = Field(..., description="刷新令牌", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

class AuthResponse(BaseModel):
    """
    认证成功响应模型
    """
    user_id: str = Field(..., description="用户ID", example="b1e2c3d4-5678-1234-9abc-1234567890ab")
    username: str = Field(..., description="用户名", example="testuser")
    email: EmailStr = Field(..., description="邮箱", example="testuser@example.com")
    nickname: Optional[str] = Field(None, description="昵称", example="测试用户")
    phone: Optional[str] = Field(None, description="手机号", example="13800000000")
    avatar_url: Optional[str] = Field(None, description="头像URL", example="https://example.com/avatar.png")
    is_active: bool = Field(True, description="是否激活", example=True)
    is_verified: bool = Field(False, description="是否已验证", example=False)
    is_admin: bool = Field(False, description="是否管理员", example=False)
    timezone: Optional[str] = Field('Asia/Shanghai', description="时区", example="Asia/Shanghai")
    language: Optional[str] = Field('zh-CN', description="语言偏好", example="zh-CN")
    currency: Optional[str] = Field('CNY', description="默认货币", example="CNY")
    last_login_at: Optional[str] = Field(None, description="最后登录时间", example="2024-01-01T12:00:00+08:00")
    email_verified_at: Optional[str] = Field(None, description="邮箱验证时间", example="2024-01-01T12:00:00+08:00")
    created_at: Optional[str] = Field(None, description="创建时间", example="2024-01-01T12:00:00+08:00")
    updated_at: Optional[str] = Field(None, description="更新时间", example="2024-01-01T12:00:00+08:00")
    access_token: str = Field(..., description="访问令牌", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="刷新令牌", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", description="令牌类型", example="bearer") 