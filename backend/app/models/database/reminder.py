"""
提醒相关数据库模型
包括提醒设置和提醒记录
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class ReminderSetting(Base):
    """提醒设置表"""
    __tablename__ = "reminder_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="提醒设置ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id", ondelete="CASCADE"), nullable=True, comment="信用卡ID(NULL表示全局)")
    reminder_type = Column(String(30), nullable=False, comment="提醒类型")
    advance_days = Column(Integer, default=3, comment="提前天数")
    reminder_time = Column(Time, default="09:00:00", comment="提醒时间")
    email_enabled = Column(Boolean, default=True, comment="邮件提醒")
    sms_enabled = Column(Boolean, default=False, comment="短信提醒")
    push_enabled = Column(Boolean, default=True, comment="推送提醒")
    wechat_enabled = Column(Boolean, default=False, comment="微信提醒")
    is_recurring = Column(Boolean, default=True, comment="是否循环")
    frequency = Column(String(20), default="monthly", comment="频率")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="reminder_settings")
    card = relationship("CreditCard", back_populates="reminder_settings")
    reminder_records = relationship("ReminderRecord", back_populates="setting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ReminderSetting(id={self.id}, type={self.reminder_type}, user_id={self.user_id})>"


class ReminderRecord(Base):
    """提醒记录表"""
    __tablename__ = "reminder_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="提醒记录ID")
    setting_id = Column(UUID(as_uuid=True), ForeignKey("reminder_settings.id", ondelete="CASCADE"), nullable=False, comment="提醒设置ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id", ondelete="SET NULL"), nullable=True, comment="信用卡ID")
    reminder_type = Column(String(30), nullable=False, comment="提醒类型")
    title = Column(String(200), nullable=False, comment="提醒标题")
    content = Column(Text, nullable=False, comment="提醒内容")
    email_sent = Column(Boolean, default=False, comment="邮件是否发送")
    sms_sent = Column(Boolean, default=False, comment="短信是否发送")
    push_sent = Column(Boolean, default=False, comment="推送是否发送")
    wechat_sent = Column(Boolean, default=False, comment="微信是否发送")
    scheduled_at = Column(DateTime(timezone=True), nullable=True, comment="计划发送时间")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="实际发送时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    setting = relationship("ReminderSetting", back_populates="reminder_records")
    user = relationship("User")
    card = relationship("CreditCard")

    def __repr__(self):
        return f"<ReminderRecord(id={self.id}, type={self.reminder_type}, user_id={self.user_id})>" 