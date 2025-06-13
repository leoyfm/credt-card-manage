"""
性能监控中间件
"""
import time
import psutil
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import app_logger


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(
        self, 
        app,
        slow_request_threshold: float = 2.0,
        enable_system_metrics: bool = True,
        log_all_requests: bool = False
    ):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.enable_system_metrics = enable_system_metrics
        self.log_all_requests = log_all_requests
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录开始时间和系统状态
        start_time = time.time()
        start_cpu_time = time.process_time()
        
        # 获取系统指标（如果启用）
        system_metrics_before = self._get_system_metrics() if self.enable_system_metrics else {}
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算性能指标
            end_time = time.time()
            end_cpu_time = time.process_time()
            
            wall_time = end_time - start_time
            cpu_time = end_cpu_time - start_cpu_time
            
            # 获取结束时的系统指标
            system_metrics_after = self._get_system_metrics() if self.enable_system_metrics else {}
            
            # 构建性能数据
            performance_data = {
                "request_id": getattr(request.state, "request_id", "unknown"),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "wall_time": round(wall_time, 4),
                "cpu_time": round(cpu_time, 4),
                "efficiency": round(cpu_time / wall_time * 100, 2) if wall_time > 0 else 0
            }
            
            # 添加系统指标差异
            if self.enable_system_metrics and system_metrics_before and system_metrics_after:
                performance_data.update(self._calculate_metrics_diff(
                    system_metrics_before, 
                    system_metrics_after
                ))
            
            # 添加性能头到响应
            response.headers["X-Response-Time"] = str(wall_time)
            response.headers["X-CPU-Time"] = str(cpu_time)
            
            # 记录性能日志
            if wall_time > self.slow_request_threshold:
                app_logger.warning(f"慢请求检测", extra=performance_data)
            elif self.log_all_requests:
                app_logger.info(f"请求性能", extra=performance_data)
            
            # 检查性能警告
            self._check_performance_warnings(performance_data)
            
            return response
            
        except Exception as e:
            # 记录异常请求的性能数据
            end_time = time.time()
            wall_time = end_time - start_time
            
            error_performance_data = {
                "request_id": getattr(request.state, "request_id", "unknown"),
                "method": request.method,
                "path": request.url.path,
                "wall_time": round(wall_time, 4),
                "error": str(e),
                "error_type": type(e).__name__
            }
            
            app_logger.error(f"异常请求性能", extra=error_performance_data)
            raise
    
    def _get_system_metrics(self) -> dict:
        """获取系统性能指标"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used": psutil.virtual_memory().used,
                "disk_io_read": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                "disk_io_write": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
                "network_sent": psutil.net_io_counters().bytes_sent,
                "network_recv": psutil.net_io_counters().bytes_recv
            }
        except Exception as e:
            app_logger.warning(f"获取系统指标失败: {e}")
            return {}
    
    def _calculate_metrics_diff(self, before: dict, after: dict) -> dict:
        """计算系统指标差异"""
        diff = {}
        
        # CPU和内存使用率（取结束时的值）
        if "cpu_percent" in after:
            diff["cpu_usage"] = after["cpu_percent"]
        if "memory_percent" in after:
            diff["memory_usage"] = after["memory_percent"]
        
        # 计算IO和网络增量
        io_network_metrics = [
            ("disk_io_read", "disk_read_bytes"),
            ("disk_io_write", "disk_write_bytes"), 
            ("network_sent", "network_sent_bytes"),
            ("network_recv", "network_recv_bytes")
        ]
        
        for before_key, diff_key in io_network_metrics:
            if before_key in before and before_key in after:
                diff[diff_key] = after[before_key] - before[before_key]
        
        return diff
    
    def _check_performance_warnings(self, performance_data: dict):
        """检查性能警告条件"""
        warnings = []
        
        # 检查响应时间
        wall_time = performance_data.get("wall_time", 0)
        if wall_time > self.slow_request_threshold:
            warnings.append(f"响应时间过长: {wall_time}s")
        
        # 检查CPU使用率
        cpu_usage = performance_data.get("cpu_usage", 0)
        if cpu_usage > 80:
            warnings.append(f"CPU使用率过高: {cpu_usage}%")
        
        # 检查内存使用率
        memory_usage = performance_data.get("memory_usage", 0)
        if memory_usage > 85:
            warnings.append(f"内存使用率过高: {memory_usage}%")
        
        # 检查效率（CPU时间/墙钟时间比例）
        efficiency = performance_data.get("efficiency", 0)
        if efficiency < 10 and wall_time > 1:  # 长时间请求但CPU使用率很低
            warnings.append(f"请求效率低: {efficiency}%，可能存在IO阻塞")
        
        # 记录警告
        if warnings:
            warning_data = {
                **performance_data,
                "warnings": warnings
            }
            app_logger.warning(f"性能警告", extra=warning_data) 