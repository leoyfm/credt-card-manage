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
    reminder_type: str = Field(..., description="提醒类型: payment_due, annual_fee, card_expiry, custom")
    reminder_name: str = Field(..., max_length=100, description="提醒名称")
    advance_days: int = Field(3, ge=0, le=365, description="提前天数")
    reminder_time: time = Field(time(9, 0), description="提醒时间")
    is_enabled: bool = Field(True, description="是否启用")
    notification_methods: List[str] = Field(["app"], description="通知方式: app, email, sms")
    custom_message: Optional[str] = Field(None, max_length=500, description="自定义消息")
    repeat_interval: str = Field("monthly", description="重复间隔: daily, weekly, monthly, yearly")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

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
                "reminder_type": "payment_due",
                "reminder_name": "还款提醒",
                "advance_days": 3,
                "reminder_time": "09:00:00",
                "is_enabled": True,
                "notification_methods": ["app", "email"],
                "custom_message": "请及时还款，避免逾期",
                "repeat_interval": "monthly",
                "notes": "重要提醒"
            }
        }
    }


class ReminderSettingCreate(ReminderSettingBase):
    """创建提醒设置请求模型"""
    pass


class ReminderSettingUpdate(BaseModel):
    """更新提醒设置请求模型"""
    reminder_name: Optional[str] = Field(None, max_length=100, description="提醒名称")
    advance_days: Optional[int] = Field(None, ge=0, le=365, description="提前天数")
    reminder_time: Optional[time] = Field(None, description="提醒时间")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    notification_methods: Optional[List[str]] = Field(None, description="通知方式")
    custom_message: Optional[str] = Field(None, max_length=500, description="自定义消息")
    repeat_interval: Optional[str] = Field(None, description="重复间隔")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

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
    reminder_date: date = Field(..., description="提醒日期")
    reminder_time: Optional[time] = Field(None, description="提醒时间")
    message: str = Field(..., max_length=1000, description="提醒消息")
    status: str = Field("pending", description="状态: pending, sent, read, cancelled")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, date):
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
                "reminder_date": "2024-01-15",
                "reminder_time": "09:00:00",
                "message": "您的招商银行信用卡将于3天后到期还款，请及时还款",
                "status": "pending",
                "notes": "自动生成的提醒"
            }
        }
    }


class ReminderRecordCreate(ReminderRecordBase):
    """创建提醒记录请求模型"""
    pass


class ReminderRecordUpdate(BaseModel):
    """更新提醒记录请求模型"""
    message: Optional[str] = Field(None, max_length=1000, description="提醒消息")
    status: Optional[str] = Field(None, description="状态")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

    model_config = {
        "from_attributes": True
    }


class ReminderRecordResponse(ReminderRecordBase):
    """提醒记录响应模型"""
    id: UUID = Field(..., description="提醒记录ID")
    reminder_type: Optional[str] = Field(None, description="提醒类型")
    card_name: Optional[str] = Field(None, description="信用卡名称")
    sent_at: Optional[datetime] = Field(None, description="发送时间")
    read_at: Optional[datetime] = Field(None, description="阅读时间")
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
                "total_reminders_30days": 12,
                "pending_reminders": 3,
                "read_rate": 0.85,
                "type_distribution": {
                    "payment_due": 8,
                    "annual_fee": 2,
                    "card_expiry": 2
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
                        "reminder_type": "payment_due",
                        "priority": "high",
                        "card_name": "招商银行信用卡",
                        "reminder_date": "2024-01-15",
                        "message": "还款提醒"
                    }
                ]
            }
        }
    } 