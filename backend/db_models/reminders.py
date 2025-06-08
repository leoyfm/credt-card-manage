"""
还款提醒数据库模型

定义还款提醒相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Numeric, Date, Boolean, ForeignKey, Text, Enum as SQLEnum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel
from models.reminders import ReminderType, ReminderStatus


class Reminder(BaseModel):
    """
    还款提醒数据库模型
    
    定义reminders表结构，存储还款提醒信息。
    """
    __tablename__ = "reminders"

    # 用户和卡片关联
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="用户ID，提醒所属用户"
    )
    
    card_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("credit_cards.id"), 
        nullable=False, 
        comment="信用卡ID，关联的信用卡"
    )

    # 提醒基本信息
    reminder_type = Column(
        SQLEnum(ReminderType), 
        nullable=False, 
        comment="提醒类型：payment/bill/annual_fee/overdue"
    )
    
    title = Column(
        String(100), 
        nullable=False, 
        comment="提醒标题"
    )
    
    message = Column(
        String(500), 
        nullable=False, 
        comment="提醒内容"
    )

    # 时间信息
    reminder_date = Column(
        Date, 
        nullable=False, 
        comment="提醒日期"
    )
    
    due_date = Column(
        Date, 
        nullable=False, 
        comment="到期日期（还款日或账单日）"
    )

    # 金额信息
    amount = Column(
        Numeric(10, 2), 
        comment="相关金额，如还款金额、年费金额"
    )

    # 状态信息
    status = Column(
        SQLEnum(ReminderStatus), 
        default=ReminderStatus.PENDING,
        comment="提醒状态：pending/sent/read/ignored"
    )
    
    is_active = Column(
        Boolean, 
        default=True, 
        comment="是否启用此提醒"
    )

    # 时间戳
    sent_at = Column(
        DateTime(timezone=True),
        comment="发送时间"
    )
    
    read_at = Column(
        DateTime(timezone=True),
        comment="已读时间"
    )

    # 备注
    notes = Column(
        Text, 
        comment="备注信息"
    )

    # 关联关系
    card = relationship("CreditCard", back_populates="reminders")

    # 索引定义
    __table_args__ = (
        Index("idx_reminders_user_id", "user_id"),
        Index("idx_reminders_card_id", "card_id"),
        Index("idx_reminders_type", "reminder_type"),
        Index("idx_reminders_status", "status"),
        Index("idx_reminders_reminder_date", "reminder_date"),
        Index("idx_reminders_due_date", "due_date"),
        Index("idx_reminders_user_status", "user_id", "status"),
    )

    def __repr__(self):
        return f"<Reminder(id={self.id}, card_id={self.card_id}, type='{self.reminder_type}', status='{self.status}')>" 