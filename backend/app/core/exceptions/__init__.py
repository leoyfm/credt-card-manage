"""异常处理包"""

from .custom import (
    BaseAPIException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    BusinessLogicError,
    ExternalServiceError,
    RateLimitError,
    DatabaseError,
    ConfigurationError
)

from .handlers import (
    base_exception_handler,
    http_exception_handler,
    general_exception_handler
)

__all__ = [
    "BaseAPIException",
    "ValidationError", 
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "BusinessLogicError",
    "ExternalServiceError",
    "RateLimitError",
    "DatabaseError",
    "ConfigurationError",
    "base_exception_handler",
    "http_exception_handler",
    "general_exception_handler"
] 