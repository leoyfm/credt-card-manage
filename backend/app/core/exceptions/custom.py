"""自定义异常类"""

from typing import Any, Dict, Optional
import uuid

class BaseAPIException(Exception):
    """API异常基类"""
    
    def __init__(
        self,
        message: str,
        error_code: int = 5000,
        error_detail: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.error_detail = error_detail or {}
        self.status_code = status_code
        self.trace_id = str(uuid.uuid4())
        super().__init__(self.message)

class ValidationError(BaseAPIException):
    """数据验证错误 (400)"""
    
    def __init__(
        self,
        message: str = "数据验证失败",
        field: Optional[str] = None,
        invalid_value: Any = None,
        error_code: int = 4001
    ):
        error_detail = {}
        if field:
            error_detail["field"] = field
        if invalid_value is not None:
            error_detail["invalid_value"] = str(invalid_value)
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=400
        )

class AuthenticationError(BaseAPIException):
    """认证错误 (401)"""
    
    def __init__(
        self,
        message: str = "认证失败",
        error_code: int = 4011
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401
        )

class AuthorizationError(BaseAPIException):
    """授权错误 (403)"""
    
    def __init__(
        self,
        message: str = "权限不足",
        required_permission: Optional[str] = None,
        error_code: int = 4031
    ):
        error_detail = {}
        if required_permission:
            error_detail["required_permission"] = required_permission
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=403
        )

class ResourceNotFoundError(BaseAPIException):
    """资源不存在错误 (404)"""
    
    def __init__(
        self,
        resource_type: str = "资源",
        resource_id: Optional[str] = None,
        error_code: int = 4041
    ):
        message = f"{resource_type}不存在"
        error_detail = {"resource_type": resource_type}
        if resource_id:
            error_detail["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=404
        )

class BusinessLogicError(BaseAPIException):
    """业务逻辑错误 (422)"""
    
    def __init__(
        self,
        message: str = "业务逻辑错误",
        business_code: Optional[str] = None,
        error_code: int = 4221
    ):
        error_detail = {}
        if business_code:
            error_detail["business_code"] = business_code
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=422
        )

class ExternalServiceError(BaseAPIException):
    """外部服务错误 (502)"""
    
    def __init__(
        self,
        service_name: str,
        message: str = "外部服务错误",
        error_code: int = 5021
    ):
        error_detail = {"service_name": service_name}
        
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=502
        )

class RateLimitError(BaseAPIException):
    """请求频率限制错误 (429)"""
    
    def __init__(
        self,
        message: str = "请求过于频繁",
        retry_after: Optional[int] = None,
        error_code: int = 4291
    ):
        error_detail = {}
        if retry_after:
            error_detail["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=429
        )

class DatabaseError(BaseAPIException):
    """数据库错误 (500)"""
    
    def __init__(
        self,
        message: str = "数据库操作失败",
        operation: Optional[str] = None,
        error_code: int = 5001
    ):
        error_detail = {}
        if operation:
            error_detail["operation"] = operation
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=500
        )

class ConfigurationError(BaseAPIException):
    """配置错误 (500)"""
    
    def __init__(
        self,
        message: str = "系统配置错误",
        config_key: Optional[str] = None,
        error_code: int = 5002
    ):
        error_detail = {}
        if config_key:
            error_detail["config_key"] = config_key
            
        super().__init__(
            message=message,
            error_code=error_code,
            error_detail=error_detail,
            status_code=500
        ) 