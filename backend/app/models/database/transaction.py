"""
交易管理模块数据库模型

定义交易分类和交易记录相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, Index, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class TransactionCategory(BaseModel):
    """
    交易分类数据库模型
    
    定义transaction_categories表结构，存储交易分类信息。
    """
    __tablename__ = "transaction_categories"

    name = Column(
        String(50),
        nullable=False,
        comment="分类名称"
    )
    
    icon = Column(
        String(50),
        comment="图标"
    )
    
    color = Column(
        String(20),
        comment="颜色"
    )
    
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey('transaction_categories.id'),
        comment="父分类ID"
    )
    
    is_system = Column(
        Boolean,
        default=False,
        comment="是否系统分类"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    sort_order = Column(
        Integer,
        default=0,
        comment="排序"
    )

    # 自关联关系
    parent = relationship("TransactionCategory", remote_side=[id], back_populates="children")
    children = relationship("TransactionCategory", back_populates="parent")
    
    # 关联关系
    transactions = relationship("Transaction", back_populates="category")

    # 索引
    __table_args__ = (
        Index('idx_transaction_categories_name', 'name'),
        Index('idx_transaction_categories_parent', 'parent_id'),
        Index('idx_transaction_categories_active', 'is_active'),
        Index('idx_transaction_categories_sort', 'sort_order'),
    )


class Transaction(BaseModel):
    """
    交易记录数据库模型
    
    定义transactions表结构，存储用户交易记录。
    """
    __tablename__ = "transactions"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey('credit_cards.id', ondelete='CASCADE'),
        nullable=False,
        comment="信用卡ID"
    )
    
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey('transaction_categories.id'),
        comment="分类ID"
    )
    
    transaction_type = Column(
        String(20),
        nullable=False,
        comment="交易类型：expense, income, transfer"
    )
    
    amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="交易金额"
    )
    
    currency = Column(
        String(10),
        default='CNY',
        comment="货币类型"
    )
    
    description = Column(
        String(200),
        comment="交易描述"
    )
    
    merchant_name = Column(
        String(100),
        comment="商户名称"
    )
    
    merchant_category = Column(
        String(50),
        comment="商户类别"
    )
    
    location = Column(
        String(200),
        comment="交易地点"
    )
    
    points_earned = Column(
        Integer,
        default=0,
        comment="获得积分"
    )
    
    cashback_earned = Column(
        DECIMAL(10, 2),
        default=0,
        comment="获得返现"
    )
    
    status = Column(
        String(20),
        default='completed',
        comment="状态：pending, completed, failed, refunded"
    )
    
    transaction_date = Column(
        DateTime(timezone=True),
        comment="交易时间"
    )
    
    notes = Column(
        Text,
        comment="备注"
    )
    
    tags = Column(
        JSONB,
        default='[]',
        comment="标签"
    )

    # 关联关系
    user = relationship("User", back_populates="transactions")
    card = relationship("CreditCard", back_populates="transactions")
    category = relationship("TransactionCategory", back_populates="transactions")

    # 索引
    __table_args__ = (
        Index('idx_transactions_user_id', 'user_id'),
        Index('idx_transactions_card_id', 'card_id'),
        Index('idx_transactions_category_id', 'category_id'),
        Index('idx_transactions_type', 'transaction_type'),
        Index('idx_transactions_status', 'status'),
        Index('idx_transactions_date', 'transaction_date'),
        Index('idx_transactions_card_date', 'card_id', 'transaction_date'),
        Index('idx_transactions_amount', 'amount'),
    ) 