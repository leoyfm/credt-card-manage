"""
通用Pydantic模型

包含分页、响应等通用模型定义
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


class PaginationInfo(BaseModel):
    """分页信息模型"""
    current_page: int = Field(..., description="当前页码", example=1)
    page_size: int = Field(..., description="每页数量", example=20)
    total: int = Field(..., description="总记录数", example=100)
    total_pages: int = Field(..., description="总页数", example=5)
    has_next: bool = Field(..., description="是否有下一页", example=True)
    has_prev: bool = Field(..., description="是否有上一页", example=False)


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="操作是否成功", example=True)
    code: int = Field(200, description="响应状态码", example=200)
    message: str = Field("操作成功", description="响应消息", example="操作成功")
    timestamp: str = Field(..., description="响应时间戳")


class ApiResponse(BaseResponse):
    """API响应模型"""
    data: Optional[Any] = Field(None, description="响应数据")


class ApiPagedResponse(BaseResponse):
    """分页API响应模型"""
    data: list = Field([], description="响应数据列表")
    pagination: PaginationInfo = Field(..., description="分页信息")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="操作是否成功", example=False)
    code: int = Field(..., description="错误状态码", example=400)
    message: str = Field(..., description="错误消息", example="参数错误")
    error_detail: Optional[str] = Field(None, description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: str = Field(..., description="响应时间戳") 