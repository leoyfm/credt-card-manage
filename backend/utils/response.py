from typing import Any, Optional, TypeVar, List
from fastapi import status
from models.response import ApiResponse, ApiPagedResponse, PagedResponse, PaginationInfo
import math

T = TypeVar('T')

class ResponseUtil:
    """
    API响应工具类
    
    提供统一的API响应格式工具方法，确保所有接口返回一致的数据结构。
    包含成功响应、错误响应、分页响应等常用方法。
    """
    
    @staticmethod
    def success(
        data: Optional[T] = None,
        message: str = "操作成功",
        code: int = status.HTTP_200_OK
    ) -> ApiResponse[T]:
        """
        成功响应
        
        用于返回操作成功的统一响应格式。
        
        参数:
        - data: 响应数据，可以是任意类型
        - message: 成功消息，默认为"操作成功"
        - code: HTTP状态码，默认为200
        """
        return ApiResponse(
            success=True,
            code=code,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[T] = None
    ) -> ApiResponse[T]:
        """错误响应"""
        return ApiResponse(
            success=False,
            code=code,
            message=message,
            data=data
        )
    
    @staticmethod
    def created(
        data: Optional[T] = None,
        message: str = "创建成功"
    ) -> ApiResponse[T]:
        """创建成功响应"""
        return ResponseUtil.success(
            data=data,
            message=message,
            code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def deleted(message: str = "删除成功") -> ApiResponse[None]:
        """删除成功响应"""
        return ResponseUtil.success(
            message=message,
            code=status.HTTP_204_NO_CONTENT
        )
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> ApiResponse[None]:
        """资源不存在响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> ApiResponse[None]:
        """未授权响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message: str = "访问被禁止") -> ApiResponse[None]:
        """禁止访问响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def validation_error(message: str = "参数验证失败") -> ApiResponse[None]:
        """参数验证错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def server_error(message: str = "服务器内部错误") -> ApiResponse[None]:
        """服务器错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def paginated(
        items: List[T],
        total: int,
        current_page: int,
        page_size: int,
        message: str = "获取成功"
    ) -> ApiPagedResponse[T]:
        """
        分页响应
        
        用于返回分页数据的统一响应格式，包含数据列表和分页信息。
        
        参数:
        - items: 当前页的数据列表
        - total: 总记录数
        - current_page: 当前页码
        - page_size: 每页大小
        - message: 响应消息
        """
        pages = math.ceil(total / page_size) if page_size > 0 else 0
        
        pagination = PaginationInfo(
            total=total,
            current_page=current_page,
            page_size=page_size,
            total_pages=pages
        )
        
        paged_data = PagedResponse(
            items=items,
            pagination=pagination
        )
        
        return ApiPagedResponse(
            success=True,
            code=status.HTTP_200_OK,
            message=message,
            data=paged_data
        )
    
    @staticmethod
    def calculate_skip(page: int, page_size: int) -> int:
        """
        根据页码和页大小计算跳过的记录数
        
        用于计算数据库查询中的OFFSET值。
        
        参数:
        - page: 页码，从1开始
        - page_size: 每页大小
        
        返回:
        - 需要跳过的记录数
        """
        return (page - 1) * page_size 