"""
用户模块 Pydantic 模型
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ========== 用户资料相关模型 ==========

class UserProfileResponse(BaseModel):
    """用户资料响应模型"""
    id: UUID = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_active: bool = Field(..., description="是否激活")
    is_verified: bool = Field(..., description="是否已验证")
    timezone: str = Field(..., description="时区")
    language: str = Field(..., description="语言偏好")
    currency: str = Field(..., description="默认货币")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    email_verified_at: Optional[datetime] = Field(None, description="邮箱验证时间")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "testuser",
                "email": "test@example.com",
                "nickname": "测试用户",
                "phone": "13800138000",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "is_verified": True,
                "timezone": "Asia/Shanghai",
                "language": "zh-CN",
                "currency": "CNY",
                "last_login_at": "2024-12-05T10:30:00Z",
                "email_verified_at": "2024-12-01T09:00:00Z",
                "created_at": "2024-12-01T09:00:00Z"
            }
        }
    )


class UserProfileUpdateRequest(BaseModel):
    """用户资料更新请求模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    timezone: Optional[str] = Field(None, max_length=50, description="时区")
    language: Optional[str] = Field(None, max_length=10, description="语言偏好")
    currency: Optional[str] = Field(None, max_length=10, description="默认货币")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nickname": "新昵称",
                "phone": "13900139000",
                "avatar_url": "https://example.com/new_avatar.jpg",
                "timezone": "Asia/Shanghai",
                "language": "zh-CN",
                "currency": "CNY"
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    current_password: str = Field(..., min_length=8, description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., min_length=8, description="确认新密码")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPass123456",
                "new_password": "NewPass123456",
                "confirm_password": "NewPass123456"
            }
        }
    )


# ========== 登录日志相关模型 ==========

class LoginLogResponse(BaseModel):
    """登录日志响应模型"""
    id: UUID = Field(..., description="日志ID")
    login_type: str = Field(..., description="登录类型")
    login_method: str = Field(..., description="登录方式")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    location: Optional[str] = Field(None, description="地理位置")
    is_success: bool = Field(..., description="是否成功")
    failure_reason: Optional[str] = Field(None, description="失败原因")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "login_type": "username",
                "login_method": "password",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "location": "北京市",
                "is_success": True,
                "failure_reason": None,
                "created_at": "2024-12-05T10:30:00Z"
            }
        }
    )


# ========== 账户操作相关模型 ==========

class AccountDeletionRequest(BaseModel):
    """账户注销请求模型"""
    password: str = Field(..., min_length=8, description="确认密码")
    reason: Optional[str] = Field(None, max_length=500, description="注销原因")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "UserPass123456",
                "reason": "不再使用此服务"
            }
        }
    )


# ========== 微信绑定相关模型 ==========

class WechatBindingResponse(BaseModel):
    """微信绑定响应模型"""
    id: UUID = Field(..., description="绑定ID")
    openid: str = Field(..., description="微信OpenID")
    unionid: Optional[str] = Field(None, description="微信UnionID")
    nickname: Optional[str] = Field(None, description="微信昵称")
    avatar_url: Optional[str] = Field(None, description="微信头像")
    is_active: bool = Field(..., description="是否激活")
    bound_at: datetime = Field(..., description="绑定时间")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "openid": "wx_openid_123456",
                "unionid": "wx_unionid_123456",
                "nickname": "微信用户",
                "avatar_url": "https://wx.qlogo.cn/avatar.jpg",
                "is_active": True,
                "bound_at": "2024-12-01T09:00:00Z"
            }
        }
    )


# ========== 用户统计相关模型 ==========

class UserStatisticsResponse(BaseModel):
    """用户统计响应模型"""
    # 基础统计
    total_cards: int = Field(..., description="信用卡总数")
    active_cards: int = Field(..., description="活跃信用卡数")
    total_credit_limit: float = Field(..., description="总信用额度")
    total_used_limit: float = Field(..., description="总已用额度")
    credit_utilization: float = Field(..., description="信用利用率(%)")
    
    # 交易统计
    total_transactions: int = Field(..., description="总交易笔数")
    total_spending: float = Field(..., description="总支出金额")
    this_month_spending: float = Field(..., description="本月支出金额")
    total_income: float = Field(..., description="总收入金额")
    avg_transaction: float = Field(..., description="平均交易金额")
    
    # 年费统计
    total_annual_fees: float = Field(..., description="总年费金额")
    waived_fees: float = Field(..., description="已减免年费")
    pending_fees: float = Field(..., description="待缴年费")
    
    # 积分统计
    total_points_earned: int = Field(..., description="总获得积分")
    total_cashback_earned: float = Field(..., description="总获得返现")
    
    # 提醒统计
    active_reminders: int = Field(..., description="活跃提醒数")
    
    # 时间统计
    account_age_days: int = Field(..., description="账户天数")
    last_transaction_date: Optional[datetime] = Field(None, description="最后交易时间")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_cards": 5,
                "active_cards": 4,
                "total_credit_limit": 150000.00,
                "total_used_limit": 45000.00,
                "credit_utilization": 30.0,
                "total_transactions": 156,
                "total_spending": 25680.50,
                "this_month_spending": 3240.80,
                "total_income": 3200.00,
                "avg_transaction": 185.67,
                "total_annual_fees": 1200.00,
                "waived_fees": 600.00,
                "pending_fees": 200.00,
                "total_points_earned": 12850,
                "total_cashback_earned": 386.40,
                "active_reminders": 3,
                "account_age_days": 365,
                "last_transaction_date": "2024-12-04T15:30:00Z"
            }
        }
    )


# ========== 其他辅助模型 ==========

class UserSearchRequest(BaseModel):
    """用户搜索请求模型（管理员用）"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    is_admin: Optional[bool] = Field(None, description="是否管理员")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "keyword": "test",
                "is_active": True,
                "is_verified": True,
                "is_admin": False,
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z"
            }
        }
    )


class UserStatusUpdateRequest(BaseModel):
    """用户状态更新请求模型（管理员用）"""
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    is_admin: Optional[bool] = Field(None, description="是否管理员")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": False,
                "is_verified": True,
                "is_admin": False
            }
        }
    ) 