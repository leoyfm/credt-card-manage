"""管理员接口路由"""

from fastapi import APIRouter
from .users import router as users_router

admin_router = APIRouter()

admin_router.include_router(users_router, prefix="/users", tags=["管理员用户管理"]) 