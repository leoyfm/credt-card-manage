"""
自定义异常类
"""
from fastapi import HTTPException
from app.core.logging import app_logger
from typing import Optional


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


# ========== 认证授权异常 ==========

class AuthenticationError(APIException):
    """认证失败异常"""
    def __init__(self, message: str = "认证失败", error_detail: Optional[str] = None):
        super().__init__(
            code=401,
            message=message,
            error_detail=error_detail,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(APIException):
    """授权失败异常"""
    def __init__(self, message: str = "权限不足", error_detail: Optional[str] = None):
        super().__init__(
            code=403,
            message=message,
            error_detail=error_detail,
            error_code="AUTHORIZATION_ERROR"
        )


# ========== 业务逻辑异常 ==========

class ValidationError(APIException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败", error_detail: Optional[str] = None):
        super().__init__(
            code=422,
            message=message,
            error_detail=error_detail,
            error_code="VALIDATION_ERROR"
        )


class BusinessRuleError(APIException):
    """业务规则异常"""
    def __init__(self, message: str = "业务规则违反", error_detail: Optional[str] = None):
        super().__init__(
            code=400,
            message=message,
            error_detail=error_detail,
            error_code="BUSINESS_RULE_ERROR"
        )


class ResourceNotFoundError(APIException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在", error_detail: Optional[str] = None):
        super().__init__(
            code=404,
            message=message,
            error_detail=error_detail,
            error_code="RESOURCE_NOT_FOUND"
        )


class ResourceConflictError(APIException):
    """资源冲突异常"""
    def __init__(self, message: str = "资源冲突", error_detail: Optional[str] = None):
        super().__init__(
            code=409,
            message=message,
            error_detail=error_detail,
            error_code="RESOURCE_CONFLICT"
        )


# ========== 系统异常 ==========

class DatabaseError(APIException):
    """数据库操作异常"""
    def __init__(self, message: str = "数据库操作失败", error_detail: Optional[str] = None):
        super().__init__(
            code=500,
            message=message,
            error_detail=error_detail,
            error_code="DATABASE_ERROR"
        )


class ExternalServiceError(APIException):
    """外部服务异常"""
    def __init__(self, message: str = "外部服务异常", error_detail: Optional[str] = None):
        super().__init__(
            code=503,
            message=message,
            error_detail=error_detail,
            error_code="EXTERNAL_SERVICE_ERROR"
        )


class RateLimitError(APIException):
    """请求限流异常"""
    def __init__(self, message: str = "请求过于频繁", error_detail: Optional[str] = None):
        super().__init__(
            code=429,
            message=message,
            error_detail=error_detail,
            error_code="RATE_LIMIT_ERROR"
        ) 