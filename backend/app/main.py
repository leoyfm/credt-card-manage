"""FastAPI主应用"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

# 导入核心组件
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    BaseAPIException,
    base_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.core.middleware import RequestLoggingMiddleware, PerformanceMiddleware

# 导入API路由
from app.api import api_router

# 初始化日志
setup_logging()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="信用卡管理系统后端API v2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PerformanceMiddleware, slow_request_threshold=1.0)

# 注册异常处理器
app.add_exception_handler(BaseAPIException, base_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册API路由
app.include_router(api_router)

@app.get("/")
async def root():
    """根路径"""
    return {
        "success": True,
        "code": 200,
        "message": "欢迎使用信用卡管理系统API v2.0",
        "data": {
            "version": settings.VERSION,
            "docs_url": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 