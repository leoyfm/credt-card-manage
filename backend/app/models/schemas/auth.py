"""
认证相关Pydantic模型
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    """
    用户注册请求模型
    """
    username: str = Field(..., description="用户名", json_schema_extra={"example": "testuser"})
    email: EmailStr = Field(..., description="邮箱", json_schema_extra={"example": "testuser@example.com"})
    password: str = Field(..., description="密码", json_schema_extra={"example": "TestPass123456"})
    nickname: Optional[str] = Field(None, description="昵称", json_schema_extra={"example": "测试用户"})

class LoginRequest(BaseModel):
    """
    用户名登录请求模型
    """
    username: str = Field(..., description="用户名", json_schema_extra={"example": "testuser"})
    password: str = Field(..., description="密码", json_schema_extra={"example": "TestPass123456"})

class TokenResponse(BaseModel):
    """
    令牌响应模型
    """
    access_token: str = Field(..., description="访问令牌", json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."})
    refresh_token: str = Field(..., description="刷新令牌", json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."})
    token_type: str = Field("bearer", description="令牌类型", json_schema_extra={"example": "bearer"})

class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求模型
    """
    refresh_token: str = Field(..., description="刷新令牌", json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."})

class AuthResponse(BaseModel):
    """
    认证成功响应模型
    """
    user_id: str = Field(..., description="用户ID", json_schema_extra={"example": "b1e2c3d4-5678-1234-9abc-1234567890ab"})
    username: str = Field(..., description="用户名", json_schema_extra={"example": "testuser"})
    email: EmailStr = Field(..., description="邮箱", json_schema_extra={"example": "testuser@example.com"})
    nickname: Optional[str] = Field(None, description="昵称", json_schema_extra={"example": "测试用户"})
    phone: Optional[str] = Field(None, description="手机号", json_schema_extra={"example": "13800000000"})
    avatar_url: Optional[str] = Field(None, description="头像URL", json_schema_extra={"example": "https://example.com/avatar.png"})
    is_active: bool = Field(True, description="是否激活", json_schema_extra={"example": True})
    is_verified: bool = Field(False, description="是否已验证", json_schema_extra={"example": False})
    is_admin: bool = Field(False, description="是否管理员", json_schema_extra={"example": False})
    timezone: Optional[str] = Field('Asia/Shanghai', description="时区", json_schema_extra={"example": "Asia/Shanghai"})
    language: Optional[str] = Field('zh-CN', description="语言偏好", json_schema_extra={"example": "zh-CN"})
    currency: Optional[str] = Field('CNY', description="默认货币", json_schema_extra={"example": "CNY"})
    last_login_at: Optional[str] = Field(None, description="最后登录时间", json_schema_extra={"example": "2024-01-01T12:00:00+08:00"})
    email_verified_at: Optional[str] = Field(None, description="邮箱验证时间", json_schema_extra={"example": "2024-01-01T12:00:00+08:00"})
    created_at: Optional[str] = Field(None, description="创建时间", json_schema_extra={"example": "2024-01-01T12:00:00+08:00"})
    updated_at: Optional[str] = Field(None, description="更新时间", json_schema_extra={"example": "2024-01-01T12:00:00+08:00"})
    access_token: str = Field(..., description="访问令牌", json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."})
    refresh_token: str = Field(..., description="刷新令牌", json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."})
    token_type: str = Field("bearer", description="令牌类型", json_schema_extra={"example": "bearer"}) 