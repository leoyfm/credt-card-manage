"""
信用卡数据库模型

定义信用卡相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Numeric, Integer, Date, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class CreditCard(BaseModel):
    """
    信用卡数据库模型
    
    定义credit_cards表结构，存储信用卡基本信息。
    """
    __tablename__ = "credit_cards"

    # 用户关联
    user_id = Column(
        UUID(as_uuid=True), 
        nullable=False,
        comment="用户ID，关联users表"
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
    
    card_number = Column(
        String(19), 
        nullable=False,
        unique=True,
        comment="信用卡号，加密存储"
    )
    
    card_type = Column(
        String(20), 
        nullable=False,
        default="visa",
        comment="卡组织类型：visa/mastercard/unionpay/amex/jcb/discover/diners"
    )

    # 额度信息
    credit_limit = Column(
        Numeric(10, 2), 
        nullable=False,
        default=0,
        comment="信用额度"
    )
    
    used_amount = Column(
        Numeric(10, 2), 
        nullable=False,
        default=0,
        comment="已使用额度"
    )

    # 账单和还款日期
    billing_day = Column(
        Integer, 
        nullable=False,
        comment="账单日，1-31"
    )
    
    due_day = Column(
        Integer, 
        nullable=False,
        comment="还款日，1-31"
    )

    # 卡片状态和有效期
    expiry_month = Column(
        Integer, 
        nullable=False,
        comment="卡片有效期月份，1-12"
    )
    
    expiry_year = Column(
        Integer, 
        nullable=False,
        comment="卡片有效期年份，如2024"
    )
    
    status = Column(
        String(20), 
        nullable=False,
        default="inactive",
        comment="卡片状态：active/inactive/frozen/cancelled"
    )
    
    is_active = Column(
        Boolean, 
        nullable=False,
        default=True,
        comment="是否启用"
    )
    
    activation_date = Column(
        Date,
        comment="激活日期"
    )

    # 年费相关
    annual_fee_rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("annual_fee_rules.id"),
        comment="年费规则ID"
    )

    # 显示相关
    card_color = Column(
        String(20), 
        nullable=False,
        default="#1890ff",
        comment="卡片颜色"
    )
    
    notes = Column(
        String(500),
        comment="备注信息"
    )

    # 关联关系
    annual_fee_rule = relationship("AnnualFeeRule", back_populates="cards")
    annual_fee_records = relationship("AnnualFeeRecord", back_populates="card")
    reminders = relationship("Reminder", back_populates="card")
    transactions = relationship("Transaction", back_populates="card")

    # 索引定义
    __table_args__ = (
        Index("idx_credit_cards_user_id", "user_id"),
        Index("idx_credit_cards_bank_name", "bank_name"),
        Index("idx_credit_cards_card_type", "card_type"),
        Index("idx_credit_cards_status", "status"),
        Index("idx_credit_cards_expiry", "expiry_year", "expiry_month"),
        Index("idx_credit_cards_is_active_deleted", "is_active", "is_deleted"),
    )

    def __repr__(self):
        return f"<CreditCard(id={self.id}, bank_name='{self.bank_name}', card_name='{self.card_name}')>"

    @property
    def available_amount(self):
        """计算可用额度"""
        return self.credit_limit - self.used_amount

    @property
    def utilization_rate(self):
        """计算额度使用率"""
        if self.credit_limit == 0:
            return 0
        return float(self.used_amount / self.credit_limit * 100)

    @property
    def masked_card_number(self):
        """获取脱敏的卡号"""
        if len(self.card_number) < 8:
            return self.card_number
        return f"{self.card_number[:4]}****{self.card_number[-4:]}"
    
    @property
    def expiry_display(self) -> str:
        """获取有效期的显示格式，如 '10/27'"""
        return f"{self.expiry_month:02d}/{str(self.expiry_year)[-2:]}"
    
    @property
    def is_expired(self) -> bool:
        """检查卡片是否已过期"""
        from datetime import date
        today = date.today()
        if self.expiry_year < today.year:
            return True
        elif self.expiry_year == today.year and self.expiry_month < today.month:
            return True
        return False 