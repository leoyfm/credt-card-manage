"""用户资料接口"""

from fastapi import APIRouter
from app.core.logging.logger import get_logger

router = APIRouter()
logger = get_logger("user.profile")

@router.get("/")
async def get_profile():
    """获取用户资料"""
    logger.info("获取用户资料请求")
    return {
        "success": True,
        "code": 200,
        "message": "获取成功",
        "data": {
            "user_id": "test-user-id",
            "username": "test_user"
        }
    } 