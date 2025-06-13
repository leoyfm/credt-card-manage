"""
通用Pydantic模型

包含项目中通用的数据模型定义
"""

from typing import Optional, Any, List, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

T = TypeVar('T')


class PaginationInfo(BaseModel):
    """分页信息模型"""
    current_page: int = Field(..., description="当前页码", example=1)
    page_size: int = Field(..., description="每页数量", example=20)
    total: int = Field(..., description="总记录数", example=100)
    total_pages: int = Field(..., description="总页数", example=5)
    has_next: bool = Field(..., description="是否有下一页", example=True)
    has_prev: bool = Field(..., description="是否有上一页", example=False)


class ApiResponse(BaseModel, Generic[T]):
    """标准API响应模型"""
    success: bool = Field(True, description="操作是否成功", example=True)
    code: int = Field(200, description="响应状态码", example=200)
    message: str = Field("操作成功", description="响应消息", example="操作成功")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")


class ApiPagedResponse(BaseModel, Generic[T]):
    """分页API响应模型"""
    success: bool = Field(True, description="操作是否成功", example=True)
    code: int = Field(200, description="响应状态码", example=200)
    message: str = Field("查询成功", description="响应消息", example="查询成功")
    data: List[T] = Field([], description="响应数据列表")
    pagination: PaginationInfo = Field(..., description="分页信息")
    timestamp: str = Field(..., description="响应时间戳")


class ApiErrorResponse(BaseModel):
    """错误API响应模型"""
    success: bool = Field(False, description="操作是否成功", example=False)
    code: int = Field(..., description="错误状态码", example=400)
    message: str = Field(..., description="错误消息", example="参数错误")
    error_detail: Optional[str] = Field(None, description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: str = Field(..., description="响应时间戳")


class BaseEntity(BaseModel):
    """基础实体模型"""
    id: UUID = Field(..., description="唯一标识")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class SortOrder(BaseModel):
    """排序模型"""
    field: str = Field(..., description="排序字段", example="created_at")
    direction: str = Field("desc", description="排序方向", example="desc")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "created_at",
                "direction": "desc"
            }
        }


class QueryFilter(BaseModel):
    """查询过滤器基类"""
    keyword: str = Field("", description="搜索关键词", json_schema_extra={"example": ""})
    page: int = Field(1, ge=1, description="页码，从1开始", json_schema_extra={"example": 1})
    page_size: int = Field(20, ge=1, le=100, description="每页数量，最大100", json_schema_extra={"example": 20})
    sort: Optional[SortOrder] = Field(None, description="排序设置") 