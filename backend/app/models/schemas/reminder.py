"""
提醒相关Pydantic模型
包括提醒设置和提醒记录的请求/响应模型
"""
from pydantic import BaseModel, Field, field_validator, model_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from uuid import UUID
from decimal import Decimal


class ReminderSettingBase(BaseModel):
    """提醒设置基础模型"""
    card_id: Optional[UUID] = Field(None, description="信用卡ID，NULL表示全局提醒")
    reminder_type: str = Field(..., description="提醒类型: payment, annual_fee, card_expiry, custom")
    advance_days: int = Field(3, ge=0, le=365, description="提前天数")
    reminder_time: Optional[time] = Field(time(9, 0), description="提醒时间")
    email_enabled: bool = Field(True, description="邮件提醒")
    sms_enabled: bool = Field(False, description="短信提醒")
    push_enabled: bool = Field(True, description="推送提醒")
    wechat_enabled: bool = Field(False, description="微信提醒")
    is_recurring: bool = Field(True, description="是否循环")
    frequency: str = Field("monthly", description="频率: daily, weekly, monthly, yearly")
    is_enabled: bool = Field(True, description="是否启用")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, time):
                data[field_name] = field_value.strftime("%H:%M:%S") if field_value else None
            elif isinstance(field_value, UUID):
                data[field_name] = str(field_value) if field_value else None
            else:
                data[field_name] = field_value
        return data

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "reminder_type": "payment",
                "advance_days": 3,
                "reminder_time": "09:00:00",
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "wechat_enabled": False,
                "is_recurring": True,
                "frequency": "monthly",
                "is_enabled": True
            }
        }
    }


class ReminderSettingCreate(ReminderSettingBase):
    """创建提醒设置请求模型"""
    pass


class ReminderSettingUpdate(BaseModel):
    """更新提醒设置请求模型"""
    advance_days: Optional[int] = Field(None, ge=0, le=365, description="提前天数")
    reminder_time: Optional[time] = Field(None, description="提醒时间")
    email_enabled: Optional[bool] = Field(None, description="邮件提醒")
    sms_enabled: Optional[bool] = Field(None, description="短信提醒")
    push_enabled: Optional[bool] = Field(None, description="推送提醒")
    wechat_enabled: Optional[bool] = Field(None, description="微信提醒")
    is_recurring: Optional[bool] = Field(None, description="是否循环")
    frequency: Optional[str] = Field(None, description="频率")
    is_enabled: Optional[bool] = Field(None, description="是否启用")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                if isinstance(field_value, time):
                    data[field_name] = field_value.strftime("%H:%M:%S")
                else:
                    data[field_name] = field_value
        return data

    model_config = {
        "from_attributes": True
    }


class ReminderSettingResponse(ReminderSettingBase):
    """提醒设置响应模型"""
    id: UUID = Field(..., description="提醒设置ID")
    user_id: UUID = Field(..., description="用户ID")
    card_name: Optional[str] = Field(None, description="信用卡名称")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, (datetime, date)):
                data[field_name] = field_value.isoformat() if field_value else None
            elif isinstance(field_value, time):
                data[field_name] = field_value.strftime("%H:%M:%S") if field_value else None
            elif isinstance(field_value, UUID):
                data[field_name] = str(field_value) if field_value else None
            else:
                data[field_name] = field_value
        return data

    model_config = {
        "from_attributes": True
    }


class ReminderRecordBase(BaseModel):
    """提醒记录基础模型"""
    setting_id: UUID = Field(..., description="提醒设置ID")
    card_id: Optional[UUID] = Field(None, description="信用卡ID")
    reminder_type: str = Field(..., description="提醒类型")
    title: str = Field(..., max_length=200, description="提醒标题")
    content: str = Field(..., max_length=1000, description="提醒内容")
    email_sent: bool = Field(False, description="邮件是否发送")
    sms_sent: bool = Field(False, description="短信是否发送")
    push_sent: bool = Field(False, description="推送是否发送")
    wechat_sent: bool = Field(False, description="微信是否发送")
    scheduled_at: Optional[datetime] = Field(None, description="计划发送时间")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, (datetime, date)):
                data[field_name] = field_value.isoformat() if field_value else None
            elif isinstance(field_value, time):
                data[field_name] = field_value.strftime("%H:%M:%S") if field_value else None
            elif isinstance(field_value, UUID):
                data[field_name] = str(field_value) if field_value else None
            else:
                data[field_name] = field_value
        return data

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "setting_id": "123e4567-e89b-12d3-a456-426614174000",
                "card_id": "123e4567-e89b-12d3-a456-426614174001",
                "reminder_type": "payment",
                "title": "还款提醒",
                "content": "您的招商银行信用卡将于3天后到期还款，请及时还款",
                "email_sent": False,
                "sms_sent": False,
                "push_sent": False,
                "wechat_sent": False,
                "scheduled_at": "2024-01-15T09:00:00"
            }
        }
    }


class ReminderRecordCreate(ReminderRecordBase):
    """创建提醒记录请求模型"""
    pass


class ReminderRecordUpdate(BaseModel):
    """更新提醒记录请求模型"""
    title: Optional[str] = Field(None, max_length=200, description="提醒标题")
    content: Optional[str] = Field(None, max_length=1000, description="提醒内容")
    email_sent: Optional[bool] = Field(None, description="邮件是否发送")
    sms_sent: Optional[bool] = Field(None, description="短信是否发送")
    push_sent: Optional[bool] = Field(None, description="推送是否发送")
    wechat_sent: Optional[bool] = Field(None, description="微信是否发送")
    scheduled_at: Optional[datetime] = Field(None, description="计划发送时间")

    model_config = {
        "from_attributes": True
    }


class ReminderRecordResponse(ReminderRecordBase):
    """提醒记录响应模型"""
    id: UUID = Field(..., description="提醒记录ID")
    user_id: UUID = Field(..., description="用户ID")
    card_name: Optional[str] = Field(None, description="信用卡名称")
    sent_at: Optional[datetime] = Field(None, description="发送时间")
    created_at: datetime = Field(..., description="创建时间")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, (datetime, date)):
                data[field_name] = field_value.isoformat() if field_value else None
            elif isinstance(field_value, time):
                data[field_name] = field_value.strftime("%H:%M:%S") if field_value else None
            elif isinstance(field_value, UUID):
                data[field_name] = str(field_value) if field_value else None
            else:
                data[field_name] = field_value
        return data

    model_config = {
        "from_attributes": True
    }


class ReminderStatisticsResponse(BaseModel):
    """提醒统计响应模型"""
    total_settings: int = Field(..., description="总设置数")
    active_settings: int = Field(..., description="活跃设置数")
    total_reminders_30days: int = Field(..., description="30天内提醒总数")
    pending_reminders: int = Field(..., description="待处理提醒数")
    read_rate: float = Field(..., description="阅读率")
    type_distribution: Dict[str, int] = Field(..., description="类型分布")
    recent_reminders: List[ReminderRecordResponse] = Field(..., description="最近提醒")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "total_settings": 5,
                "active_settings": 4,
                "total_reminders_30days": 15,
                "pending_reminders": 3,
                "read_rate": 0.85,
                "type_distribution": {
                    "payment": 8,
                    "annual_fee": 4,
                    "card_expiry": 3
                },
                "recent_reminders": []
            }
        }
    }


class UpcomingRemindersResponse(BaseModel):
    """即将到来的提醒响应模型"""
    total_upcoming: int = Field(..., description="即将到来的提醒总数")
    high_priority_count: int = Field(..., description="高优先级提醒数")
    medium_priority_count: int = Field(..., description="中优先级提醒数")
    low_priority_count: int = Field(..., description="低优先级提醒数")
    analysis_period: str = Field(..., description="分析周期")
    reminders: List[Dict[str, Any]] = Field(..., description="提醒列表")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "total_upcoming": 5,
                "high_priority_count": 2,
                "medium_priority_count": 2,
                "low_priority_count": 1,
                "analysis_period": "7天",
                "reminders": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "还款提醒",
                        "content": "您的信用卡还款日即将到来",
                        "reminder_type": "payment",
                        "scheduled_at": "2024-01-15T09:00:00",
                        "priority": "high"
                    }
                ]
            }
        }
    }


class UnreadRemindersCountResponse(BaseModel):
    """未读提醒个数响应模型"""
    total_unread: int = Field(..., description="未读提醒总数")
    type_breakdown: Dict[str, int] = Field(..., description="按类型分布的未读提醒数")
    last_check_time: str = Field(..., description="最后检查时间")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "total_unread": 3,
                "type_breakdown": {
                    "payment": 2,
                    "annual_fee": 1
                },
                "last_check_time": "2024-01-15T10:30:00"
            }
        }
    }


class MarkAllReadResponse(BaseModel):
    """标记所有提醒为已读响应模型"""
    marked_count: int = Field(..., description="标记为已读的提醒数量")
    marked_at: str = Field(..., description="标记时间")
    message: str = Field(..., description="操作结果消息")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "marked_count": 3,
                "marked_at": "2024-01-15T10:30:00",
                "message": "已标记 3 条提醒为已读"
            }
        }
    } 