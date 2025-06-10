"""API路由包"""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

# 导入各版本路由
from .v1 import v1_router

api_router.include_router(v1_router, prefix="/v1") 