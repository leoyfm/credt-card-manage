"""
自定义异常类
"""
from fastapi import HTTPException
from app.core.logging import app_logger

class APIException(HTTPException):
    """
    基础API异常，支持自定义错误码和详细信息
    """
    def __init__(self, code: int = 400, message: str = "请求错误", error_detail: str = None, error_code: str = None):
        app_logger.error(f"API异常: {code} - {message}")
        super().__init__(
            status_code=code,
            detail={
                "message": message,
                "error_detail": error_detail,
                "error_code": error_code
            }
        ) 