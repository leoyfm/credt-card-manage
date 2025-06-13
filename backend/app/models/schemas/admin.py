"""
管理员相关数据模型
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

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