"""
统一响应工具类
提供标准化的API响应格式和工具方法
"""
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Type, List, Dict
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

# 从common模块导入响应模型
from app.models.schemas.common import (
    PaginationInfo, 
    ApiResponse, 
    ApiPagedResponse, 
    ApiErrorResponse
)

# 导入分页工具函数
from app.utils.pagination import calculate_skip, validate_pagination_params, calculate_pagination_info


class ResponseUtil:
    """统一响应工具类"""
    
    @staticmethod
    def _serialize_data(data: Any) -> Any:
        """
        序列化数据，处理特殊类型
        
        Args:
            data: 需要序列化的数据
            
        Returns:
            Any: 序列化后的数据
        """
        if data is None:
            return None
        
        # 处理UUID
        if isinstance(data, UUID):
            return str(data)
        
        # 处理Decimal
        if isinstance(data, Decimal):
            return float(data)
        
        # 处理datetime
        if isinstance(data, datetime):
            return data.isoformat()
        
        # 处理Pydantic模型
        if hasattr(data, 'model_dump'):
            dumped = data.model_dump()
            return ResponseUtil._serialize_data(dumped)  # 递归处理转换后的字典
        elif hasattr(data, 'dict'):
            dumped = data.model_dump()
            return ResponseUtil._serialize_data(dumped)  # 递归处理转换后的字典
        
        # 处理列表
        if isinstance(data, list):
            return [ResponseUtil._serialize_data(item) for item in data]
        
        # 处理字典
        if isinstance(data, dict):
            return {key: ResponseUtil._serialize_data(value) for key, value in data.items()}
        
        return data
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        return datetime.now(timezone(timedelta(hours=8))).isoformat()
    
    # ========== 成功响应 ==========
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "操作成功", 
        code: int = status.HTTP_200_OK,
        model: Optional[Type[BaseModel]] = None
    ):
        """
        返回标准成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: HTTP状态码
            model: Pydantic模型类（可选，用于数据验证）
            
        Returns:
            JSONResponse: 标准成功响应
        """
        # 数据序列化
        serialized_data = ResponseUtil._serialize_data(data)
        
        # 用Pydantic模型校验（如果提供）
        if model and data:
            try:
                if isinstance(data, list):
                    serialized_data = [model(**item).model_dump() if isinstance(item, dict) else item for item in data]
                elif isinstance(data, dict):
                    serialized_data = model(**data).model_dump()
            except Exception:
                # 如果验证失败，使用原始序列化数据
                pass
        
        response_data = {
            "success": True,
            "code": code,
            "message": message,
            "data": serialized_data,
            "timestamp": ResponseUtil._get_timestamp()
        }
        
        return JSONResponse(
            status_code=code,
            content=response_data
        )
    
    @staticmethod
    def created(data: Any = None, message: str = "创建成功"):
        """返回创建成功响应"""
        return ResponseUtil.success(
            data=data,
            message=message,
            code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def updated(data: Any = None, message: str = "更新成功"):
        """返回更新成功响应"""
        return ResponseUtil.success(
            data=data,
            message=message,
            code=status.HTTP_200_OK
        )
    
    @staticmethod
    def deleted(message: str = "删除成功"):
        """返回删除成功响应"""
        return ResponseUtil.success(
            data=None,
            message=message,
            code=status.HTTP_200_OK
        )
    
    # ========== 分页响应 ==========
    
    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = "查询成功",
        model: Optional[Type[BaseModel]] = None
    ):
        """
        返回分页响应
        
        Args:
            items: 数据列表
            total: 总数
            page: 当前页码
            page_size: 每页大小
            message: 响应消息
            model: Pydantic模型类（可选）
            
        Returns:
            JSONResponse: 分页响应
        """
        # 验证分页参数
        page, page_size = validate_pagination_params(page, page_size)
        
        # 计算分页信息
        pagination_info = calculate_pagination_info(total, page, page_size)
        
        pagination = PaginationInfo(
            current_page=pagination_info["current_page"],
            page_size=pagination_info["page_size"],
            total=pagination_info["total"],
            total_pages=pagination_info["total_pages"],
            has_next=pagination_info["has_next"],
            has_prev=pagination_info["has_prev"]
        )
        
        # 序列化数据
        serialized_items = ResponseUtil._serialize_data(items)
        
        # 用Pydantic模型校验（如果提供）
        if model and items:
            try:
                serialized_items = [
                    model(**item).model_dump() if isinstance(item, dict) else item 
                    for item in items
                ]
            except Exception:
                # 如果验证失败，使用原始序列化数据
                pass
        
        response_data = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": message,
            "data": serialized_items,
            "pagination": pagination.model_dump(),
            "timestamp": ResponseUtil._get_timestamp()
        }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data
        )
    
    # ========== 错误响应 ==========
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = status.HTTP_400_BAD_REQUEST,
        error_detail: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        """
        返回标准错误响应
        
        Args:
            message: 错误消息
            code: HTTP状态码
            error_detail: 错误详情
            error_code: 错误代码
            
        Returns:
            JSONResponse: 标准错误响应
        """
        response_data = {
            "success": False,
            "code": code,
            "message": message,
            "error_detail": error_detail,
            "error_code": error_code,
            "timestamp": ResponseUtil._get_timestamp()
        }
        
        return JSONResponse(
            status_code=code,
            content=response_data
        )
    
    @staticmethod
    def bad_request(message: str = "请求参数错误", error_detail: Optional[str] = None):
        """返回400错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_400_BAD_REQUEST,
            error_detail=error_detail,
            error_code="BAD_REQUEST"
        )
    
    @staticmethod
    def unauthorized(message: str = "认证失败", error_detail: Optional[str] = None):
        """返回401错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_401_UNAUTHORIZED,
            error_detail=error_detail,
            error_code="UNAUTHORIZED"
        )
    
    @staticmethod
    def forbidden(message: str = "权限不足", error_detail: Optional[str] = None):
        """返回403错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_403_FORBIDDEN,
            error_detail=error_detail,
            error_code="FORBIDDEN"
        )
    
    @staticmethod
    def not_found(message: str = "资源不存在", error_detail: Optional[str] = None):
        """返回404错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_404_NOT_FOUND,
            error_detail=error_detail,
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def conflict(message: str = "资源冲突", error_detail: Optional[str] = None):
        """返回409错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_409_CONFLICT,
            error_detail=error_detail,
            error_code="CONFLICT"
        )
    
    @staticmethod
    def validation_error(message: str = "数据验证失败", errors: Optional[List[Dict]] = None):
        """返回422验证错误响应"""
        error_detail = None
        if errors:
            # 格式化验证错误信息
            error_messages = []
            for error in errors:
                if isinstance(error, dict):
                    loc = error.get('loc', [])
                    msg = error.get('msg', '验证失败')
                    field = '.'.join(str(x) for x in loc) if loc else '未知字段'
                    error_messages.append(f"{field}: {msg}")
            error_detail = "; ".join(error_messages)
        
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_detail=error_detail,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def internal_error(message: str = "服务器内部错误", error_detail: Optional[str] = None):
        """返回500错误响应"""
        return ResponseUtil.error(
            message=message,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_detail=error_detail,
            error_code="INTERNAL_ERROR"
        )
    
    # ========== 工具方法 ==========
    
    @staticmethod
    def format_validation_errors(validation_errors: List) -> List[Dict]:
        """
        格式化Pydantic验证错误
        
        Args:
            validation_errors: Pydantic验证错误列表
            
        Returns:
            List[Dict]: 格式化后的错误信息
        """
        formatted_errors = []
        for error in validation_errors:
            formatted_error = {
                "field": ".".join(str(x) for x in error.get("loc", [])),
                "message": error.get("msg", "验证失败"),
                "type": error.get("type", "validation_error"),
                "input": error.get("input")
            }
            formatted_errors.append(formatted_error)
        
        return formatted_errors
    
    @staticmethod
    def from_exception(exception: Exception, default_message: str = "操作失败") -> JSONResponse:
        """
        从异常创建错误响应
        
        Args:
            exception: 异常对象
            default_message: 默认错误消息
            
        Returns:
            JSONResponse: 错误响应
        """
        # 这里可以根据不同的异常类型返回不同的错误响应
        # 实际实现需要根据项目的异常体系来完善
        
        if hasattr(exception, 'status_code'):
            return ResponseUtil.error(
                message=str(exception),
                code=exception.status_code,
                error_detail=getattr(exception, 'detail', None),
                error_code=getattr(exception, 'error_code', None)
            )
        
        return ResponseUtil.error(
            message=default_message,
            error_detail=str(exception)
        ) 