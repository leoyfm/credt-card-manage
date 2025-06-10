"""管理面板接口"""

from fastapi import APIRouter
from app.core.logging.logger import get_logger

router = APIRouter()
logger = get_logger("admin.dashboard")

@router.get("/stats")
async def get_dashboard_stats():
    """获取仪表板统计数据"""
    logger.info("获取仪表板统计数据请求")
    return {
        "success": True,
        "code": 200,
        "message": "获取成功",
        "data": {
            "total_users": 100,
            "total_cards": 250
        }
    } 