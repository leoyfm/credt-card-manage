# 中间件系统配置文档

**版本**: v1.0  
**作者**: LEO  
**邮箱**: leoyfm@gmail.com  

## 概述

信用卡管理系统采用了完整的企业级中间件栈，提供请求日志、性能监控、异常处理和安全防护等功能。

## 中间件架构

### 执行顺序
中间件按照以下顺序执行（洋葱模型）：

```
请求 → 安全中间件 → CORS → 性能监控 → 请求日志 → 异常处理 → 业务逻辑
响应 ← 安全中间件 ← CORS ← 性能监控 ← 请求日志 ← 异常处理 ← 业务逻辑
```

### 中间件列表

1. **SecurityMiddleware** - 安全防护（最外层）
2. **CORSMiddleware** - 跨域处理
3. **PerformanceMiddleware** - 性能监控
4. **RequestLoggingMiddleware** - 请求日志
5. **ExceptionHandlerMiddleware** - 异常处理（最内层）

## 详细配置

### 1. 安全中间件 (SecurityMiddleware)

**功能**：
- 安全响应头设置
- 请求速率限制
- IP地址阻止
- 失败尝试监控

**配置参数**：
```python
app.add_middleware(
    SecurityMiddleware,
    enable_security_headers=True,      # 启用安全头
    enable_rate_limiting=True,         # 启用速率限制
    rate_limit_requests=100,           # 每分钟最大请求数
    rate_limit_window=60,              # 时间窗口（秒）
    enable_ip_blocking=True,           # 启用IP阻止
    max_failed_attempts=5,             # 最大失败尝试次数
    block_duration=300                 # 阻止时长（秒）
)
```

**安全头列表**：
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 2. 性能监控中间件 (PerformanceMiddleware)

**功能**：
- 响应时间监控
- CPU使用率监控
- 内存使用率监控
- 系统资源监控
- 慢请求检测

**配置参数**：
```python
app.add_middleware(
    PerformanceMiddleware,
    slow_request_threshold=2.0,        # 慢请求阈值（秒）
    enable_system_metrics=True,        # 启用系统指标
    log_all_requests=False             # 记录所有请求（建议关闭）
)
```

**监控指标**：
- 墙钟时间 (wall_time)
- CPU时间 (cpu_time)
- 效率比例 (efficiency)
- CPU使用率 (cpu_usage)
- 内存使用率 (memory_usage)
- 磁盘IO (disk_read_bytes, disk_write_bytes)
- 网络IO (network_sent_bytes, network_recv_bytes)

### 3. 请求日志中间件 (RequestLoggingMiddleware)

**功能**：
- 请求信息记录
- 响应信息记录
- 客户端信息记录
- 请求体记录（可选）
- 请求ID生成

**配置参数**：
```python
app.add_middleware(
    RequestLoggingMiddleware,
    log_body=False,                    # 记录请求体（生产环境建议关闭）
    max_body_size=1024                 # 最大请求体大小
)
```

**记录信息**：
- 请求ID (request_id)
- HTTP方法 (method)
- 请求URL (url)
- 查询参数 (query_params)
- 客户端IP (client_ip)
- 用户代理 (user_agent)
- 请求头 (headers)
- 响应状态码 (status_code)
- 处理时间 (process_time)

### 4. 异常处理中间件 (ExceptionHandlerMiddleware)

**功能**：
- 全局异常捕获
- 标准化错误响应
- 异常日志记录
- 调试信息控制

**配置参数**：
```python
app.add_middleware(
    ExceptionHandlerMiddleware,
    debug=settings.DEBUG               # 调试模式
)
```

**处理的异常类型**：
- APIException（自定义异常）
- ValueError（验证异常）
- PermissionError（权限异常）
- 其他未知异常

**响应格式**：
```json
{
    "success": false,
    "code": 500,
    "message": "错误描述",
    "error_code": "ERROR_CODE",
    "timestamp": "2024-12-18T10:30:00Z",
    "error_detail": "详细错误信息（仅调试模式）",
    "request_id": "uuid（仅调试模式）"
}
```

## 响应头说明

### 性能相关头
- `X-Process-Time`: 请求处理时间（秒）
- `X-Response-Time`: 响应时间（秒）
- `X-CPU-Time`: CPU处理时间（秒）
- `X-Request-ID`: 请求唯一标识符

### 速率限制头
- `X-RateLimit-Limit`: 速率限制数量
- `X-RateLimit-Window`: 时间窗口
- `Retry-After`: 重试等待时间

## 日志格式

### 请求日志
```json
{
    "timestamp": "2024-12-18T10:30:00Z",
    "level": "INFO",
    "message": "请求开始",
    "request_id": "uuid",
    "method": "GET",
    "url": "http://localhost:8000/api/v1/user/profile",
    "path": "/api/v1/user/profile",
    "query_params": {},
    "client_ip": "127.0.0.1",
    "user_agent": "Mozilla/5.0..."
}
```

### 性能日志
```json
{
    "timestamp": "2024-12-18T10:30:00Z",
    "level": "WARNING",
    "message": "慢请求检测",
    "request_id": "uuid",
    "method": "GET",
    "path": "/api/v1/user/statistics/overview",
    "status_code": 200,
    "wall_time": 3.2456,
    "cpu_time": 0.1234,
    "efficiency": 3.81,
    "cpu_usage": 45.2,
    "memory_usage": 67.8
}
```

### 异常日志
```json
{
    "timestamp": "2024-12-18T10:30:00Z",
    "level": "ERROR",
    "message": "未捕获异常",
    "request_id": "uuid",
    "method": "POST",
    "url": "http://localhost:8000/api/v1/user/cards/create",
    "path": "/api/v1/user/cards/create",
    "client_ip": "127.0.0.1",
    "exception_type": "ValidationError",
    "exception_message": "卡号格式不正确",
    "traceback": "..."
}
```

## 性能优化建议

### 生产环境配置
```python
# 安全中间件
SecurityMiddleware(
    enable_security_headers=True,
    enable_rate_limiting=True,
    rate_limit_requests=200,           # 根据实际需求调整
    rate_limit_window=60,
    enable_ip_blocking=True,
    max_failed_attempts=3,             # 更严格的限制
    block_duration=600                 # 更长的阻止时间
)

# 性能监控中间件
PerformanceMiddleware(
    slow_request_threshold=1.0,        # 更严格的慢请求阈值
    enable_system_metrics=False,       # 关闭系统指标以提高性能
    log_all_requests=False
)

# 请求日志中间件
RequestLoggingMiddleware(
    log_body=False,                    # 关闭请求体记录
    max_body_size=512                  # 减小最大记录大小
)

# 异常处理中间件
ExceptionHandlerMiddleware(
    debug=False                        # 关闭调试模式
)
```

### 开发环境配置
```python
# 开发环境可以启用更多调试功能
SecurityMiddleware(
    enable_rate_limiting=False,        # 开发时可关闭速率限制
    enable_ip_blocking=False
)

PerformanceMiddleware(
    slow_request_threshold=5.0,        # 更宽松的阈值
    enable_system_metrics=True,
    log_all_requests=True              # 记录所有请求
)

RequestLoggingMiddleware(
    log_body=True,                     # 开发时可记录请求体
    max_body_size=2048
)

ExceptionHandlerMiddleware(
    debug=True                         # 启用调试模式
)
```

## 监控和告警

### 关键指标监控
1. **响应时间**: 监控平均响应时间和95%分位数
2. **错误率**: 监控4xx和5xx错误的比例
3. **速率限制**: 监控触发速率限制的频率
4. **系统资源**: 监控CPU和内存使用率

### 告警规则
- 平均响应时间 > 2秒
- 错误率 > 5%
- CPU使用率 > 80%
- 内存使用率 > 85%
- 速率限制触发频率 > 10次/分钟

## 故障排查

### 常见问题

1. **请求被阻止**
   - 检查IP是否在阻止列表中
   - 检查速率限制配置
   - 查看安全日志

2. **响应时间过长**
   - 查看性能日志中的慢请求
   - 检查系统资源使用情况
   - 分析数据库查询性能

3. **异常处理不当**
   - 检查异常日志
   - 确认自定义异常类型
   - 验证错误响应格式

### 调试命令
```bash
# 查看最近的请求日志
tail -f logs/app.log | grep "请求开始\|请求完成"

# 查看性能警告
tail -f logs/app.log | grep "慢请求\|性能警告"

# 查看异常日志
tail -f logs/app.log | grep "ERROR"

# 查看安全事件
tail -f logs/app.log | grep "速率限制\|IP被阻止"
```

---

**联系**: LEO (leoyfm@gmail.com)  
**版本**: v1.0 