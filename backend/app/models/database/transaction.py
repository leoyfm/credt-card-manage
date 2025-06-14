"""
交易管理数据库模型
"""
from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class TransactionCategory(Base):
    """交易分类表"""
    __tablename__ = "transaction_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="分类ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    icon = Column(String(50), comment="图标")
    color = Column(String(20), comment="颜色")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("transaction_categories.id"), comment="父分类ID")
    is_system = Column(Boolean, default=False, comment="是否系统分类")
    is_active = Column(Boolean, default=True, comment="是否激活")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    parent = relationship("TransactionCategory", remote_side=[id], back_populates="children")
    children = relationship("TransactionCategory", back_populates="parent")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    """交易记录表"""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="交易ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=False, comment="信用卡ID")
    category_id = Column(UUID(as_uuid=True), ForeignKey("transaction_categories.id"), comment="分类ID")
    
    # 交易基本信息
    transaction_type = Column(String(20), nullable=False, comment="交易类型: expense, payment, refund, transfer, withdrawal, fee")
    amount = Column(DECIMAL(15, 2), nullable=False, comment="交易金额")
    currency = Column(String(10), default="CNY", comment="货币类型")
    description = Column(String(200), comment="交易描述")
    
    # 商户信息
    merchant_name = Column(String(100), comment="商户名称")
    merchant_category = Column(String(50), comment="商户类别")
    location = Column(String(200), comment="交易地点")
    
    # 奖励信息
    points_earned = Column(Integer, default=0, comment="获得积分")
    cashback_earned = Column(DECIMAL(10, 2), default=0, comment="获得返现")
    
    # 状态和时间
    status = Column(String(20), default="completed", comment="状态: pending, completed, failed, refunded")
    transaction_date = Column(TIMESTAMP(timezone=True), comment="交易时间")
    
    # 其他信息
    notes = Column(Text, comment="备注")
    tags = Column(JSONB, default=list, comment="标签")
    
    # 时间戳
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="transactions")
    card = relationship("CreditCard", back_populates="transactions")
    category = relationship("TransactionCategory", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>" 