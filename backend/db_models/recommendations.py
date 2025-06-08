"""
智能推荐数据库模型

定义智能推荐相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Numeric, Integer, Boolean, Text, Enum as SQLEnum, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel
from models.recommendations import RecommendationType, RecommendationStatus


class Recommendation(BaseModel):
    """
    智能推荐数据库模型
    
    定义recommendations表结构，存储信用卡推荐信息。
    """
    __tablename__ = "recommendations"

    # 用户关联
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="用户ID，推荐的目标用户"
    )

    # 银行和卡片信息
    bank_name = Column(
        String(50), 
        nullable=False, 
        comment="银行名称"
    )
    
    card_name = Column(
        String(100), 
        nullable=False, 
        comment="信用卡名称"
    )

    # 推荐信息
    recommendation_type = Column(
        SQLEnum(RecommendationType), 
        nullable=False, 
        comment="推荐类型：cashback/points/travel/dining/shopping/fuel"
    )
    
    title = Column(
        String(100), 
        nullable=False, 
        comment="推荐标题"
    )
    
    description = Column(
        Text, 
        nullable=False, 
        comment="推荐描述"
    )

    # 卡片特性
    features = Column(
        JSON,
        comment="卡片特色功能列表，JSON格式存储"
    )
    
    annual_fee = Column(
        Numeric(8, 2), 
        default=0, 
        comment="年费金额"
    )
    
    credit_limit_range = Column(
        String(50), 
        nullable=False, 
        comment="额度范围"
    )

    # 推荐评分
    approval_difficulty = Column(
        Integer, 
        nullable=False, 
        comment="申请难度等级，1-5分"
    )
    
    recommendation_score = Column(
        Numeric(5, 2), 
        nullable=False, 
        comment="推荐分数，0-100分"
    )

    # 推荐理由
    match_reasons = Column(
        JSON,
        comment="匹配原因列表，JSON格式存储"
    )
    
    pros = Column(
        JSON,
        comment="优点列表，JSON格式存储"
    )
    
    cons = Column(
        JSON,
        comment="缺点列表，JSON格式存储"
    )

    # 申请信息
    apply_url = Column(
        String(500),
        comment="申请链接"
    )

    # 状态信息
    status = Column(
        SQLEnum(RecommendationStatus), 
        default=RecommendationStatus.ACTIVE,
        comment="推荐状态：active/expired/applied/rejected"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        comment="推荐过期时间"
    )
    
    is_featured = Column(
        Boolean, 
        default=False, 
        comment="是否为精选推荐"
    )

    # 用户交互统计
    view_count = Column(
        Integer, 
        default=0, 
        comment="查看次数"
    )
    
    last_viewed_at = Column(
        DateTime(timezone=True),
        comment="最后查看时间"
    )

    # 索引定义
    __table_args__ = (
        Index("idx_recommendations_user_id", "user_id"),
        Index("idx_recommendations_type", "recommendation_type"),
        Index("idx_recommendations_status", "status"),
        Index("idx_recommendations_score", "recommendation_score"),
        Index("idx_recommendations_bank", "bank_name"),
        Index("idx_recommendations_featured", "is_featured"),
        Index("idx_recommendations_user_status", "user_id", "status"),
        Index("idx_recommendations_expires", "expires_at"),
    )

    def __repr__(self):
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, card_name='{self.card_name}', score={self.recommendation_score})>" 