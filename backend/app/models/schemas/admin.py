"""
管理员相关数据模型
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.utils.response import PaginationInfo


class UserSummaryResponse(BaseModel):
    """用户摘要信息响应（管理员查看，已脱敏）"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    nickname: Optional[str] = Field(None, description="昵称")
    is_active: bool = Field(..., description="是否激活")
    is_verified: bool = Field(..., description="是否已验证")
    is_admin: bool = Field(..., description="是否管理员")
    timezone: str = Field(..., description="时区")
    language: str = Field(..., description="语言偏好")
    currency: str = Field(..., description="默认货币")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    email_verified_at: Optional[datetime] = Field(None, description="邮箱验证时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 统计信息（不涉及敏感数据详情）
    cards_count: int = Field(0, description="信用卡数量")
    transactions_count: int = Field(0, description="交易记录数量")
    login_logs_count: int = Field(0, description="登录日志数量")


class UserStatusUpdateRequest(BaseModel):
    """用户状态更新请求"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_active": False,
                "reason": "用户违反使用条款"
            }
        }
    )
    
    is_active: bool = Field(..., description="是否激活")
    reason: Optional[str] = Field(None, max_length=200, description="操作原因")


class UserPermissionsUpdateRequest(BaseModel):
    """用户权限更新请求"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_admin": True,
                "is_verified": True,
                "reason": "提升为管理员权限"
            }
        }
    )
    
    is_admin: bool = Field(..., description="是否管理员")
    is_verified: bool = Field(..., description="是否已验证")
    reason: Optional[str] = Field(None, max_length=200, description="操作原因")


class UserDeletionRequest(BaseModel):
    """用户删除请求"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reason": "用户请求删除账户",
                "confirm_username": "username_to_delete"
            }
        }
    )
    
    reason: str = Field(..., min_length=1, max_length=500, description="删除原因")
    confirm_username: str = Field(..., description="确认用户名")


class LoginLogResponse(BaseModel):
    """登录日志响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="日志ID")
    user_id: Optional[UUID] = Field(None, description="用户ID")
    login_type: str = Field(..., description="登录类型")
    login_method: str = Field(..., description="登录方式")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    location: Optional[str] = Field(None, description="地理位置")
    is_success: bool = Field(..., description="是否成功")
    failure_reason: Optional[str] = Field(None, description="失败原因")
    created_at: datetime = Field(..., description="创建时间")


class UserStatisticsResponse(BaseModel):
    """用户统计响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_users": 1000,
                "active_users": 950,
                "verified_users": 800,
                "admin_users": 5,
                "new_users_today": 10,
                "new_users_this_week": 50,
                "new_users_this_month": 200,
                "user_distribution": {
                    "by_timezone": {"Asia/Shanghai": 800, "UTC": 200},
                    "by_language": {"zh-CN": 900, "en-US": 100}
                },
                "login_statistics": {
                    "total_logins_today": 500,
                    "successful_logins_today": 480,
                    "failed_logins_today": 20
                }
            }
        }
    )
    
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    verified_users: int = Field(..., description="已验证用户数")
    admin_users: int = Field(..., description="管理员用户数")
    new_users_today: int = Field(..., description="今日新增用户")
    new_users_this_week: int = Field(..., description="本周新增用户")
    new_users_this_month: int = Field(..., description="本月新增用户")
    
    # 用户分布统计
    user_distribution: dict = Field(..., description="用户分布统计")
    login_statistics: dict = Field(..., description="登录统计")


class AdminUserListResponse(BaseModel):
    """管理员用户列表响应"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(True, description="操作是否成功")
    code: int = Field(200, description="状态码")
    message: str = Field("查询成功", description="响应消息")
    data: List[UserSummaryResponse] = Field(..., description="用户列表")
    pagination: PaginationInfo = Field(..., description="分页信息")
    timestamp: datetime = Field(..., description="响应时间戳")


class AdminUserDetailsResponse(BaseModel):
    """管理员用户详情响应"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(True, description="操作是否成功") 
    code: int = Field(200, description="状态码")
    message: str = Field("查询成功", description="响应消息")
    data: UserSummaryResponse = Field(..., description="用户详情")
    timestamp: datetime = Field(..., description="响应时间戳")


class AdminLoginLogsResponse(BaseModel):
    """管理员登录日志列表响应"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(True, description="操作是否成功")
    code: int = Field(200, description="状态码")
    message: str = Field("查询成功", description="响应消息")
    data: List[LoginLogResponse] = Field(..., description="登录日志列表")
    pagination: PaginationInfo = Field(..., description="分页信息")
    timestamp: datetime = Field(..., description="响应时间戳")


class AdminUserStatisticsResponse(BaseModel):
    """管理员用户统计响应"""
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(True, description="操作是否成功")
    code: int = Field(200, description="状态码")
    message: str = Field("查询成功", description="响应消息")
    data: UserStatisticsResponse = Field(..., description="用户统计数据")
    timestamp: datetime = Field(..., description="响应时间戳")


# ==================== 信用卡管理员模型 ====================

class AdminCardStatisticsResponse(BaseModel):
    """管理员信用卡系统统计响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_cards": 5000,
                "active_cards": 4500,
                "frozen_cards": 400,
                "closed_cards": 100,
                "total_credit_limit": "50000000.00",
                "total_used_limit": "15000000.00",
                "average_utilization": "30.00",
                "cards_by_status": {
                    "active": 4500,
                    "frozen": 400,
                    "closed": 100
                },
                "cards_by_type": {
                    "credit": 4800,
                    "debit": 200
                },
                "cards_by_level": {
                    "普卡": 2000,
                    "金卡": 1500,
                    "白金卡": 1000,
                    "钻石卡": 400,
                    "无限卡": 100
                }
            }
        }
    )
    
    total_cards: int = Field(..., description="总信用卡数量")
    active_cards: int = Field(..., description="活跃信用卡数量")
    frozen_cards: int = Field(..., description="冻结信用卡数量")
    closed_cards: int = Field(..., description="已关闭信用卡数量")
    total_credit_limit: Decimal = Field(..., description="总信用额度")
    total_used_limit: Decimal = Field(..., description="总已用额度")
    average_utilization: Decimal = Field(..., description="平均利用率（百分比）")
    
    # 分类统计
    cards_by_status: Dict[str, int] = Field(..., description="按状态分类统计")
    cards_by_type: Dict[str, int] = Field(..., description="按类型分类统计")
    cards_by_level: Dict[str, int] = Field(..., description="按等级分类统计")


class AdminBankDistributionResponse(BaseModel):
    """管理员银行分布统计响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_banks": 20,
                "bank_distribution": [
                    {
                        "bank_name": "招商银行",
                        "bank_code": "CMB",
                        "card_count": 1000,
                        "percentage": "20.00",
                        "total_credit_limit": "10000000.00",
                        "average_credit_limit": "10000.00"
                    },
                    {
                        "bank_name": "建设银行",
                        "bank_code": "CCB",
                        "card_count": 800,
                        "percentage": "16.00",
                        "total_credit_limit": "8000000.00",
                        "average_credit_limit": "10000.00"
                    }
                ],
                "top_banks": ["招商银行", "建设银行", "工商银行"]
            }
        }
    )
    
    total_banks: int = Field(..., description="银行总数")
    bank_distribution: List[Dict[str, Any]] = Field(..., description="银行分布详情")
    bank_stats: List[Dict[str, Any]] = Field(..., description="银行统计信息", alias="bank_distribution")
    top_banks: List[str] = Field(..., description="前十大银行")


class AdminCardHealthResponse(BaseModel):
    """管理员信用卡健康状况响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_health_score": "85.5",
                "utilization_distribution": {
                    "low_risk": {"range": "0-30%", "count": 2000, "percentage": "40.00"},
                    "medium_risk": {"range": "30-70%", "count": 2000, "percentage": "40.00"},
                    "high_risk": {"range": "70-90%", "count": 800, "percentage": "16.00"},
                    "critical_risk": {"range": "90-100%", "count": 200, "percentage": "4.00"}
                },
                "expiring_soon": {
                    "next_month": 50,
                    "next_3_months": 150,
                    "next_6_months": 300
                },
                "inactive_cards": {
                    "no_transactions_30_days": 500,
                    "no_transactions_90_days": 200,
                    "no_transactions_180_days": 100
                }
            }
        }
    )
    
    overall_health_score: Decimal = Field(..., description="整体健康评分（0-100）")
    utilization_distribution: Dict[str, Dict[str, Any]] = Field(..., description="利用率分布")
    expiring_soon: Dict[str, int] = Field(..., description="即将到期统计")
    inactive_cards: Dict[str, int] = Field(..., description="不活跃卡片统计")


class AdminCardTrendsResponse(BaseModel):
    """管理员信用卡趋势分析响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "analysis_period": "6个月",
                "monthly_trends": [
                    {
                        "month": "2024-07",
                        "new_cards": 100,
                        "closed_cards": 10,
                        "net_growth": 90,
                        "total_cards": 4500,
                        "average_utilization": "28.5"
                    }
                ],
                "growth_rate": "2.5",
                "utilization_trend": "稳定",
                "predictions": {
                    "next_month_new_cards": 105,
                    "next_month_total": 4605
                }
            }
        }
    )
    
    analysis_period: str = Field(..., description="分析周期")
    monthly_trends: List[Dict[str, Any]] = Field(..., description="月度趋势数据")
    monthly_stats: List[Dict[str, Any]] = Field(..., description="月度统计数据", alias="monthly_trends")
    growth_rate: Decimal = Field(..., description="增长率（百分比）")
    growth_prediction: Dict[str, Any] = Field(..., description="增长预测", alias="predictions")
    utilization_trend: str = Field(..., description="利用率趋势描述")
    predictions: Dict[str, Any] = Field(..., description="预测数据")


class AdminUtilizationAnalysisResponse(BaseModel):
    """管理员信用额度利用率分析响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_utilization": "32.5",
                "risk_distribution": {
                    "low_risk": {"count": 3000, "percentage": "60.00"},
                    "medium_risk": {"count": 1500, "percentage": "30.00"},
                    "high_risk": {"count": 400, "percentage": "8.00"},
                    "critical_risk": {"count": 100, "percentage": "2.00"}
                },
                "utilization_by_bank": [
                    {"bank_name": "招商银行", "average_utilization": "35.2"},
                    {"bank_name": "建设银行", "average_utilization": "28.8"}
                ],
                "utilization_by_card_level": [
                    {"card_level": "普卡", "average_utilization": "45.2"},
                    {"card_level": "白金卡", "average_utilization": "25.8"}
                ],
                "recommendations": [
                    "建议关注利用率超过80%的用户",
                    "普卡用户利用率偏高，可推荐升级"
                ]
            }
        }
    )
    
    overall_utilization: Decimal = Field(..., description="整体利用率（百分比）")
    risk_distribution: Dict[str, Dict[str, Any]] = Field(..., description="风险分布")
    utilization_by_bank: List[Dict[str, Any]] = Field(..., description="按银行分析")
    utilization_by_card_level: List[Dict[str, Any]] = Field(..., description="按卡片等级分析")
    recommendations: List[str] = Field(..., description="分析建议")


class AdminExpiryAlertsResponse(BaseModel):
    """管理员即将到期卡片统计响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "analysis_months": 3,
                "expiring_cards": {
                    "next_month": 50,
                    "next_2_months": 80,
                    "next_3_months": 120
                },
                "expiring_by_bank": [
                    {"bank_name": "招商银行", "count": 25},
                    {"bank_name": "建设银行", "count": 20}
                ],
                "renewal_rate": "85.5",
                "recommendations": [
                    "提前通知用户更新卡片信息",
                    "关注续卡率较低的银行"
                ]
            }
        }
    )
    
    analysis_months: int = Field(..., description="分析月数")
    expiring_cards: Dict[str, int] = Field(..., description="即将到期卡片统计")
    expiring_by_bank: List[Dict[str, Any]] = Field(..., description="按银行分类到期统计")
    renewal_rate: Decimal = Field(..., description="历史续卡率（百分比）")
    recommendations: List[str] = Field(..., description="管理建议")


class AdminAnnualFeeSummaryResponse(BaseModel):
    """管理员年费管理概览响应"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 2024,
                "total_cards_with_fee": 2000,
                "total_base_fee": "2000000.00",
                "total_actual_fee": "1200000.00",
                "total_waived_amount": "800000.00",
                "waiver_rate": "40.00",
                "fee_status_distribution": {
                    "paid": 800,
                    "waived": 800,
                    "pending": 300,
                    "overdue": 100
                },
                "waiver_methods": {
                    "spending_amount": 400,
                    "transaction_count": 300,
                    "points_redeem": 100
                },
                "revenue_impact": {
                    "collected_fees": "1200000.00",
                    "waived_fees": "800000.00",
                    "collection_rate": "60.00"
                }
            }
        }
    )
    
    year: int = Field(..., description="统计年份")
    total_cards_with_fee: int = Field(..., description="有年费的卡片总数")
    total_base_fee: Decimal = Field(..., description="基础年费总额")
    total_actual_fee: Decimal = Field(..., description="实际收取年费总额")
    total_waived_amount: Decimal = Field(..., description="减免年费总额")
    total_revenue: Decimal = Field(..., description="总收入", alias="total_actual_fee")
    waiver_rate: Decimal = Field(..., description="减免率（百分比）")
    
    # 详细分布
    fee_status_distribution: Dict[str, int] = Field(..., description="年费状态分布")
    waiver_methods: Dict[str, int] = Field(..., description="减免方式统计")
    waiver_stats: Dict[str, int] = Field(..., description="减免统计", alias="waiver_methods")
    revenue_impact: Dict[str, Any] = Field(..., description="收入影响分析") 