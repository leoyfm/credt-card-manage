"""
数据库会话管理工具

提供会话上下文管理器和事务处理工具。
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .database import SessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器
    
    自动处理会话的创建、提交和回滚。
    
    使用示例:
        with db_session() as db:
            user = db.query(User).first()
            # 自动提交或回滚
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"未知错误: {e}")
        raise
    finally:
        session.close()


@contextmanager
def db_transaction(db: Session) -> Generator[Session, None, None]:
    """
    数据库事务上下文管理器
    
    在现有会话中创建事务，支持嵌套事务。
    
    Args:
        db: 现有数据库会话
    
    使用示例:
        with db_transaction(db) as tx_db:
            # 事务操作
            tx_db.add(user)
            # 自动提交或回滚
    """
    savepoint = None
    try:
        # 如果已在事务中，创建保存点
        if db.in_transaction():
            savepoint = db.begin_nested()
        else:
            db.begin()
        
        yield db
        
        if savepoint:
            savepoint.commit()
        else:
            db.commit()
            
    except SQLAlchemyError as e:
        if savepoint:
            savepoint.rollback()
        else:
            db.rollback()
        logger.error(f"数据库事务失败: {e}")
        raise
    except Exception as e:
        if savepoint:
            savepoint.rollback()
        else:
            db.rollback()
        logger.error(f"事务处理异常: {e}")
        raise


class DatabaseManager:
    """
    数据库管理器
    
    提供高级数据库操作方法。
    """
    
    def __init__(self):
        self._session_factory = SessionLocal
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """
        在事务中执行函数
        
        Args:
            func: 要执行的函数，第一个参数必须是数据库会话
            *args: 函数的其他参数
            **kwargs: 函数的关键字参数
        
        Returns:
            函数执行结果
        """
        with db_session() as db:
            return func(db, *args, **kwargs)
    
    def bulk_save(self, objects, batch_size=1000):
        """
        批量保存对象
        
        Args:
            objects: 要保存的对象列表
            batch_size: 批次大小
        """
        with db_session() as db:
            for i in range(0, len(objects), batch_size):
                batch = objects[i:i + batch_size]
                db.bulk_save_objects(batch)
                logger.info(f"批量保存 {len(batch)} 个对象")
    
    def bulk_update(self, model_class, updates, batch_size=1000):
        """
        批量更新对象
        
        Args:
            model_class: 模型类
            updates: 更新数据列表，每个元素包含where条件和values
            batch_size: 批次大小
        """
        with db_session() as db:
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                for update in batch:
                    db.query(model_class).filter(**update['where']).update(update['values'])
                logger.info(f"批量更新 {len(batch)} 个对象")


# 全局数据库管理器实例
db_manager = DatabaseManager() 