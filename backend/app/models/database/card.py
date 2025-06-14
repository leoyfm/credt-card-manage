"""
信用卡管理模块数据库模型

包含银行信息和信用卡信息的数据库模型定义
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.types import Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Bank(Base):
    """银行信息表"""
    __tablename__ = "banks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="银行ID")
    bank_code = Column(String(20), unique=True, nullable=False, comment="银行代码")
    bank_name = Column(String(100), nullable=False, comment="银行名称")
    bank_logo = Column(String(500), comment="银行logo")
    is_active = Column(Boolean, default=True, comment="是否激活")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    credit_cards = relationship("CreditCard", back_populates="bank")

    def __repr__(self):
        return f"<Bank(id={self.id}, name={self.bank_name})>"


class CreditCard(Base):
    """信用卡信息表"""
    __tablename__ = "credit_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="信用卡ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    bank_id = Column(UUID(as_uuid=True), ForeignKey("banks.id"), comment="银行ID")
    
    # 卡片基本信息
    card_number = Column(String(100), nullable=False, comment="卡号(加密存储)")
    card_name = Column(String(100), nullable=False, comment="卡片名称")
    card_type = Column(String(20), default="credit", comment="卡片类型")
    card_network = Column(String(20), comment="卡组织")
    card_level = Column(String(20), comment="卡片等级")
    
    # 额度信息
    credit_limit = Column(Numeric(15, 2), nullable=False, comment="信用额度")
    available_limit = Column(Numeric(15, 2), comment="可用额度")
    used_limit = Column(Numeric(15, 2), default=0, comment="已用额度")
    
    # 有效期信息
    expiry_month = Column(Integer, nullable=False, comment="有效期月份")
    expiry_year = Column(Integer, nullable=False, comment="有效期年份")
    
    # 账单信息
    billing_date = Column(Integer, comment="账单日")
    due_date = Column(Integer, comment="还款日")
    
    # 年费信息
    annual_fee = Column(Numeric(10, 2), default=0, comment="年费金额")
    fee_waivable = Column(Boolean, default=False, comment="年费是否可减免")
    fee_auto_deduct = Column(Boolean, default=False, comment="是否自动扣费")
    fee_due_month = Column(Integer, comment="年费到期月份")
    
    # 特色功能
    features = Column(JSONB, default=list, comment="特色功能")
    points_rate = Column(Numeric(4, 2), default=1.00, comment="积分倍率")
    cashback_rate = Column(Numeric(4, 2), default=0.00, comment="返现比例")
    
    # 状态信息
    status = Column(String(20), default="active", comment="状态")
    is_primary = Column(Boolean, default=False, comment="是否主卡")
    notes = Column(Text, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    user = relationship("User", back_populates="credit_cards")
    bank = relationship("Bank", back_populates="credit_cards")
    transactions = relationship("Transaction", back_populates="card", cascade="all, delete-orphan")
    annual_fee_records = relationship("AnnualFeeRecord", back_populates="card", cascade="all, delete-orphan")
    fee_waiver_rules = relationship("FeeWaiverRule", back_populates="card", cascade="all, delete-orphan")
    reminder_settings = relationship("ReminderSetting", back_populates="card", cascade="all, delete-orphan")

    @property
    def expiry_display(self) -> str:
        """返回格式化的有效期显示，如 '10/27'"""
        return f"{self.expiry_month:02d}/{str(self.expiry_year)[-2:]}"

    @property
    def is_expired(self) -> bool:
        """检查信用卡是否已过期"""
        from datetime import datetime
        now = datetime.now()
        return (self.expiry_year < now.year or 
                (self.expiry_year == now.year and self.expiry_month < now.month))

    def expires_soon(self, months: int = 3) -> bool:
        """检查信用卡是否即将过期（默认3个月内）"""
        from datetime import datetime, timedelta
        now = datetime.now()
        future = now + timedelta(days=months * 30)
        return (self.expiry_year < future.year or 
                (self.expiry_year == future.year and self.expiry_month <= future.month))

    @property
    def credit_utilization_rate(self) -> float:
        """计算信用额度使用率"""
        if self.credit_limit and self.credit_limit > 0:
            return float(self.used_limit or 0) / float(self.credit_limit) * 100
        return 0.0

    def __repr__(self):
        return f"<CreditCard(id={self.id}, name={self.card_name}, user_id={self.user_id})>" 