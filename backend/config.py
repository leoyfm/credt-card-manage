"""
应用配置管理

统一管理应用的配置项，包括数据库、JWT、微信、邮件等配置。
支持从环境变量读取配置，提供默认值。
"""

import os
from typing import Optional
from functools import lru_cache


class Settings:
    """
    应用设置类
    
    集中管理所有配置项，支持从环境变量读取。
    """
    
    # ==================== 应用基础配置 ====================
    APP_NAME: str = "信用卡管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ==================== 数据库配置 ====================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/credit_card_manage"
    )
    SQL_DEBUG: bool = os.getenv("SQL_DEBUG", "false").lower() == "true"
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # ==================== JWT配置 ====================
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "your-super-secret-jwt-key-change-in-production-2024"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24小时
    JWT_REFRESH_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "30"))  # 30天
    
    # ==================== 密码配置 ====================
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_HASH_ROUNDS: int = int(os.getenv("PASSWORD_HASH_ROUNDS", "12"))
    
    # ==================== 验证码配置 ====================
    VERIFICATION_CODE_LENGTH: int = int(os.getenv("VERIFICATION_CODE_LENGTH", "6"))
    VERIFICATION_CODE_EXPIRE_MINUTES: int = int(os.getenv("VERIFICATION_CODE_EXPIRE_MINUTES", "5"))
    VERIFICATION_CODE_RESEND_INTERVAL: int = int(os.getenv("VERIFICATION_CODE_RESEND_INTERVAL", "60"))  # 秒
    
    # ==================== 微信登录配置 ====================
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET: str = os.getenv("WECHAT_APP_SECRET", "")
    WECHAT_API_BASE_URL: str = "https://api.weixin.qq.com"
    
    # ==================== 短信配置 ====================
    SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "aliyun")  # aliyun, tencent, test
    SMS_ACCESS_KEY: str = os.getenv("SMS_ACCESS_KEY", "")
    SMS_SECRET_KEY: str = os.getenv("SMS_SECRET_KEY", "")
    SMS_SIGN_NAME: str = os.getenv("SMS_SIGN_NAME", "信用卡管家")
    SMS_TEMPLATE_CODE: str = os.getenv("SMS_TEMPLATE_CODE", "SMS_123456789")
    
    # ==================== 邮件配置 ====================
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.qq.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "信用卡管家")
    
    # ==================== Redis配置 ====================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_EXPIRE_SECONDS: int = int(os.getenv("REDIS_EXPIRE_SECONDS", "3600"))
    
    # ==================== 文件上传配置 ====================
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf")
    
    # ==================== 安全配置 ====================
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1小时
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # ==================== 业务配置 ====================
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # 年费相关
    ANNUAL_FEE_REMIND_DAYS: int = int(os.getenv("ANNUAL_FEE_REMIND_DAYS", "30"))
    
    # 还款提醒
    PAYMENT_REMIND_DAYS: int = int(os.getenv("PAYMENT_REMIND_DAYS", "3"))
    
    @property
    def cors_origins_list(self) -> list:
        """获取CORS允许的源列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> list:
        """获取允许的文件扩展名列表"""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.DEBUG
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return not self.DEBUG


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用设置实例
    
    使用LRU缓存确保单例模式，避免重复创建设置对象。
    
    Returns:
        Settings: 应用设置实例
    """
    return Settings()


# 导出设置实例
settings = get_settings()


# ==================== 配置验证 ====================

def validate_config():
    """
    验证配置的有效性
    
    检查关键配置项是否正确设置，提供配置问题的早期发现。
    """
    errors = []
    
    # 检查数据库URL
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL 未配置")
    
    # 检查JWT密钥
    if settings.JWT_SECRET_KEY == "your-super-secret-jwt-key-change-in-production-2024" and settings.is_production():
        errors.append("生产环境必须设置安全的 JWT_SECRET_KEY")
    
    # 检查微信配置（如果启用）
    if settings.WECHAT_APP_ID and not settings.WECHAT_APP_SECRET:
        errors.append("WECHAT_APP_ID 已设置但 WECHAT_APP_SECRET 未配置")
    
    # 检查短信配置（如果启用）
    if settings.SMS_PROVIDER != "test" and not settings.SMS_ACCESS_KEY:
        errors.append("SMS_ACCESS_KEY 未配置，但短信服务已启用")
    
    # 检查邮件配置（如果启用）
    if settings.SMTP_USERNAME and not settings.SMTP_PASSWORD:
        errors.append("SMTP_USERNAME 已设置但 SMTP_PASSWORD 未配置")
    
    if errors:
        error_msg = "配置验证失败:\n" + "\n".join(f"- {error}" for error in errors)
        raise ValueError(error_msg)


# ==================== 环境检测 ====================

def get_environment_info() -> dict:
    """
    获取环境信息
    
    返回当前运行环境的基本信息，用于调试和监控。
    
    Returns:
        dict: 环境信息字典
    """
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "database_configured": bool(settings.DATABASE_URL),
        "redis_configured": bool(settings.REDIS_URL),
        "wechat_configured": bool(settings.WECHAT_APP_ID and settings.WECHAT_APP_SECRET),
        "sms_provider": settings.SMS_PROVIDER,
        "smtp_configured": bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD),
        "jwt_expire_minutes": settings.JWT_EXPIRE_MINUTES,
        "cors_origins": settings.cors_origins_list
    } 