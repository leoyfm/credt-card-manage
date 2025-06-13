"""
管理员模块
"""
from fastapi import APIRouter

from .users import router as users_router
from .cards import router as cards_router

# 创建管理员主路由
admin_router = APIRouter(prefix="/admin", tags=["管理员"])

# 注册子路由
admin_router.include_router(users_router)
admin_router.include_router(cards_router) 