"""API v1版本路由"""

from fastapi import APIRouter

v1_router = APIRouter()

# 导入各级别路由
from .public import public_router
from .user import user_router
from .admin import admin_router

# 挂载路由
v1_router.include_router(public_router, prefix="/public", tags=["公开接口"])
v1_router.include_router(user_router, prefix="/user", tags=["用户接口"])
v1_router.include_router(admin_router, prefix="/admin", tags=["管理员接口"]) 