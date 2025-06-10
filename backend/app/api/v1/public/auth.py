"""认证相关接口"""

from fastapi import APIRouter
from app.core.logging.logger import get_logger

router = APIRouter()
logger = get_logger("auth")

@router.get("/health")
async def health_check():
    """健康检查接口"""
    logger.info("健康检查请求")
    return {
        "success": True,
        "code": 200,
        "message": "系统运行正常",
        "data": {
            "status": "healthy",
            "version": "2.0.0"
        }
    } 