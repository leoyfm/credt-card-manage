"""
用户相关的Pydantic模型 - API v1

定义用户功能区的请求和响应模型：
- 用户资料更新
- 密码修改
- 登录日志
- 微信绑定信息
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator


class UserUpdateRequest(BaseModel):
    """用户资料更新请求模型"""
    
    nickname: Optional[str] = Field(
        None, 
        max_length=50,
        description="昵称，最大50个字符",
        example="小明"
    )
    
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="手机号",
        example="13800138000"
    )
    
    avatar_url: Optional[str] = Field(
        None,
        max_length=500,
        description="头像URL",
        example="https://example.com/avatar.jpg"
    )
    
    timezone: Optional[str] = Field(
        None,
        max_length=50,
        description="时区设置",
        example="Asia/Shanghai"
    )
    
    language: Optional[str] = Field(
        None,
        max_length=10,
        description="语言偏好",
        example="zh-CN"
    )
    
    currency: Optional[str] = Field(
        None,
        max_length=10,
        description="默认货币",
        example="CNY"
    )
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号只能包含数字')
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        if v and v not in ['Asia/Shanghai', 'UTC', 'America/New_York', 'Europe/London']:
            raise ValueError('不支持的时区设置')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        if v and v not in ['zh-CN', 'en-US', 'ja-JP']:
            raise ValueError('不支持的语言设置')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        if v and v not in ['CNY', 'USD', 'EUR', 'JPY']:
            raise ValueError('不支持的货币类型')
        return v


class UserPasswordChangeRequest(BaseModel):
    """密码修改请求模型"""
    
    current_password: str = Field(
        ...,
        min_length=8,
        description="当前密码",
        example="CurrentPass123"
    )
    
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="新密码，至少8位",
        example="NewPass123456"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not has_letter or not has_digit:
            raise ValueError('密码必须包含字母和数字')
        
        return v


class LoginLogInfo(BaseModel):
    """登录日志信息模型"""
    
    id: UUID = Field(description="日志ID")
    
    login_type: str = Field(
        description="登录类型",
        example="username"
    )
    
    login_method: str = Field(
        description="登录方式",
        example="password"
    )
    
    ip_address: Optional[str] = Field(
        description="IP地址",
        example="192.168.1.100"
    )
    
    user_agent: Optional[str] = Field(
        description="用户代理",
        example="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    location: Optional[str] = Field(
        description="地理位置",
        example="北京市"
    )
    
    is_success: bool = Field(
        description="是否登录成功",
        example=True
    )
    
    failure_reason: Optional[str] = Field(
        description="失败原因",
        example="密码错误"
    )
    
    created_at: datetime = Field(
        description="登录时间",
        example="2024-12-01T10:00:00Z"
    )


class WechatBindingInfo(BaseModel):
    """微信绑定信息模型"""
    
    id: UUID = Field(description="绑定ID")
    
    openid: str = Field(
        description="微信OpenID",
        example="oWr7L0xxxxxxxxxxxxxxxxxxx"
    )
    
    unionid: Optional[str] = Field(
        description="微信UnionID",
        example="oGExxxxxxxxxxxxxxxxxxxxxxx"
    )
    
    nickname: Optional[str] = Field(
        description="微信昵称",
        example="微信用户"
    )
    
    avatar_url: Optional[str] = Field(
        description="微信头像",
        example="https://thirdwx.qlogo.cn/mmopen/xxx.jpg"
    )
    
    is_active: bool = Field(
        description="绑定是否激活",
        example=True
    )
    
    bound_at: datetime = Field(
        description="绑定时间",
        example="2024-12-01T10:00:00Z"
    )


class UserStatsInfo(BaseModel):
    """用户统计信息模型"""
    
    total_cards: int = Field(
        description="信用卡总数",
        example=5
    )
    
    active_cards: int = Field(
        description="活跃卡片数",
        example=4
    )
    
    total_credit_limit: float = Field(
        description="总信用额度",
        example=200000.00
    )
    
    total_used_limit: float = Field(
        description="已用额度",
        example=50000.00
    )
    
    credit_utilization_rate: float = Field(
        description="信用利用率（百分比）",
        example=25.0
    )
    
    total_transactions: int = Field(
        description="交易总数",
        example=150
    )
    
    total_spending: float = Field(
        description="总支出",
        example=80000.00
    )
    
    monthly_avg_spending: float = Field(
        description="月均支出",
        example=8000.00
    )
    
    total_points_earned: int = Field(
        description="累计获得积分",
        example=80000
    )
    
    total_cashback_earned: float = Field(
        description="累计获得返现",
        example=800.00
    )
    
    pending_reminders: int = Field(
        description="待处理提醒数",
        example=3
    )
    
    account_age_days: int = Field(
        description="账户年龄（天数）",
        example=365
    )


class UserProfileResponse(BaseModel):
    """用户资料响应模型（扩展版）"""
    
    id: UUID = Field(description="用户ID")
    username: str = Field(description="用户名", example="testuser")
    email: EmailStr = Field(description="邮箱", example="user@example.com")
    nickname: Optional[str] = Field(description="昵称", example="测试用户")
    phone: Optional[str] = Field(description="手机号", example="13800138000")
    avatar_url: Optional[str] = Field(description="头像URL")
    
    is_active: bool = Field(description="是否激活", example=True)
    is_verified: bool = Field(description="是否已验证", example=False)
    is_admin: bool = Field(description="是否管理员", example=False)
    
    timezone: str = Field(description="时区", example="Asia/Shanghai")
    language: str = Field(description="语言", example="zh-CN")
    currency: str = Field(description="货币", example="CNY")
    
    last_login_at: Optional[datetime] = Field(description="最后登录时间")
    email_verified_at: Optional[datetime] = Field(description="邮箱验证时间")
    created_at: datetime = Field(description="注册时间")
    updated_at: datetime = Field(description="更新时间")
    
    # 扩展统计信息
    stats: Optional[UserStatsInfo] = Field(description="用户统计信息")


class UserActivityInfo(BaseModel):
    """用户活动信息"""
    
    last_login_ip: Optional[str] = Field(
        description="最后登录IP",
        example="192.168.1.100"
    )
    
    last_login_location: Optional[str] = Field(
        description="最后登录位置",
        example="北京市"
    )
    
    login_count_today: int = Field(
        description="今日登录次数",
        example=3
    )
    
    login_count_week: int = Field(
        description="本周登录次数",
        example=15
    )
    
    last_transaction_at: Optional[datetime] = Field(
        description="最后交易时间"
    )
    
    active_sessions: int = Field(
        description="活跃会话数",
        example=2
    ) 