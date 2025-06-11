"""
数据库连接模块
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 主数据库引擎
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# 测试数据库引擎
TestEngine = create_engine(settings.TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TestEngine, future=True)

Base = declarative_base() 