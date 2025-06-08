"""
SQLAlchemy基础模型

定义所有数据库模型的基类，包含公共字段和配置。
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class BaseModel(Base):
    """
    基础数据库模型
    
    所有数据库表都继承此基类，包含公共字段：
    - id: UUID主键
    - created_at: 创建时间
    - updated_at: 更新时间
    - is_deleted: 软删除标记
    """
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="主键ID"
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    is_deleted = Column(
        Boolean, 
        default=False,
        nullable=False,
        comment="软删除标记"
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>" 