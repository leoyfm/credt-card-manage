"""
智能推荐模块数据库模型

定义智能推荐规则和记录相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, Integer, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class RecommendationRule(BaseModel):
    """
    推荐规则数据库模型
    
    定义recommendation_rules表结构，存储智能推荐的规则配置。
    """
    __tablename__ = "recommendation_rules"

    rule_name = Column(
        String(100),
        nullable=False,
        comment="规则名称"
    )
    
    rule_type = Column(
        String(30),
        nullable=False,
        comment="规则类型：card_usage, fee_optimization, category_analysis"
    )
    
    conditions = Column(
        JSONB,
        nullable=False,
        comment="规则条件（JSON格式）"
    )
    
    recommendation_title = Column(
        String(200),
        comment="推荐标题模板"
    )
    
    recommendation_content = Column(
        Text,
        comment="推荐内容模板"
    )
    
    action_type = Column(
        String(30),
        comment="行动类型：card_switch, fee_waiver, spending_adjust"
    )
    
    priority = Column(
        Integer,
        default=1,
        comment="优先级（数字越大优先级越高）"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="是否激活"
    )

    # 关联关系
    recommendation_records = relationship("RecommendationRecord", back_populates="rule")

    # 索引
    __table_args__ = (
        Index('idx_recommendation_rules_type', 'rule_type'),
        Index('idx_recommendation_rules_active', 'is_active'),
        Index('idx_recommendation_rules_priority', 'priority'),
    )


class RecommendationRecord(BaseModel):
    """
    推荐记录数据库模型
    
    定义recommendation_records表结构，存储用户推荐历史记录。
    """
    __tablename__ = "recommendation_records"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey('recommendation_rules.id'),
        comment="规则ID"
    )
    
    recommendation_type = Column(
        String(30),
        nullable=False,
        comment="推荐类型"
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment="推荐标题"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="推荐内容"
    )
    
    action_data = Column(
        JSONB,
        comment="行动相关数据（JSON格式）"
    )
    
    user_action = Column(
        String(20),
        comment="用户操作：viewed, accepted, rejected, ignored"
    )
    
    feedback = Column(
        Text,
        comment="用户反馈"
    )
    
    status = Column(
        String(20),
        default='pending',
        comment="状态：pending, sent, read, acted"
    )

    # 关联关系
    user = relationship("User", back_populates="recommendation_records")
    rule = relationship("RecommendationRule", back_populates="recommendation_records")

    # 索引
    __table_args__ = (
        Index('idx_recommendation_records_user_id', 'user_id'),
        Index('idx_recommendation_records_rule_id', 'rule_id'),
        Index('idx_recommendation_records_type', 'recommendation_type'),
        Index('idx_recommendation_records_status', 'status'),
        Index('idx_recommendation_records_action', 'user_action'),
        Index('idx_recommendation_records_user_created', 'user_id', 'created_at'),
    ) 