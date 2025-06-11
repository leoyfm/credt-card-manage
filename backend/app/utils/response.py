"""
统一响应工具
"""
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Any, Optional, Type
from pydantic import BaseModel

class ResponseUtil:
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200, model: Optional[Type[BaseModel]] = None):
        """
        返回标准成功响应
        """
        if model and data:
            # 用Pydantic模型校验和序列化
            data = model(**data).dict()
        return JSONResponse(
            status_code=code,
            content={
                "success": True,
                "code": code,
                "message": message,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    @staticmethod
    def error(message: str = "操作失败", code: int = 400, error_detail: Optional[str] = None, error_code: Optional[str] = None):
        """
        返回标准错误响应
        """
        return JSONResponse(
            status_code=code,
            content={
                "success": False,
                "code": code,
                "message": message,
                "error_detail": error_detail,
                "error_code": error_code,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ) 