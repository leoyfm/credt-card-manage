"""统一响应工具类"""

from typing import Any, Optional, Dict, List
from datetime import datetime
import json

class ResponseUtil:
    """统一响应格式工具类"""
    
    @staticmethod
    def _format_timestamp() -> str:
        """格式化时间戳"""
        return datetime.utcnow().isoformat() + "Z"
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200
    ) -> Dict[str, Any]:
        """成功响应"""
        return {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": ResponseUtil._format_timestamp()
        }
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 400,
        error_detail: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """错误响应"""
        return {
            "success": False,
            "code": code,
            "message": message,
            "error_detail": error_detail or {},
            "trace_id": trace_id,
            "timestamp": ResponseUtil._format_timestamp()
        }
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "创建成功"
    ) -> Dict[str, Any]:
        """创建成功响应"""
        return ResponseUtil.success(data=data, message=message, code=201)
    
    @staticmethod
    def deleted(
        message: str = "删除成功"
    ) -> Dict[str, Any]:
        """删除成功响应"""
        return ResponseUtil.success(message=message, code=204)
    
    @staticmethod
    def not_found(
        resource: str = "资源",
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """资源不存在响应"""
        message = f"{resource}不存在"
        error_detail = {"resource_type": resource}
        if resource_id:
            error_detail["resource_id"] = resource_id
        return ResponseUtil.error(
            message=message,
            code=404,
            error_detail=error_detail
        )
    
    @staticmethod
    def validation_error(
        message: str = "数据验证失败",
        field: Optional[str] = None,
        invalid_value: Any = None
    ) -> Dict[str, Any]:
        """数据验证错误响应"""
        error_detail = {}
        if field:
            error_detail["field"] = field
        if invalid_value is not None:
            error_detail["invalid_value"] = str(invalid_value)
        
        return ResponseUtil.error(
            message=message,
            code=422,
            error_detail=error_detail
        )
    
    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "获取成功"
    ) -> Dict[str, Any]:
        """分页响应"""
        total_pages = (total + page_size - 1) // page_size
        
        pagination = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        return ResponseUtil.success(
            data={
                "items": items,
                "pagination": pagination
            },
            message=message
        )
    
    @staticmethod
    def calculate_skip(page: int, page_size: int) -> int:
        """计算跳过的记录数"""
        return (page - 1) * page_size 