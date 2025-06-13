"""
FastAPI应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.public import auth as auth_router
from app.api.v1.public import system as system_router
from app.api.v1.user import user_router
from app.api.v1.admin import users as admin_users_router
from app.core.logging import app_logger
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    app_logger.info("FastAPI 应用启动完成")
    yield
    app_logger.info("FastAPI 应用已关闭")

app = FastAPI(
    title="信用卡管理系统API",
    description="企业级个人信用卡管理系统后端API，支持注册、登录、令牌、权限等功能。",
    version="1.0.0",
    contact={"name": "leo", "email": "leoyfm@gmail.com"},
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册API路由
app.include_router(auth_router.router, prefix="/api/v1/public")  # Level 1 - 公开接口  
app.include_router(system_router.router, prefix="/api/v1/public")  # Level 1 - 系统信息
app.include_router(user_router, prefix="/api/v1")  # Level 2 - 用户接口
app.include_router(admin_users_router.router, prefix="/api/v1/admin")  # Level 3 - 管理员接口

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser(description="启动信用卡管理系统API服务")
    parser.add_argument('--host', type=str, default="127.0.0.1", help="监听主机")
    parser.add_argument('--port', type=int, default=8000, help="监听端口")
    parser.add_argument('--reload', action='store_true', help="自动重载")
    args = parser.parse_args()
    app_logger.info(f"通过main.py启动服务 host={args.host} port={args.port} reload={args.reload}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload) 