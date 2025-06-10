"""
还款提醒模块数据库模型

定义还款提醒设置和记录相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, Integer, Time, DateTime, Index, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class ReminderSetting(BaseModel):
    """
    提醒设置数据库模型
    
    定义reminder_settings表结构，存储用户提醒偏好设置。
    """
    __tablename__ = "reminder_settings"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey('credit_cards.id', ondelete='CASCADE'),
        comment="信用卡ID(NULL表示全局设置)"
    )
    
    reminder_type = Column(
        String(30),
        nullable=False,
        comment="提醒类型：payment_due, annual_fee, balance_alert"
    )
    
    advance_days = Column(
        Integer,
        default=3,
        comment="提前天数"
    )
    
    reminder_time = Column(
        Time,
        default='09:00:00',
        comment="提醒时间"
    )
    
    email_enabled = Column(
        Boolean,
        default=True,
        comment="邮件提醒开关"
    )
    
    sms_enabled = Column(
        Boolean,
        default=False,
        comment="短信提醒开关"
    )
    
    push_enabled = Column(
        Boolean,
        default=True,
        comment="推送提醒开关"
    )
    
    wechat_enabled = Column(
        Boolean,
        default=False,
        comment="微信提醒开关"
    )
    
    is_recurring = Column(
        Boolean,
        default=True,
        comment="是否循环提醒"
    )
    
    frequency = Column(
        String(20),
        default='monthly',
        comment="提醒频率：daily, weekly, monthly"
    )
    
    is_enabled = Column(
        Boolean,
        default=True,
        comment="是否启用"
    )

    # 关联关系
    user = relationship("User", back_populates="reminder_settings")
    card = relationship("CreditCard", back_populates="reminder_settings")
    reminder_logs = relationship("ReminderLog", back_populates="setting", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_reminder_settings_user_id', 'user_id'),
        Index('idx_reminder_settings_card_id', 'card_id'),
        Index('idx_reminder_settings_type', 'reminder_type'),
        Index('idx_reminder_settings_enabled', 'is_enabled'),
        Index('idx_reminder_settings_user_type', 'user_id', 'reminder_type'),
    )


class ReminderLog(BaseModel):
    """
    提醒记录数据库模型
    
    定义reminder_logs表结构，存储提醒发送记录。
    """
    __tablename__ = "reminder_logs"

    setting_id = Column(
        UUID(as_uuid=True),
        ForeignKey('reminder_settings.id', ondelete='CASCADE'),
        nullable=False,
        comment="提醒设置ID"
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey('credit_cards.id', ondelete='SET NULL'),
        comment="信用卡ID"
    )
    
    reminder_type = Column(
        String(30),
        nullable=False,
        comment="提醒类型"
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment="提醒标题"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="提醒内容"
    )
    
    email_sent = Column(
        Boolean,
        default=False,
        comment="邮件是否发送"
    )
    
    sms_sent = Column(
        Boolean,
        default=False,
        comment="短信是否发送"
    )
    
    push_sent = Column(
        Boolean,
        default=False,
        comment="推送是否发送"
    )
    
    wechat_sent = Column(
        Boolean,
        default=False,
        comment="微信是否发送"
    )
    
    scheduled_at = Column(
        DateTime(timezone=True),
        comment="计划发送时间"
    )
    
    sent_at = Column(
        DateTime(timezone=True),
        comment="实际发送时间"
    )

    # 关联关系
    setting = relationship("ReminderSetting", back_populates="reminder_logs")
    user = relationship("User")
    card = relationship("CreditCard")

    # 索引
    __table_args__ = (
        Index('idx_reminder_logs_setting_id', 'setting_id'),
        Index('idx_reminder_logs_user_id', 'user_id'),
        Index('idx_reminder_logs_card_id', 'card_id'),
        Index('idx_reminder_logs_type', 'reminder_type'),
        Index('idx_reminder_logs_scheduled', 'scheduled_at'),
        Index('idx_reminder_logs_sent', 'sent_at'),
    ) 