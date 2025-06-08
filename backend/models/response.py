from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """
    统一API响应格式
    
    所有API接口都使用此统一响应格式，确保前端处理的一致性。
    """
    success: bool = Field(
        ..., 
        description="请求是否成功，true表示成功，false表示失败",
        example=True
    )
    code: int = Field(
        ..., 
        description="HTTP状态码，如200、404、500等",
        example=200
    )
    message: str = Field(
        ..., 
        description="响应消息，用于描述操作结果",
        example="操作成功"
    )
    data: Optional[T] = Field(
        None, 
        description="响应数据，根据接口不同而变化，可能为null、对象或数组"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, 
        description="响应时间戳，ISO 8601格式",
        example="2024-01-15T10:30:00.000Z"
    )

class PaginationInfo(BaseModel):
    """
    分页信息模型
    
    包含分页相关的所有信息，用于前端分页组件显示。
    """
    total: int = Field(
        ..., 
        description="总记录数",
        example=150
    )
    page: int = Field(
        ..., 
        description="当前页码，从1开始",
        example=1
    )
    size: int = Field(
        ..., 
        description="每页大小，即当前页实际返回的记录数",
        example=20
    )
    pages: int = Field(
        ..., 
        description="总页数，根据总记录数和每页大小计算得出",
        example=8
    )

class PagedResponse(BaseModel, Generic[T]):
    """
    分页响应数据模型
    
    包含分页数据列表和分页信息。
    """
    items: list[T] = Field(
        ..., 
        description="当前页的数据列表"
    )
    pagination: PaginationInfo = Field(
        ..., 
        description="分页信息"
    )

class ApiPagedResponse(BaseModel, Generic[T]):
    """
    统一分页API响应格式
    
    用于所有需要分页的列表接口，提供统一的分页响应结构。
    """
    success: bool = Field(
        ..., 
        description="请求是否成功",
        example=True
    )
    code: int = Field(
        ..., 
        description="HTTP状态码",
        example=200
    )
    message: str = Field(
        ..., 
        description="响应消息",
        example="获取列表成功"
    )
    data: Optional[PagedResponse[T]] = Field(
        None, 
        description="分页响应数据，包含items数组和pagination信息"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, 
        description="响应时间戳",
        example="2024-01-15T10:30:00.000Z"
    ) 