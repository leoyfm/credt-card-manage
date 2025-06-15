"""
推荐模块数据库模型

包含推荐规则和推荐记录的数据库模型定义
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class RecommendationRule(Base):
    """推荐规则表"""
    __tablename__ = "recommendation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="规则ID")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    rule_type = Column(String(30), nullable=False, comment="规则类型")
    conditions = Column(JSON, nullable=False, comment="规则条件")
    recommendation_title = Column(String(200), comment="推荐标题")
    recommendation_content = Column(Text, comment="推荐内容")
    action_type = Column(String(30), comment="行动类型")
    priority = Column(Integer, default=1, comment="优先级")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联推荐记录
    records = relationship("RecommendationRecord", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RecommendationRule(id={self.id}, name={self.rule_name}, type={self.rule_type})>"


class RecommendationRecord(Base):
    """推荐记录表"""
    __tablename__ = "recommendation_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="记录ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    rule_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_rules.id"), comment="规则ID")
    recommendation_type = Column(String(30), nullable=False, comment="推荐类型")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    action_data = Column(JSON, comment="行动数据")
    user_action = Column(String(20), comment="用户行动")
    feedback = Column(Text, comment="用户反馈")
    status = Column(String(20), default="pending", comment="状态")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联用户
    user = relationship("User", back_populates="recommendation_records")
    # 关联推荐规则
    rule = relationship("RecommendationRule", back_populates="records")

    def __repr__(self):
        return f"<RecommendationRecord(id={self.id}, user_id={self.user_id}, type={self.recommendation_type})>" 