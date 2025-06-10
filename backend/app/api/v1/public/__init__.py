"""公开接口路由"""

from fastapi import APIRouter
from .auth import router as auth_router

public_router = APIRouter()

public_router.include_router(auth_router, tags=["认证管理"]) 