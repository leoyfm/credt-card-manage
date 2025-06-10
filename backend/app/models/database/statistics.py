"""
统计分析模块数据库模型

定义用户统计数据相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Date, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserStatistics(BaseModel):
    """
    用户统计数据库模型
    
    定义user_statistics表结构，存储用户各维度统计数据。
    """
    __tablename__ = "user_statistics"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    stat_date = Column(
        Date,
        nullable=False,
        comment="统计日期"
    )
    
    stat_type = Column(
        String(20),
        nullable=False,
        comment="统计类型：daily, monthly, yearly"
    )
    
    total_transactions = Column(
        Integer,
        default=0,
        comment="总交易笔数"
    )
    
    total_spending = Column(
        DECIMAL(15, 2),
        default=0,
        comment="总支出"
    )
    
    total_income = Column(
        DECIMAL(15, 2),
        default=0,
        comment="总收入"
    )
    
    avg_transaction = Column(
        DECIMAL(15, 2),
        default=0,
        comment="平均交易额"
    )
    
    active_cards = Column(
        Integer,
        default=0,
        comment="活跃卡片数"
    )
    
    total_credit_limit = Column(
        DECIMAL(15, 2),
        default=0,
        comment="总信用额度"
    )
    
    total_used_limit = Column(
        DECIMAL(15, 2),
        default=0,
        comment="总已用额度"
    )
    
    credit_utilization = Column(
        DECIMAL(5, 2),
        default=0,
        comment="信用利用率"
    )
    
    category_spending = Column(
        JSONB,
        default='{}',
        comment="分类支出统计"
    )
    
    total_points_earned = Column(
        Integer,
        default=0,
        comment="总获得积分"
    )
    
    total_cashback_earned = Column(
        DECIMAL(10, 2),
        default=0,
        comment="总获得返现"
    )

    # 关联关系
    user = relationship("User", back_populates="user_statistics")

    # 索引
    __table_args__ = (
        Index('idx_user_statistics_user_id', 'user_id'),
        Index('idx_user_statistics_date', 'stat_date'),
        Index('idx_user_statistics_type', 'stat_type'),
        Index('idx_user_statistics_user_date', 'user_id', 'stat_date'),
        Index('idx_user_statistics_user_type', 'user_id', 'stat_type'),
        # 唯一约束：每个用户每个日期每种类型只能有一条记录
        Index('idx_user_statistics_unique', 'user_id', 'stat_date', 'stat_type', unique=True),
    ) 