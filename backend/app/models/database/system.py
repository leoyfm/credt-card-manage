"""
系统配置模块数据库模型

定义系统配置和通知模板相关的SQLAlchemy ORM模型。
"""

from sqlalchemy import Column, String, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB

from .base import BaseModel


class SystemConfig(BaseModel):
    """
    系统配置数据库模型
    
    定义system_configs表结构，存储系统配置参数。
    """
    __tablename__ = "system_configs"

    config_key = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="配置键，全局唯一"
    )
    
    config_value = Column(
        Text,
        comment="配置值"
    )
    
    config_type = Column(
        String(20),
        default='string',
        comment="配置类型：string, integer, boolean, json"
    )
    
    description = Column(
        Text,
        comment="配置描述"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        comment="是否公开配置（前端可访问）"
    )

    # 索引
    __table_args__ = (
        Index('idx_system_configs_key', 'config_key'),
        Index('idx_system_configs_type', 'config_type'),
        Index('idx_system_configs_public', 'is_public'),
    )


class NotificationTemplate(BaseModel):
    """
    通知模板数据库模型
    
    定义notification_templates表结构，存储各种通知模板。
    """
    __tablename__ = "notification_templates"

    template_code = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="模板代码，全局唯一"
    )
    
    template_name = Column(
        String(100),
        nullable=False,
        comment="模板名称"
    )
    
    template_type = Column(
        String(20),
        nullable=False,
        comment="模板类型：email, sms, push, wechat"
    )
    
    subject = Column(
        String(200),
        comment="主题(邮件使用)"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="模板内容"
    )
    
    variables = Column(
        JSONB,
        default='[]',
        comment="变量列表"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        comment="是否激活"
    )

    # 索引
    __table_args__ = (
        Index('idx_notification_templates_code', 'template_code'),
        Index('idx_notification_templates_type', 'template_type'),
        Index('idx_notification_templates_active', 'is_active'),
    ) 