"""
提醒相关数据库模型
包括提醒设置和提醒记录
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    reminder_name = Column(String(100), nullable=False, comment="提醒名称")
    advance_days = Column(Integer, default=3, comment="提前天数")
    reminder_time = Column(Time, default="09:00:00", comment="提醒时间")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    notification_methods = Column(ARRAY(String), default=["app"], comment="通知方式")
    custom_message = Column(Text, nullable=True, comment="自定义消息")
    repeat_interval = Column(String(20), default="monthly", comment="重复间隔")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="reminder_settings")
    card = relationship("CreditCard", back_populates="reminder_settings")
    reminder_records = relationship("ReminderRecord", back_populates="setting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ReminderSetting(id={self.id}, type={self.reminder_type}, name={self.reminder_name})>"


class ReminderRecord(Base):
    """提醒记录表"""
    __tablename__ = "reminder_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="提醒记录ID")
    setting_id = Column(UUID(as_uuid=True), ForeignKey("reminder_settings.id", ondelete="CASCADE"), nullable=False, comment="提醒设置ID")
    reminder_date = Column(Date, nullable=False, comment="提醒日期")
    reminder_time = Column(Time, nullable=True, comment="提醒时间")
    message = Column(Text, nullable=False, comment="提醒消息")
    status = Column(String(20), default="pending", comment="状态")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="发送时间")
    read_at = Column(DateTime(timezone=True), nullable=True, comment="阅读时间")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    setting = relationship("ReminderSetting", back_populates="reminder_records")

    def __repr__(self):
        return f"<ReminderRecord(id={self.id}, date={self.reminder_date}, status={self.status})>" 