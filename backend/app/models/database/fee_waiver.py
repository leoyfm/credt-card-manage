"""
年费管理模块数据库模型

包含年费减免规则和年费记录的数据库模型定义
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class FeeWaiverRule(Base):
    """年费减免规则表"""
    __tablename__ = "fee_waiver_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="规则ID")
    card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, comment="信用卡ID")
    rule_group_id = Column(UUID(as_uuid=True), nullable=True, comment="规则组ID(同组规则用AND连接)")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    
    # 减免条件
    condition_type = Column(String(20), nullable=False, comment="条件类型: spending_amount, transaction_count, points_redeem, specific_category")
    condition_value = Column(Numeric(15, 2), nullable=True, comment="条件数值")
    condition_count = Column(Integer, nullable=True, comment="条件次数")
    condition_period = Column(String(20), nullable=True, comment="统计周期: monthly, quarterly, yearly")
    logical_operator = Column(String(10), nullable=True, comment="逻辑操作符: AND, OR, NULL")
    
    # 规则配置
    priority = Column(Integer, nullable=True, comment="优先级")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    effective_from = Column(Date, nullable=True, comment="生效日期")
    effective_to = Column(Date, nullable=True, comment="失效日期")
    description = Column(Text, nullable=True, comment="规则说明")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    card = relationship("CreditCard", back_populates="fee_waiver_rules")
    fee_records = relationship("AnnualFeeRecord", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FeeWaiverRule(id={self.id}, rule_name={self.rule_name}, condition_type={self.condition_type})>"


class AnnualFeeRecord(Base):
    """年费记录表"""
    __tablename__ = "annual_fee_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="记录ID")
    waiver_rule_id = Column(UUID(as_uuid=True), ForeignKey("fee_waiver_rules.id", ondelete="CASCADE"), nullable=True, comment="年费规则ID")
    card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, comment="信用卡ID")
    
    # 年费信息
    fee_year = Column(Integer, nullable=False, comment="年费年份")
    base_fee = Column(Numeric(10, 2), nullable=False, comment="基础年费")
    actual_fee = Column(Numeric(10, 2), nullable=False, comment="实际年费")
    waiver_amount = Column(Numeric(10, 2), default=0, comment="减免金额")
    waiver_rules_applied = Column(JSONB, default=list, comment="应用的减免规则")
    rule_evaluation_result = Column(JSONB, comment="规则评估结果")
    waiver_reason = Column(String(200), comment="减免原因")
    calculation_details = Column(JSONB, comment="计算详情")
    
    # 状态信息
    status = Column(String(20), default="pending", comment="状态: pending, paid, waived, overdue")
    due_date = Column(Date, comment="应缴日期")
    paid_date = Column(Date, comment="实际缴费日期")
    payment_method = Column(String(20), comment="支付方式")
    notes = Column(Text, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    rule = relationship("FeeWaiverRule", back_populates="fee_records")
    card = relationship("CreditCard", back_populates="annual_fee_records")

    def __repr__(self):
        return f"<AnnualFeeRecord(id={self.id}, waiver_rule_id={self.waiver_rule_id}, fee_year={self.fee_year})>" 