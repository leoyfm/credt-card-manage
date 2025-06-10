"""用户接口路由"""

from fastapi import APIRouter
from .profile import router as profile_router

user_router = APIRouter()

user_router.include_router(profile_router, prefix="/profile", tags=["个人资料"]) 