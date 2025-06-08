"""
年费数据库模型

定义年费相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Numeric, Integer, Date, Boolean, ForeignKey, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import date

from .base import BaseModel
from models.annual_fee import FeeType, WaiverStatus


class AnnualFeeRule(BaseModel):
    """
    年费规则数据库模型
    
    定义annual_fee_rules表结构，存储年费规则配置信息。
    """
    __tablename__ = "annual_fee_rules"

    rule_name = Column(
        String(100), 
        nullable=False, 
        comment="规则名称，如：刷卡次数减免-标准"
    )
    
    fee_type = Column(
        SQLEnum(FeeType), 
        nullable=False, 
        comment="年费类型：rigid/transaction_count/transaction_amount/points_exchange"
    )
    
    base_fee = Column(
        Numeric(10, 2), 
        nullable=False, 
        default=0, 
        comment="基础年费金额，单位：元"
    )
    
    waiver_condition_value = Column(
        Numeric(15, 2), 
        comment="减免条件数值，如刷卡次数12或消费金额50000"
    )
    
    waiver_period_months = Column(
        Integer, 
        default=12, 
        comment="考核周期（月），通常为12个月"
    )
    
    description = Column(
        Text, 
        comment="规则描述，详细说明减免条件"
    )

    # 关联关系
    cards = relationship("CreditCard", back_populates="annual_fee_rule")
    records = relationship("AnnualFeeRecord", back_populates="rule")

    # 索引定义
    __table_args__ = (
        Index("idx_annual_fee_rules_fee_type", "fee_type"),
        Index("idx_annual_fee_rules_rule_name", "rule_name"),
    )

    def __repr__(self):
        return f"<AnnualFeeRule(id={self.id}, rule_name='{self.rule_name}', fee_type='{self.fee_type}')>"


class AnnualFeeRecord(BaseModel):
    """
    年费记录数据库模型
    
    定义annual_fee_records表结构，存储年费记录和减免状态。
    """
    __tablename__ = "annual_fee_records"

    card_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("credit_cards.id"), 
        nullable=False, 
        comment="信用卡ID，关联credit_cards表"
    )
    
    fee_year = Column(
        Integer, 
        nullable=False, 
        comment="年费所属年份，如2024"
    )
    
    due_date = Column(
        Date, 
        nullable=False, 
        comment="年费到期日期"
    )
    
    fee_amount = Column(
        Numeric(10, 2), 
        nullable=False, 
        default=0, 
        comment="应付年费金额，单位：元"
    )
    
    waiver_status = Column(
        SQLEnum(WaiverStatus), 
        default=WaiverStatus.PENDING, 
        comment="减免状态：pending/waived/paid/overdue"
    )
    
    waiver_condition_met = Column(
        Boolean, 
        default=False, 
        comment="是否满足减免条件"
    )
    
    current_progress = Column(
        Numeric(15, 2), 
        default=0, 
        comment="当前进度，如已刷卡次数或金额"
    )
    
    payment_date = Column(
        Date, 
        comment="实际支付日期"
    )
    
    notes = Column(
        Text, 
        comment="备注信息"
    )

    # 关联关系
    card = relationship("CreditCard", back_populates="annual_fee_records")

    # 索引定义
    __table_args__ = (
        Index("idx_annual_fee_records_card_year", "card_id", "fee_year"),
        Index("idx_annual_fee_records_due_date", "due_date"),
        Index("idx_annual_fee_records_status", "waiver_status"),
        Index("idx_annual_fee_records_year", "fee_year"),
    )

    def __repr__(self):
        return f"<AnnualFeeRecord(id={self.id}, card_id={self.card_id}, fee_year={self.fee_year})>" 