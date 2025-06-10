"""公开接口路由"""

from fastapi import APIRouter
from .test import router as test_router
from .auth import router as auth_router

public_router = APIRouter()

public_router.include_router(test_router, tags=["测试接口"])
public_router.include_router(auth_router, prefix="/auth", tags=["认证管理"]) 