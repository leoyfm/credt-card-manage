"""
年费管理模块数据库模型

定义年费减免规则和记录相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, Index, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class FeeWaiverRule(BaseModel):
    """
    年费减免规则数据库模型
    
    定义fee_waiver_rules表结构，存储年费减免条件规则。
    """
    __tablename__ = "fee_waiver_rules"

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey('credit_cards.id', ondelete='CASCADE'),
        nullable=False,
        comment="信用卡ID"
    )
    
    rule_group_id = Column(
        UUID(as_uuid=True),
        comment="规则组ID(同组规则用AND连接)"
    )
    
    rule_name = Column(
        String(100),
        nullable=False,
        comment="规则名称"
    )
    
    condition_type = Column(
        String(20),
        nullable=False,
        comment="条件类型：spending_amount, transaction_count, points_redeem, specific_category"
    )
    
    condition_value = Column(
        DECIMAL(15, 2),
        comment="条件数值"
    )
    
    condition_count = Column(
        Integer,
        comment="条件次数"
    )
    
    condition_period = Column(
        String(20),
        default='yearly',
        comment="统计周期：monthly, quarterly, yearly"
    )
    
    logical_operator = Column(
        String(10),
        comment="逻辑操作符：AND, OR, NULL"
    )
    
    priority = Column(
        Integer,
        default=1,
        comment="优先级"
    )
    
    is_enabled = Column(
        Boolean,
        default=True,
        comment="是否启用"
    )
    
    effective_from = Column(
        Date,
        comment="生效日期"
    )
    
    effective_to = Column(
        Date,
        comment="失效日期"
    )
    
    description = Column(
        Text,
        comment="规则说明"
    )

    # 关联关系
    card = relationship("CreditCard", back_populates="fee_waiver_rules")

    # 索引
    __table_args__ = (
        Index('idx_fee_waiver_rules_card_id', 'card_id'),
        Index('idx_fee_waiver_rules_group_id', 'rule_group_id'),
        Index('idx_fee_waiver_rules_type', 'condition_type'),
        Index('idx_fee_waiver_rules_enabled', 'is_enabled'),
        Index('idx_fee_waiver_rules_priority', 'priority'),
    )


class AnnualFeeRecord(BaseModel):
    """
    年费记录数据库模型
    
    定义annual_fee_records表结构，存储年费计算和缴费记录。
    """
    __tablename__ = "annual_fee_records"

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey('credit_cards.id', ondelete='CASCADE'),
        nullable=False,
        comment="信用卡ID"
    )
    
    fee_year = Column(
        Integer,
        nullable=False,
        comment="年费年份"
    )
    
    base_fee = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="基础年费"
    )
    
    actual_fee = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="实际年费"
    )
    
    waiver_amount = Column(
        DECIMAL(10, 2),
        default=0,
        comment="减免金额"
    )
    
    waiver_rules_applied = Column(
        JSONB,
        default='[]',
        comment="应用的减免规则"
    )
    
    rule_evaluation_result = Column(
        JSONB,
        comment="规则评估结果"
    )
    
    waiver_reason = Column(
        String(100),
        comment="减免原因"
    )
    
    calculation_details = Column(
        JSONB,
        comment="计算详情"
    )
    
    status = Column(
        String(20),
        default='pending',
        comment="状态：pending, paid, waived, overdue"
    )
    
    due_date = Column(
        Date,
        comment="应缴日期"
    )
    
    paid_date = Column(
        Date,
        comment="实际缴费日期"
    )
    
    payment_method = Column(
        String(20),
        comment="支付方式：auto_deduct, manual, points, waived"
    )
    
    notes = Column(
        Text,
        comment="备注"
    )

    # 关联关系
    card = relationship("CreditCard", back_populates="annual_fee_records")

    # 索引
    __table_args__ = (
        Index('idx_annual_fee_records_card_id', 'card_id'),
        Index('idx_annual_fee_records_card_year', 'card_id', 'fee_year'),
        Index('idx_annual_fee_records_year', 'fee_year'),
        Index('idx_annual_fee_records_status', 'status'),
        Index('idx_annual_fee_records_due_date', 'due_date'),
        # 唯一约束：每张卡每年只能有一条记录
        Index('idx_annual_fee_records_unique', 'card_id', 'fee_year', unique=True),
    ) 