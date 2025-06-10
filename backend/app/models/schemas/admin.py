"""
管理员相关的Pydantic模型 - API v1

定义管理员功能区的请求和响应模型：
- 管理员查看的用户列表
- 管理员查看的用户详情
- 用户状态和权限管理
- 系统统计信息
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class AdminUserListResponse(BaseModel):
    """管理员查看的用户列表响应模型（脱敏）"""
    
    id: UUID = Field(description="用户ID")
    username: str = Field(description="用户名", example="testuser")
    email: EmailStr = Field(description="邮箱（部分脱敏）", example="te***@example.com")
    nickname: Optional[str] = Field(description="昵称", example="测试用户")
    
    is_active: bool = Field(description="是否激活", example=True)
    is_verified: bool = Field(description="是否已验证", example=False)
    is_admin: bool = Field(description="是否管理员", example=False)
    
    last_login_at: Optional[datetime] = Field(description="最后登录时间")
    created_at: datetime = Field(description="注册时间")
    
    # 统计信息（不涉及具体数据）
    cards_count: int = Field(description="信用卡数量", example=3)
    transactions_count: int = Field(description="交易数量", example=50)
    total_spending: float = Field(description="总支出（汇总）", example=10000.00)
    
    # 最近活动
    login_count_30days: int = Field(description="30天内登录次数", example=15)
    last_login_ip: Optional[str] = Field(description="最后登录IP", example="192.168.1.100")
    last_login_location: Optional[str] = Field(description="最后登录位置", example="北京市")


class AdminUserStatsDetail(BaseModel):
    """管理员查看的用户统计详情"""
    
    # 信用卡统计
    total_cards: int = Field(description="信用卡总数", example=5)
    active_cards: int = Field(description="活跃卡片数", example=4)
    total_credit_limit: float = Field(description="总信用额度", example=200000.00)
    credit_utilization_rate: float = Field(description="信用利用率", example=25.0)
    
    # 交易统计（汇总级别）
    total_transactions: int = Field(description="交易总数", example=150)
    transactions_30days: int = Field(description="30天内交易数", example=25)
    total_spending: float = Field(description="总支出", example=80000.00)
    spending_30days: float = Field(description="30天内支出", example=5000.00)
    avg_transaction_amount: float = Field(description="平均交易金额", example=533.33)
    
    # 积分和返现统计
    total_points_earned: int = Field(description="累计获得积分", example=80000)
    total_cashback_earned: float = Field(description="累计获得返现", example=800.00)
    
    # 年费统计
    annual_fees_paid: float = Field(description="已支付年费", example=1200.00)
    annual_fees_waived: float = Field(description="已减免年费", example=800.00)
    
    # 提醒统计
    total_reminders: int = Field(description="提醒总数", example=10)
    pending_reminders: int = Field(description="待处理提醒", example=3)


class AdminUserActivityDetail(BaseModel):
    """管理员查看的用户活动详情"""
    
    # 登录活动
    login_count_total: int = Field(description="总登录次数", example=100)
    login_count_30days: int = Field(description="30天内登录次数", example=15)
    login_count_7days: int = Field(description="7天内登录次数", example=5)
    last_login_ip: Optional[str] = Field(description="最后登录IP", example="192.168.1.100")
    last_login_location: Optional[str] = Field(description="最后登录位置", example="北京市")
    
    # 使用活动
    last_transaction_at: Optional[datetime] = Field(description="最后交易时间")
    last_card_added_at: Optional[datetime] = Field(description="最后添加卡片时间")
    last_reminder_set_at: Optional[datetime] = Field(description="最后设置提醒时间")
    
    # 活跃度指标
    days_since_last_login: Optional[int] = Field(description="距离最后登录天数", example=2)
    days_since_last_transaction: Optional[int] = Field(description="距离最后交易天数", example=5)
    activity_score: float = Field(description="活跃度评分（0-100）", example=75.5)


class AdminUserDetailResponse(BaseModel):
    """管理员查看的用户详情响应模型（脱敏）"""
    
    # 基础信息
    id: UUID = Field(description="用户ID")
    username: str = Field(description="用户名", example="testuser")
    email: EmailStr = Field(description="邮箱（部分脱敏）", example="te***@example.com")
    nickname: Optional[str] = Field(description="昵称", example="测试用户")
    phone: Optional[str] = Field(description="手机号（脱敏）", example="138****8000")
    
    # 账户状态
    is_active: bool = Field(description="是否激活", example=True)
    is_verified: bool = Field(description="是否已验证", example=False)
    is_admin: bool = Field(description="是否管理员", example=False)
    
    # 偏好设置
    timezone: str = Field(description="时区", example="Asia/Shanghai")
    language: str = Field(description="语言", example="zh-CN")
    currency: str = Field(description="货币", example="CNY")
    
    # 时间信息
    last_login_at: Optional[datetime] = Field(description="最后登录时间")
    email_verified_at: Optional[datetime] = Field(description="邮箱验证时间")
    created_at: datetime = Field(description="注册时间")
    updated_at: datetime = Field(description="更新时间")
    
    # 统计信息（汇总数据，不涉及具体内容）
    stats: AdminUserStatsDetail = Field(description="用户统计详情")
    
    # 活动信息
    activity: AdminUserActivityDetail = Field(description="用户活动详情")


class UserStatusUpdateRequest(BaseModel):
    """用户状态更新请求模型"""
    
    is_active: bool = Field(
        description="是否激活用户",
        example=True
    )
    
    reason: str = Field(
        min_length=1,
        max_length=200,
        description="状态变更原因，必须提供",
        example="用户违反服务条款，暂时禁用账户"
    )


class UserPermissionUpdateRequest(BaseModel):
    """用户权限更新请求模型"""
    
    is_admin: bool = Field(
        description="是否授予管理员权限",
        example=False
    )
    
    reason: str = Field(
        min_length=1,
        max_length=200,
        description="权限变更原因，必须提供",
        example="授予管理员权限以协助系统管理"
    )


class AdminUserStatsResponse(BaseModel):
    """管理员用户统计响应模型"""
    
    # 用户数量统计
    total_users: int = Field(description="用户总数", example=1000)
    active_users: int = Field(description="活跃用户数", example=800)
    verified_users: int = Field(description="已验证用户数", example=600)
    admin_users: int = Field(description="管理员用户数", example=5)
    
    # 注册趋势
    new_users_today: int = Field(description="今日新增用户", example=5)
    new_users_7days: int = Field(description="7天内新增用户", example=35)
    new_users_30days: int = Field(description="30天内新增用户", example=150)
    
    # 活跃度统计
    active_users_today: int = Field(description="今日活跃用户", example=200)
    active_users_7days: int = Field(description="7天内活跃用户", example=500)
    active_users_30days: int = Field(description="30天内活跃用户", example=700)
    
    # 登录统计
    total_logins_today: int = Field(description="今日总登录次数", example=500)
    failed_logins_today: int = Field(description="今日失败登录次数", example=20)
    unique_ips_today: int = Field(description="今日唯一IP数", example=180)
    
    # 地域分布（TOP5）
    top_locations: List[Dict[str, Any]] = Field(
        description="用户地域分布TOP5",
        example=[
            {"location": "北京市", "count": 200},
            {"location": "上海市", "count": 150},
            {"location": "广州市", "count": 100},
            {"location": "深圳市", "count": 80},
            {"location": "杭州市", "count": 60}
        ]
    )
    
    # 设备分布
    device_stats: Dict[str, int] = Field(
        description="设备类型分布",
        example={
            "mobile": 600,
            "desktop": 300,
            "tablet": 100
        }
    )
    
    # 账户状态分布
    status_distribution: Dict[str, int] = Field(
        description="账户状态分布",
        example={
            "active": 800,
            "inactive": 150,
            "suspended": 30,
            "pending_verification": 20
        }
    )


class AdminUserOperationLog(BaseModel):
    """管理员用户操作日志"""
    
    id: UUID = Field(description="操作日志ID")
    admin_id: UUID = Field(description="操作管理员ID")
    admin_username: str = Field(description="操作管理员用户名", example="admin")
    target_user_id: UUID = Field(description="目标用户ID")
    target_username: str = Field(description="目标用户名", example="testuser")
    
    operation_type: str = Field(
        description="操作类型",
        example="status_update"
    )
    
    operation_description: str = Field(
        description="操作描述",
        example="禁用用户账户"
    )
    
    before_value: Optional[Dict[str, Any]] = Field(
        description="操作前的值",
        example={"is_active": True}
    )
    
    after_value: Optional[Dict[str, Any]] = Field(
        description="操作后的值",
        example={"is_active": False}
    )
    
    reason: str = Field(
        description="操作原因",
        example="用户违反服务条款"
    )
    
    ip_address: Optional[str] = Field(
        description="操作IP地址",
        example="192.168.1.100"
    )
    
    created_at: datetime = Field(
        description="操作时间",
        example="2024-12-01T10:00:00Z"
    ) 