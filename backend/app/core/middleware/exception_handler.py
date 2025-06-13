"""
全局异常处理中间件
"""
import traceback
from datetime import datetime, timezone
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import app_logger
from app.core.exceptions.custom import (
    APIException,
    ValidationError,
    ResourceNotFoundError,
    BusinessRuleError,
    AuthenticationError,
    AuthorizationError
)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self._handle_exception(request, exc)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理异常并返回标准化响应"""
        
        # 获取请求ID
        request_id = getattr(request.state, "request_id", "unknown")
        
        # 构建基础错误信息
        error_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc() if self.debug else None
        }
        
        # 根据异常类型处理
        if isinstance(exc, APIException):
            return await self._handle_custom_exception(exc, error_info)
        elif isinstance(exc, ValueError):
            return await self._handle_validation_exception(exc, error_info)
        elif isinstance(exc, PermissionError):
            return await self._handle_permission_exception(exc, error_info)
        else:
            return await self._handle_unknown_exception(exc, error_info)
    
    async def _handle_custom_exception(self, exc: APIException, error_info: dict) -> JSONResponse:
        """处理自定义异常"""
        
        # 根据异常类型选择日志级别
        if isinstance(exc, (ValidationError, ResourceNotFoundError)):
            app_logger.warning(f"客户端错误: {exc}", extra=error_info)
        elif isinstance(exc, (AuthenticationError, AuthorizationError)):
            app_logger.warning(f"认证/授权错误: {exc}", extra=error_info)
        elif isinstance(exc, BusinessRuleError):
            app_logger.info(f"业务规则错误: {exc}", extra=error_info)
        else:
            app_logger.error(f"自定义异常: {exc}", extra=error_info)
        
        # 构建响应
        detail = exc.detail if hasattr(exc, 'detail') else {}
        if isinstance(detail, dict):
            response_data = {
                "success": False,
                "code": exc.status_code,
                "message": detail.get("message", "请求错误"),
                "error_code": detail.get("error_code", "UNKNOWN_ERROR"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # 在调试模式下添加详细信息
            if self.debug:
                response_data["error_detail"] = detail.get("error_detail")
                response_data["request_id"] = error_info["request_id"]
        else:
            response_data = {
                "success": False,
                "code": exc.status_code,
                "message": str(detail),
                "error_code": "UNKNOWN_ERROR",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if self.debug:
                response_data["request_id"] = error_info["request_id"]
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    async def _handle_validation_exception(self, exc: ValueError, error_info: dict) -> JSONResponse:
        """处理验证异常"""
        app_logger.warning(f"验证错误: {exc}", extra=error_info)
        
        response_data = {
            "success": False,
            "code": 400,
            "message": "请求参数验证失败",
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if self.debug:
            response_data["error_detail"] = str(exc)
            response_data["request_id"] = error_info["request_id"]
        
        return JSONResponse(status_code=400, content=response_data)
    
    async def _handle_permission_exception(self, exc: PermissionError, error_info: dict) -> JSONResponse:
        """处理权限异常"""
        app_logger.warning(f"权限错误: {exc}", extra=error_info)
        
        response_data = {
            "success": False,
            "code": 403,
            "message": "权限不足",
            "error_code": "PERMISSION_DENIED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if self.debug:
            response_data["error_detail"] = str(exc)
            response_data["request_id"] = error_info["request_id"]
        
        return JSONResponse(status_code=403, content=response_data)
    
    async def _handle_unknown_exception(self, exc: Exception, error_info: dict) -> JSONResponse:
        """处理未知异常"""
        app_logger.error(f"未捕获异常: {exc}", extra=error_info)
        
        response_data = {
            "success": False,
            "code": 500,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 在调试模式下提供更多信息
        if self.debug:
            response_data["error_detail"] = str(exc)
            response_data["exception_type"] = type(exc).__name__
            response_data["request_id"] = error_info["request_id"]
            response_data["traceback"] = traceback.format_exc()
        
        return JSONResponse(status_code=500, content=response_data)
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直连IP
        return request.client.host if request.client else "unknown" 