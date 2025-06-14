"""
统一异常管理模块

提供项目中使用的所有自定义异常类，支持统一的错误处理和响应格式
"""

from .custom import (
    # 基础异常
    APIException,
    
    # 认证授权异常
    AuthenticationError,
    AuthorizationError,
    
    # 业务逻辑异常
    ValidationError,
    BusinessRuleError,
    ResourceNotFoundError,
    ResourceConflictError,
    
    # 系统异常
    DatabaseError,
    ExternalServiceError,
    RateLimitError
)

__all__ = [
    "APIException",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "BusinessRuleError",
    "ResourceNotFoundError",
    "ResourceConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "RateLimitError"
] 