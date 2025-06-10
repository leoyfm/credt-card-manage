"""
数据库基础模型

定义所有数据库模型的基类，包含通用字段和方法。
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class BaseModel(Base):
    """
    数据库模型基类
    
    所有数据库模型都应该继承此类，提供通用的ID和时间戳字段。
    """
    __abstract__ = True

    # 主键ID，使用UUID4
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="主键ID"
    )
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )

    def to_dict(self):
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>" 