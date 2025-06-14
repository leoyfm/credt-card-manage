"""
用户功能模块路由注册
"""
from fastapi import APIRouter
from .profile import router as profile_router
from .cards import router as cards_router
from .reminders import router as reminders_router
from .recommendations import router as recommendations_router

# 创建用户功能区路由
user_router = APIRouter(prefix="/user", tags=["v1-用户功能"])

# 注册子路由
user_router.include_router(profile_router)
user_router.include_router(cards_router)
user_router.include_router(reminders_router)
user_router.include_router(recommendations_router)

__all__ = ["user_router"] 