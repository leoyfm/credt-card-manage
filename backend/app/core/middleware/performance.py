"""性能监控中间件"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from ..logging.logger import get_logger

logger = get_logger("performance")

class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录性能数据
        if process_time > self.slow_request_threshold:
            logger.warning(
                "慢请求检测",
                method=request.method,
                url=str(request.url),
                process_time=process_time,
                threshold=self.slow_request_threshold,
                request_id=getattr(request.state, 'request_id', None)
            )
        
        # 记录性能指标
        logger.debug(
            "性能指标",
            method=request.method,
            url=str(request.url),
            process_time=process_time,
            status_code=response.status_code,
            request_id=getattr(request.state, 'request_id', None)
        )
        
        return response 