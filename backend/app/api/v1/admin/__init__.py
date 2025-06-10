"""管理员接口路由"""

from fastapi import APIRouter
from .dashboard import router as dashboard_router

admin_router = APIRouter()

admin_router.include_router(dashboard_router, prefix="/dashboard", tags=["管理面板"]) 