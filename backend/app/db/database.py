"""
数据库连接和会话管理

配置SQLAlchemy数据库连接，提供会话管理和数据库操作工具。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG,  # 调试模式下显示SQL
    # 连接池配置
    pool_size=10,
    max_overflow=20,
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 数据库依赖
def get_db():
    """
    获取数据库会话
    
    用于FastAPI依赖注入，自动管理数据库会话生命周期。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    获取数据库会话（同步版本）
    
    用于非FastAPI环境下的数据库操作。
    """
    return SessionLocal()


def init_db():
    """
    初始化数据库表
    
    创建所有定义的数据库表结构。
    注意：实际项目中应使用Alembic进行数据库迁移。
    """
    from app.models.database import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    删除所有数据库表
    
    仅用于测试或重新初始化，生产环境慎用。
    """
    from app.models.database import Base
    Base.metadata.drop_all(bind=engine) 