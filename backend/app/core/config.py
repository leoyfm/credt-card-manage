"""应用配置管理"""

from pydantic import BaseModel
from typing import Optional, List
import os

class Settings(BaseModel):
    """应用设置"""
    
    # 应用配置
    APP_NAME: str = "信用卡管理系统"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./credit_card.db"
    DATABASE_POOL_SIZE: int = 50
    DATABASE_MAX_OVERFLOW: int = 100
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "logs/app.log"
    
    # Redis配置
    REDIS_URL: Optional[str] = None
    
    # 安全配置
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]

# 全局设置实例
settings = Settings() 