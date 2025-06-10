"""测试路由"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """测试接口"""
    return {
        "success": True,
        "message": "测试成功",
        "data": {
            "status": "working"
        }
    } 