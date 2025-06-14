"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "postgresql://credit_user:credit_password@localhost:5432/credit_card_db"
    TEST_DATABASE_URL: str = "postgresql://credit_user:credit_password@localhost:5432/test"

    # JWT配置
    JWT_SECRET_KEY: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 邮箱配置（可扩展）
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 465
    MAIL_SERVER: str = ""
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    DEBUG: bool = True

    model_config = ConfigDict(env_file=".env")

settings = Settings() 