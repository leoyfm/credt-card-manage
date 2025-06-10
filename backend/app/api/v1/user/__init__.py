"""用户接口路由"""

from fastapi import APIRouter
from .profile import router as profile_router
from .cards import router as cards_router
from .transactions import router as transactions_router
from .annual_fees import router as annual_fees_router
from .statistics import router as statistics_router
from .reminders import router as reminders_router
from .recommendations import router as recommendations_router

user_router = APIRouter()

user_router.include_router(profile_router, prefix="/profile", tags=["个人资料"])
user_router.include_router(cards_router, tags=["信用卡管理"])
user_router.include_router(transactions_router, tags=["交易管理"])
user_router.include_router(annual_fees_router, tags=["年费管理"])
user_router.include_router(statistics_router, tags=["统计分析"])
user_router.include_router(reminders_router, tags=["还款提醒"])
user_router.include_router(recommendations_router, tags=["智能推荐"]) 