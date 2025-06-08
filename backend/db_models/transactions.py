"""
交易记录数据库模型

定义交易记录相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, Enum as SQLEnum, Index, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .base import BaseModel


class TransactionType(str, Enum):
    """
    交易类型枚举
    
    定义不同的交易类型：
    - EXPENSE: 消费交易
    - PAYMENT: 还款交易
    - REFUND: 退款交易
    - WITHDRAWAL: 取现交易
    - TRANSFER: 转账交易
    - FEE: 手续费交易
    """
    EXPENSE = "expense"      # 消费
    PAYMENT = "payment"      # 还款
    REFUND = "refund"        # 退款
    WITHDRAWAL = "withdrawal" # 取现
    TRANSFER = "transfer"    # 转账
    FEE = "fee"             # 手续费


class TransactionCategory(str, Enum):
    """
    交易分类枚举
    
    定义不同的消费分类：
    - DINING: 餐饮美食
    - SHOPPING: 购物消费
    - TRANSPORT: 交通出行
    - ENTERTAINMENT: 娱乐休闲
    - MEDICAL: 医疗健康
    - EDUCATION: 教育培训
    - TRAVEL: 旅游酒店
    - FUEL: 加油充值
    - SUPERMARKET: 超市便利
    - ONLINE: 网上购物
    - OTHER: 其他消费
    """
    DINING = "dining"              # 餐饮美食
    SHOPPING = "shopping"          # 购物消费
    TRANSPORT = "transport"        # 交通出行
    ENTERTAINMENT = "entertainment" # 娱乐休闲
    MEDICAL = "medical"           # 医疗健康
    EDUCATION = "education"       # 教育培训
    TRAVEL = "travel"             # 旅游酒店
    FUEL = "fuel"                 # 加油充值
    SUPERMARKET = "supermarket"   # 超市便利
    ONLINE = "online"             # 网上购物
    OTHER = "other"               # 其他消费


class TransactionStatus(str, Enum):
    """
    交易状态枚举
    
    定义交易的处理状态：
    - PENDING: 待处理
    - COMPLETED: 已完成
    - FAILED: 交易失败
    - CANCELLED: 已取消
    - REFUNDED: 已退款
    """
    PENDING = "pending"       # 待处理
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 交易失败
    CANCELLED = "cancelled"   # 已取消
    REFUNDED = "refunded"     # 已退款


class Transaction(BaseModel):
    """
    交易记录数据库模型
    
    定义transactions表结构，存储信用卡交易记录信息。
    """
    __tablename__ = "transactions"

    # 关联信息
    card_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("credit_cards.id"), 
        nullable=False, 
        comment="信用卡ID，关联credit_cards表"
    )
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False, 
        comment="用户ID，关联users表"
    )

    # 交易基本信息
    transaction_type = Column(
        SQLEnum(TransactionType), 
        nullable=False, 
        comment="交易类型：expense/payment/refund/withdrawal/transfer/fee"
    )
    
    amount = Column(
        Numeric(12, 2), 
        nullable=False, 
        comment="交易金额，正数表示支出，负数表示收入，单位：元"
    )
    
    transaction_date = Column(
        DateTime, 
        nullable=False,
        default=datetime.now,
        comment="交易时间"
    )
    
    # 交易描述
    merchant_name = Column(
        String(200), 
        comment="商户名称"
    )
    
    description = Column(
        String(500), 
        comment="交易描述"
    )
    
    # 交易分类
    category = Column(
        SQLEnum(TransactionCategory), 
        default=TransactionCategory.OTHER,
        comment="交易分类：dining/shopping/transport等"
    )
    
    # 交易状态
    status = Column(
        SQLEnum(TransactionStatus), 
        default=TransactionStatus.COMPLETED,
        comment="交易状态：pending/completed/failed/cancelled/refunded"
    )
    
    # 积分相关
    points_earned = Column(
        Numeric(10, 2), 
        default=0,
        comment="获得积分数"
    )
    
    points_rate = Column(
        Numeric(6, 4), 
        comment="积分倍率，如1.5倍积分记录为1.5"
    )
    
    # 附加信息
    reference_number = Column(
        String(100), 
        comment="交易参考号/凭证号"
    )
    
    location = Column(
        String(200), 
        comment="交易地点"
    )
    
    is_installment = Column(
        Boolean, 
        default=False,
        comment="是否分期交易"
    )
    
    installment_count = Column(
        Integer, 
        comment="分期期数"
    )
    
    notes = Column(
        Text, 
        comment="备注信息"
    )

    # 关联关系
    card = relationship("CreditCard", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

    # 索引定义
    __table_args__ = (
        Index("idx_transactions_card_id", "card_id"),
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_date", "transaction_date"),
        Index("idx_transactions_type", "transaction_type"),
        Index("idx_transactions_category", "category"),
        Index("idx_transactions_status", "status"),
        Index("idx_transactions_card_date", "card_id", "transaction_date"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_merchant", "merchant_name"),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, card_id={self.card_id}, amount={self.amount}, type={self.transaction_type})>"

    @property
    def is_expense(self):
        """是否为支出交易"""
        return self.transaction_type in [
            TransactionType.EXPENSE, 
            TransactionType.WITHDRAWAL, 
            TransactionType.FEE
        ]

    @property
    def is_income(self):
        """是否为收入交易"""
        return self.transaction_type in [
            TransactionType.PAYMENT, 
            TransactionType.REFUND
        ]

    @property
    def affects_annual_fee_progress(self):
        """是否影响年费减免进度"""
        # 只有消费交易才计入年费减免进度
        return (
            self.transaction_type == TransactionType.EXPENSE and 
            self.status == TransactionStatus.COMPLETED
        ) 