"""
通用响应模型 - API v1

定义所有API接口使用的通用响应格式：
- 统一成功响应格式
- 统一错误响应格式
- 分页响应格式
- 其他通用模型
"""

from datetime import datetime
from typing import Generic, TypeVar, Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar('T')


class ApiResponse(GenericModel, Generic[T]):
    """统一API响应格式"""
    
    success: bool = Field(
        description="请求是否成功",
        example=True
    )
    
    code: int = Field(
        description="响应状态码",
        example=200
    )
    
    message: str = Field(
        description="响应消息",
        example="操作成功"
    )
    
    data: Optional[T] = Field(
        description="响应数据",
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


class PaginationInfo(BaseModel):
    """分页信息"""
    
    current_page: int = Field(
        description="当前页码",
        example=1
    )
    
    page_size: int = Field(
        description="每页数量",
        example=20
    )
    
    total: int = Field(
        description="总记录数",
        example=100
    )
    
    total_pages: int = Field(
        description="总页数",
        example=5
    )
    
    has_next: bool = Field(
        description="是否有下一页",
        example=True
    )
    
    has_prev: bool = Field(
        description="是否有上一页",
        example=False
    )


class ApiPagedResponse(GenericModel, Generic[T]):
    """分页API响应格式"""
    
    success: bool = Field(
        description="请求是否成功",
        example=True
    )
    
    code: int = Field(
        description="响应状态码",
        example=200
    )
    
    message: str = Field(
        description="响应消息",
        example="查询成功"
    )
    
    data: List[T] = Field(
        description="响应数据列表",
        default=[]
    )
    
    pagination: PaginationInfo = Field(
        description="分页信息"
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