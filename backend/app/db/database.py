"""
数据库连接模块
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings
from typing import Generator

# 主数据库引擎
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# 测试数据库引擎
TestEngine = create_engine(settings.TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TestEngine, future=True)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """创建所有表（用于测试）"""
    Base.metadata.create_all(bind=TestEngine)


def drop_all_tables():
    """删除所有表（用于测试清理）"""
    Base.metadata.drop_all(bind=TestEngine) 