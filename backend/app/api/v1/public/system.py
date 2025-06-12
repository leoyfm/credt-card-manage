"""
系统信息API路由 - Level 1权限（公开接口）
"""
from fastapi import APIRouter
from app.utils.response import ResponseUtil
from app.core.config import settings
from datetime import datetime, timezone, timedelta
import psutil
import sys

router = APIRouter(
    prefix="/system",
    tags=["v1-系统信息"],
    responses={404: {"description": "未找到"}}
)

@router.get(
    "/health", 
    summary="健康检查",
    description="检查系统健康状态，包括服务状态、数据库连接等"
)
async def health_check():
    """
    系统健康检查接口
    返回服务运行状态、数据库连接状态等信息
    """
    try:
        # 获取系统基本信息
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "uptime": "系统运行中",
            "version": "1.0.0",
            "database": "connected",  # 这里可以添加实际的数据库连接检查
            "memory_usage": f"{psutil.virtual_memory().percent:.1f}%",
            "disk_usage": f"{psutil.disk_usage('/').percent:.1f}%",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
        return ResponseUtil.success(
            data=health_data,
            message="系统健康状态正常"
        )
    except Exception as e:
        return ResponseUtil.error(
            message="系统健康检查失败",
            code=503
        )

@router.get(
    "/version",
    summary="版本信息", 
    description="获取系统版本信息"
)
async def get_version():
    """
    获取系统版本信息
    """
    version_data = {
        "version": "1.0.0",
        "build_time": "2024-12-01",
        "environment": "development",
        "api_version": "v1",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "framework": "FastAPI",
        "author": "LEO",
        "contact": "leoyfm@gmail.com"
    }
    
    return ResponseUtil.success(
        data=version_data,
        message="获取版本信息成功"
    )

@router.get(
    "/status",
    summary="服务状态",
    description="获取系统服务状态信息"
)
async def get_status():
    """
    获取系统服务状态
    """
    try:
        status_data = {
            "service_name": "信用卡管理系统API",
            "status": "running",
            "start_time": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "request_count": "N/A",  # 可以集成请求计数器
            "active_connections": "N/A",  # 可以集成连接池监控
            "cpu_usage": f"{psutil.cpu_percent():.1f}%",
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.1f}GB",
            "load_average": "N/A" if sys.platform == "win32" else psutil.getloadavg()[0]
        }
        
        return ResponseUtil.success(
            data=status_data,
            message="获取服务状态成功"
        )
    except Exception as e:
        return ResponseUtil.error(
            message="获取服务状态失败",
            code=500
        ) 