"""
请求日志中间件
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import app_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app, log_body: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.log_body = log_body
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # 记录请求信息
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "headers": dict(request.headers) if self._should_log_headers() else {},
        }
        
        # 记录请求体（如果启用）
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await self._get_request_body(request)
                if body:
                    request_info["body"] = body
            except Exception as e:
                request_info["body_error"] = str(e)
        
        app_logger.info(f"请求开始", extra=request_info)
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            response_info = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
                "response_headers": dict(response.headers) if self._should_log_headers() else {}
            }
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # 根据状态码选择日志级别
            if response.status_code >= 500:
                app_logger.error(f"请求完成 - 服务器错误", extra=response_info)
            elif response.status_code >= 400:
                app_logger.warning(f"请求完成 - 客户端错误", extra=response_info)
            else:
                app_logger.info(f"请求完成 - 成功", extra=response_info)
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            error_info = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time": round(process_time, 4)
            }
            app_logger.error(f"请求异常", extra=error_info)
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直连IP
        return request.client.host if request.client else "unknown"
    
    async def _get_request_body(self, request: Request) -> str:
        """获取请求体内容"""
        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                return f"<body too large: {len(body)} bytes>"
            
            # 尝试解码为文本
            try:
                return body.decode("utf-8")
            except UnicodeDecodeError:
                return f"<binary data: {len(body)} bytes>"
        except Exception:
            return "<unable to read body>"
    
    def _should_log_headers(self) -> bool:
        """是否应该记录请求头"""
        # 在生产环境中可能需要关闭敏感头信息的记录
        return True
    
    def _filter_sensitive_headers(self, headers: dict) -> dict:
        """过滤敏感请求头"""
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", 
            "x-auth-token", "password"
        }
        
        return {
            k: "***" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        } 