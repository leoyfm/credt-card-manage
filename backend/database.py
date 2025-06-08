"""
数据库连接配置

配置SQLAlchemy连接和会话管理，支持PostgreSQL数据库。
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from db_models.base import Base

logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/credit_card_manage"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def create_database():
    """
    创建数据库表
    
    在应用启动时调用，根据ORM模型创建数据库表结构。
    """
    try:
        logger.info("开始创建数据库表...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    FastAPI依赖注入函数，用于获取数据库会话。
    自动处理会话的创建、提交和关闭。
    
    Yields:
        Session: SQLAlchemy数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库操作异常: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    检查数据库连接
    
    用于健康检查，验证数据库连接是否正常。
    
    Returns:
        bool: 连接是否成功
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("数据库连接检查成功")
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False


class DatabaseManager:
    """
    数据库管理器
    
    提供数据库操作的高级接口，包括事务管理、批量操作等。
    """
    
    @staticmethod
    def execute_in_transaction(func, *args, **kwargs):
        """
        在事务中执行函数
        
        自动处理事务的开始、提交和回滚。
        """
        db = SessionLocal()
        try:
            result = func(db, *args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"事务执行失败: {str(e)}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def get_session() -> Session:
        """
        获取新的数据库会话
        
        用于需要手动管理会话生命周期的场景。
        调用者负责关闭会话。
        """
        return SessionLocal()


# 数据库健康检查依赖
def get_db_health() -> dict:
    """
    获取数据库健康状态
    
    Returns:
        dict: 包含数据库状态信息的字典
    """
    try:
        is_connected = check_database_connection()
        return {
            "database": "connected" if is_connected else "disconnected",
            "url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "unknown"
        }
    except Exception as e:
        return {
            "database": "error",
            "error": str(e)
        } 