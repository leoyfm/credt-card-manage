"""
年费管理数据库模型
"""
from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, Date, Text, ForeignKey, TIMESTAMP
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
    rule_group_id = Column(UUID(as_uuid=True), comment="规则组ID(同组规则用AND连接)")
    
    # 规则基本信息
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    condition_type = Column(String(20), nullable=False, comment="条件类型: spending_amount, transaction_count, points_redeem, specific_category")
    condition_value = Column(DECIMAL(15, 2), comment="条件数值")
    condition_count = Column(Integer, comment="条件次数")
    condition_period = Column(String(20), default="yearly", comment="统计周期: monthly, quarterly, yearly")
    
    # 逻辑控制
    logical_operator = Column(String(10), comment="逻辑操作符: AND, OR, NULL")
    priority = Column(Integer, default=1, comment="优先级")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    
    # 有效期
    effective_from = Column(Date, comment="生效日期")
    effective_to = Column(Date, comment="失效日期")
    
    # 描述
    description = Column(Text, comment="规则说明")
    
    # 时间戳
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    card = relationship("CreditCard", back_populates="fee_waiver_rules")
    annual_fee_records = relationship("AnnualFeeRecord", back_populates="waiver_rule")

    def __repr__(self):
        return f"<FeeWaiverRule(id={self.id}, name={self.rule_name}, type={self.condition_type})>"


class AnnualFeeRecord(Base):
    """年费记录表"""
    __tablename__ = "annual_fee_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="记录ID")
    card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, comment="信用卡ID")
    waiver_rule_id = Column(UUID(as_uuid=True), ForeignKey("fee_waiver_rules.id"), comment="减免规则ID")
    
    # 年费信息
    fee_year = Column(Integer, nullable=False, comment="年费年份")
    base_fee = Column(DECIMAL(10, 2), nullable=False, comment="基础年费")
    actual_fee = Column(DECIMAL(10, 2), nullable=False, comment="实际年费")
    waiver_amount = Column(DECIMAL(10, 2), default=0, comment="减免金额")
    
    # 减免信息
    waiver_rules_applied = Column(JSONB, default=list, comment="应用的减免规则")
    rule_evaluation_result = Column(JSONB, comment="规则评估结果")
    waiver_reason = Column(String(100), comment="减免原因")
    calculation_details = Column(JSONB, comment="计算详情")
    
    # 状态和支付
    status = Column(String(20), default="pending", comment="状态: pending, paid, waived, overdue")
    due_date = Column(Date, comment="应缴日期")
    paid_date = Column(Date, comment="实际缴费日期")
    payment_method = Column(String(20), comment="支付方式: auto_deduct, manual, points, waived")
    
    # 备注
    notes = Column(Text, comment="备注")
    
    # 时间戳
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    card = relationship("CreditCard", back_populates="annual_fee_records")
    waiver_rule = relationship("FeeWaiverRule", back_populates="annual_fee_records")

    def __repr__(self):
        return f"<AnnualFeeRecord(id={self.id}, year={self.fee_year}, status={self.status})>" 