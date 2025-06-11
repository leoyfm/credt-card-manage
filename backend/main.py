"""
FastAPI应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.public import auth as auth_router
from app.core.logging import app_logger

app = FastAPI(
    title="信用卡管理系统API",
    description="企业级个人信用卡管理系统后端API，支持注册、登录、令牌、权限等功能。",
    version="1.0.0",
    contact={"name": "leo", "email": "leoyfm@gmail.com"}
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册认证API路由
app.include_router(auth_router.router, prefix="/api/v1/public")

@app.on_event("startup")
def on_startup():
    app_logger.info("FastAPI 应用启动完成")

@app.on_event("shutdown")
def on_shutdown():
    app_logger.info("FastAPI 应用已关闭") 