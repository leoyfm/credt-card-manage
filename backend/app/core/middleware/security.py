"""
安全中间件
"""
import time
from collections import defaultdict, deque
from typing import Callable, Dict, Deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import app_logger


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(
        self,
        app,
        enable_security_headers: bool = True,
        enable_rate_limiting: bool = True,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        enable_ip_blocking: bool = True,
        max_failed_attempts: int = 5,
        block_duration: int = 300
    ):
        super().__init__(app)
        self.enable_security_headers = enable_security_headers
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.enable_ip_blocking = enable_ip_blocking
        self.max_failed_attempts = max_failed_attempts
        self.block_duration = block_duration
        
        # 速率限制存储
        self.rate_limit_storage: Dict[str, Deque[float]] = defaultdict(deque)
        
        # IP阻止存储
        self.blocked_ips: Dict[str, float] = {}
        self.failed_attempts: Dict[str, int] = defaultdict(int)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        
        # 检查IP是否被阻止
        if self.enable_ip_blocking and self._is_ip_blocked(client_ip):
            app_logger.warning(f"阻止的IP访问: {client_ip}", extra={
                "client_ip": client_ip,
                "path": request.url.path,
                "method": request.method
            })
            return self._create_blocked_response()
        
        # 检查速率限制
        if self.enable_rate_limiting and not self._check_rate_limit(client_ip):
            app_logger.warning(f"速率限制触发: {client_ip}", extra={
                "client_ip": client_ip,
                "path": request.url.path,
                "method": request.method,
                "rate_limit": f"{self.rate_limit_requests}/{self.rate_limit_window}s"
            })
            return self._create_rate_limit_response()
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 检查失败的认证尝试
            if self.enable_ip_blocking and response.status_code == 401:
                self._record_failed_attempt(client_ip)
            elif response.status_code < 400:
                # 成功请求，重置失败计数
                self._reset_failed_attempts(client_ip)
            
            # 添加安全头
            if self.enable_security_headers:
                self._add_security_headers(response)
            
            return response
            
        except Exception as e:
            # 记录异常但不影响异常处理流程
            app_logger.error(f"安全中间件异常: {e}", extra={
                "client_ip": client_ip,
                "path": request.url.path,
                "method": request.method
            })
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
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """检查IP是否被阻止"""
        if ip in self.blocked_ips:
            block_time = self.blocked_ips[ip]
            if time.time() - block_time < self.block_duration:
                return True
            else:
                # 阻止时间已过，移除阻止
                del self.blocked_ips[ip]
                if ip in self.failed_attempts:
                    del self.failed_attempts[ip]
        return False
    
    def _check_rate_limit(self, ip: str) -> bool:
        """检查速率限制"""
        current_time = time.time()
        requests = self.rate_limit_storage[ip]
        
        # 移除过期的请求记录
        while requests and current_time - requests[0] > self.rate_limit_window:
            requests.popleft()
        
        # 检查是否超过限制
        if len(requests) >= self.rate_limit_requests:
            return False
        
        # 记录当前请求
        requests.append(current_time)
        return True
    
    def _record_failed_attempt(self, ip: str):
        """记录失败的认证尝试"""
        self.failed_attempts[ip] += 1
        
        if self.failed_attempts[ip] >= self.max_failed_attempts:
            # 阻止IP
            self.blocked_ips[ip] = time.time()
            app_logger.warning(f"IP被阻止: {ip}", extra={
                "client_ip": ip,
                "failed_attempts": self.failed_attempts[ip],
                "block_duration": self.block_duration
            })
    
    def _reset_failed_attempts(self, ip: str):
        """重置失败尝试计数"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
    
    def _add_security_headers(self, response: Response):
        """添加安全响应头"""
        security_headers = {
            # 防止XSS攻击
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # 强制HTTPS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # 内容安全策略
            "Content-Security-Policy": "default-src 'self'",
            
            # 引用策略
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # 权限策略
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            
            # 服务器信息隐藏
            "Server": "CreditCardAPI/1.0"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def _create_blocked_response(self) -> Response:
        """创建IP被阻止的响应"""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "code": 429,
                "message": "IP地址已被临时阻止",
                "error_code": "IP_BLOCKED",
                "timestamp": time.time()
            }
        )
    
    def _create_rate_limit_response(self) -> Response:
        """创建速率限制响应"""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "code": 429,
                "message": f"请求过于频繁，限制为{self.rate_limit_requests}次/{self.rate_limit_window}秒",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "timestamp": time.time()
            },
            headers={
                "X-RateLimit-Limit": str(self.rate_limit_requests),
                "X-RateLimit-Window": str(self.rate_limit_window),
                "Retry-After": str(self.rate_limit_window)
            }
        ) 