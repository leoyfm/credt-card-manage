"""
通用响应模型

提供统一的API响应格式、分页响应格式等通用模型。
"""

from typing import TypeVar, Generic, List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

# 泛型类型变量
T = TypeVar('T')

class PaginationInfo(BaseModel):
    """分页信息模型"""
    page: int = Field(..., description="当前页码", example=1)
    page_size: int = Field(..., description="每页数量", example=20)
    total: int = Field(..., description="总记录数", example=100)
    total_pages: int = Field(..., description="总页数", example=5)
    has_next: bool = Field(..., description="是否有下一页", example=True)
    has_prev: bool = Field(..., description="是否有上一页", example=False)


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="请求是否成功", example=True)
    code: int = Field(..., description="响应状态码", example=200)
    message: str = Field(..., description="响应消息", example="操作成功")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ApiPagedResponse(BaseModel):
    """分页响应模型"""
    success: bool = Field(..., description="请求是否成功", example=True)
    code: int = Field(..., description="响应状态码", example=200)
    message: str = Field(..., description="响应消息", example="操作成功")
    data: Optional[Any] = Field(None, description="响应数据")
    pagination: Optional[PaginationInfo] = Field(None, description="分页信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ListQuery(BaseModel):
    """列表查询基础模型"""
    page: int = Field(1, ge=1, description="页码，从1开始", example=1)
    page_size: int = Field(20, ge=1, le=100, description="每页数量，最大100", example=20)
    keyword: str = Field("", description="搜索关键词", example="")


class TimestampMixin(BaseModel):
    """时间戳混入模型"""
    created_at: datetime = Field(
        description="创建时间",
        example="2024-12-01T10:00:00Z"
    )
    
    updated_at: datetime = Field(
        description="更新时间", 
        example="2024-12-01T10:00:00Z"
    )


class IdMixin(BaseModel):
    """ID混入模型"""
    id: UUID = Field(description="唯一标识符")


class UserInfoMixin(BaseModel):
    """用户信息混入模型"""
    created_by: Optional[UUID] = Field(
        description="创建者ID",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    updated_by: Optional[UUID] = Field(
        description="更新者ID",
        example="550e8400-e29b-41d4-a716-446655440000"
    )


class StatusMixin(BaseModel):
    """状态混入模型"""
    is_active: bool = Field(
        True,
        description="是否激活",
        example=True
    )


class AuditMixin(TimestampMixin, UserInfoMixin):
    """审计混入模型（包含时间戳和用户信息）"""
    last_updated: datetime = Field(
        description="最后更新时间",
        example="2024-12-01T10:00:00Z"
    )


class ApiErrorResponse(BaseModel):
    """错误响应格式"""
    
    success: bool = Field(
        description="请求是否成功",
        example=False
    )
    
    code: int = Field(
        description="错误状态码",
        example=400
    )
    
    message: str = Field(
        description="错误消息",
        example="请求参数错误"
    )
    
    error_detail: Optional[str] = Field(
        description="错误详情",
        example="字段validation失败",
        default=None
    )
    
    error_code: Optional[str] = Field(
        description="错误代码",
        example="VALIDATION_ERROR",
        default=None
    )
    
    timestamp: datetime = Field(
        description="响应时间戳",
        example="2024-12-01T10:00:00Z"
    )
    
    trace_id: Optional[str] = Field(
        description="请求追踪ID",
        example="abc123def456",
        default=None
    )
    
    help_url: Optional[str] = Field(
        description="帮助文档链接",
        example="https://api-docs.example.com/errors/validation",
        default=None
    )


class SuccessMessage(BaseModel):
    """简单成功消息"""
    
    message: str = Field(
        description="成功消息",
        example="操作完成"
    )
    
    timestamp: datetime = Field(
        description="操作时间",
        example="2024-12-01T10:00:00Z"
    )


class ValidationError(BaseModel):
    """字段验证错误"""
    
    field: str = Field(
        description="错误字段名",
        example="email"
    )
    
    message: str = Field(
        description="错误消息",
        example="邮箱格式不正确"
    )
    
    invalid_value: Optional[Any] = Field(
        description="无效的值",
        example="invalid-email",
        default=None
    )


class ApiValidationErrorResponse(BaseModel):
    """字段验证错误响应"""
    
    success: bool = Field(
        description="请求是否成功",
        example=False
    )
    
    code: int = Field(
        description="错误状态码",
        example=422
    )
    
    message: str = Field(
        description="错误消息",
        example="请求参数验证失败"
    )
    
    errors: List[ValidationError] = Field(
        description="验证错误列表",
        example=[
            {
                "field": "email",
                "message": "邮箱格式不正确",
                "invalid_value": "invalid-email"
            }
        ]
    )
    
    timestamp: datetime = Field(
        description="响应时间戳",
        example="2024-12-01T10:00:00Z"
    )
    
    trace_id: Optional[str] = Field(
        description="请求追踪ID",
        example="abc123def456",
        default=None
    )


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(
        description="服务状态",
        example="healthy"
    )
    
    version: str = Field(
        description="API版本",
        example="v1.0.0"
    )
    
    timestamp: datetime = Field(
        description="检查时间",
        example="2024-12-01T10:00:00Z"
    )
    
    uptime: str = Field(
        description="运行时间",
        example="2 days, 5 hours"
    )
    
    dependencies: Dict[str, str] = Field(
        description="依赖服务状态",
        example={
            "database": "healthy",
            "redis": "healthy",
            "external_api": "healthy"
        }
    )


class SystemInfoResponse(BaseModel):
    """系统信息响应"""
    
    api_version: str = Field(
        description="API版本",
        example="v1.0.0"
    )
    
    build_version: str = Field(
        description="构建版本",
        example="2024.12.01.001"
    )
    
    environment: str = Field(
        description="运行环境",
        example="production"
    )
    
    server_time: datetime = Field(
        description="服务器时间",
        example="2024-12-01T10:00:00Z"
    )
    
    timezone: str = Field(
        description="服务器时区",
        example="Asia/Shanghai"
    )
    
    supported_features: List[str] = Field(
        description="支持的功能特性",
        example=[
            "user_management",
            "card_management", 
            "transaction_tracking",
            "annual_fee_management",
            "reminder_system"
        ]
    )


class ApiMetrics(BaseModel):
    """API指标信息"""
    
    total_requests: int = Field(
        description="总请求数",
        example=10000
    )
    
    success_rate: float = Field(
        description="成功率（百分比）",
        example=99.5
    )
    
    avg_response_time: float = Field(
        description="平均响应时间（毫秒）",
        example=150.5
    )
    
    active_users: int = Field(
        description="活跃用户数",
        example=500
    )
    
    last_updated: datetime = Field(
        description="最后更新时间",
        example="2024-12-01T10:00:00Z"
    )


# 别名定义（兼容旧代码）
BaseResponse = ApiResponse
BasePaginatedResponse = ApiPagedResponse
BaseQueryParams = ListQuery 