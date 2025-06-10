"""
银行和信用卡模块数据库模型

定义银行和信用卡相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, Index, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class Bank(BaseModel):
    """
    银行数据库模型
    
    定义banks表结构，存储银行基本信息。
    """
    __tablename__ = "banks"

    bank_code = Column(
        String(20),
        unique=True,
        nullable=False,
        comment="银行代码"
    )
    
    bank_name = Column(
        String(100),
        nullable=False,
        comment="银行名称"
    )
    
    bank_logo = Column(
        String(500),
        comment="银行logo URL"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        comment="排序权重"
    )

    # 关联关系
    credit_cards = relationship("CreditCard", back_populates="bank")

    # 索引
    __table_args__ = (
        Index('idx_banks_code', 'bank_code'),
        Index('idx_banks_active', 'is_active'),
        Index('idx_banks_sort', 'sort_order'),
    )


class CreditCard(BaseModel):
    """
    信用卡数据库模型
    
    定义credit_cards表结构，存储用户信用卡信息。
    """
    __tablename__ = "credit_cards"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    bank_id = Column(
        UUID(as_uuid=True),
        ForeignKey('banks.id'),
        comment="银行ID"
    )
    
    card_number = Column(
        String(100),
        nullable=False,
        comment="卡号(加密存储)"
    )
    
    card_name = Column(
        String(100),
        nullable=False,
        comment="卡片名称"
    )
    
    card_type = Column(
        String(20),
        default='credit',
        comment="卡片类型：credit, debit"
    )
    
    card_network = Column(
        String(20),
        comment="卡组织：VISA, MasterCard, 银联, American Express, JCB"
    )
    
    card_level = Column(
        String(20),
        comment="卡片等级：普卡, 金卡, 白金卡, 钻石卡, 无限卡"
    )
    
    credit_limit = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="信用额度"
    )
    
    available_limit = Column(
        DECIMAL(15, 2),
        comment="可用额度"
    )
    
    used_limit = Column(
        DECIMAL(15, 2),
        default=0,
        comment="已用额度"
    )
    
    expiry_month = Column(
        Integer,
        nullable=False,
        comment="有效期月份"
    )
    
    expiry_year = Column(
        Integer,
        nullable=False,
        comment="有效期年份"
    )
    
    billing_date = Column(
        Integer,
        comment="账单日"
    )
    
    due_date = Column(
        Integer,
        comment="还款日"
    )
    
    annual_fee = Column(
        DECIMAL(10, 2),
        default=0,
        comment="年费金额"
    )
    
    fee_waivable = Column(
        Boolean,
        default=False,
        comment="年费是否可减免"
    )
    
    fee_auto_deduct = Column(
        Boolean,
        default=False,
        comment="是否自动扣费"
    )
    
    fee_due_month = Column(
        Integer,
        comment="年费到期月份"
    )
    
    features = Column(
        JSONB,
        default='[]',
        comment="特色功能"
    )
    
    points_rate = Column(
        DECIMAL(4, 2),
        default=1.00,
        comment="积分倍率"
    )
    
    cashback_rate = Column(
        DECIMAL(4, 2),
        default=0.00,
        comment="返现比例"
    )
    
    status = Column(
        String(20),
        default='active',
        comment="状态：active, frozen, closed"
    )
    
    is_primary = Column(
        Boolean,
        default=False,
        comment="是否主卡"
    )
    
    notes = Column(
        Text,
        comment="备注"
    )

    # 关联关系
    user = relationship("User", back_populates="credit_cards")
    bank = relationship("Bank", back_populates="credit_cards")
    transactions = relationship("Transaction", back_populates="card", cascade="all, delete-orphan")
    fee_waiver_rules = relationship("FeeWaiverRule", back_populates="card", cascade="all, delete-orphan")
    annual_fee_records = relationship("AnnualFeeRecord", back_populates="card", cascade="all, delete-orphan")
    reminder_settings = relationship("ReminderSetting", back_populates="card")

    # 索引
    __table_args__ = (
        Index('idx_credit_cards_user_id', 'user_id'),
        Index('idx_credit_cards_bank_id', 'bank_id'),
        Index('idx_credit_cards_status', 'status'),
        Index('idx_credit_cards_expiry', 'expiry_year', 'expiry_month'),
        Index('idx_credit_cards_primary', 'is_primary'),
    ) 