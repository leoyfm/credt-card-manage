from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.logging import app_logger
import traceback

app = FastAPI(...)

# 全局异常日志中间件
@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        # 记录详细异常日志
        app_logger.error(
            f"未捕获异常: {request.method} {request.url} - {exc}\n{traceback.format_exc()}"
        )
        # 返回标准 500 响应
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": 500,
                "message": "服务器内部错误",
                "error_detail": str(exc),
                "timestamp": None
            }
        )
# ... 其余 FastAPI 路由和配置 ... 