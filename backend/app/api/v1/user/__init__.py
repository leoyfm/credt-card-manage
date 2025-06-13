"""
用户功能模块路由注册
"""
from fastapi import APIRouter
from .profile import router as profile_router
from .cards import router as cards_router

# 创建用户功能区路由
user_router = APIRouter(prefix="/user", tags=["v1-用户功能"])

# 注册子路由
user_router.include_router(profile_router)
user_router.include_router(cards_router)

__all__ = ["user_router"] 