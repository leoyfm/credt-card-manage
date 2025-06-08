from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ReminderType(str, Enum):
    """
    提醒类型枚举
    
    定义不同的提醒类型：
    - PAYMENT: 还款提醒，到期还款通知
    - BILL: 账单提醒，账单生成通知
    - ANNUAL_FEE: 年费提醒，年费到期通知
    - OVERDUE: 逾期提醒，逾期还款警告
    """
    PAYMENT = "payment"      # 还款提醒
    BILL = "bill"           # 账单提醒
    ANNUAL_FEE = "annual_fee"  # 年费提醒
    OVERDUE = "overdue"     # 逾期提醒


class ReminderStatus(str, Enum):
    """
    提醒状态枚举
    
    定义提醒的状态：
    - PENDING: 待发送，提醒待触发
    - SENT: 已发送，提醒已推送
    - READ: 已读，用户已查看
    - IGNORED: 已忽略，用户忽略提醒
    """
    PENDING = "pending"    # 待发送
    SENT = "sent"         # 已发送
    READ = "read"         # 已读
    IGNORED = "ignored"   # 已忽略


class ReminderBase(BaseModel):
    """
    还款提醒基础模型
    
    定义还款提醒的基础字段，包括提醒类型、时间、内容等。
    """
    card_id: UUID = Field(
        ..., 
        description="信用卡ID，关联的信用卡",
        json_schema_extra={"example": "f47ac10b-58cc-4372-a567-0e02b2c3d479"}
    )
    
    reminder_type: ReminderType = Field(
        ...,
        description="提醒类型",
        json_schema_extra={"example": ReminderType.PAYMENT}
    )
    
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="提醒标题",
        json_schema_extra={"example": "招商银行信用卡还款提醒"}
    )
    
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="提醒内容",
        json_schema_extra={"example": "您的招商银行信用卡将于3天后到期还款，请及时还款避免逾期"}
    )
    
    reminder_date: date = Field(
        ...,
        description="提醒日期",
        json_schema_extra={"example": "2024-01-20"}
    )
    
    due_date: date = Field(
        ...,
        description="到期日期（还款日或账单日）",
        json_schema_extra={"example": "2024-01-25"}
    )
    
    amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="相关金额，如还款金额、年费金额",
        json_schema_extra={"example": 3500.50}
    )
    
    status: ReminderStatus = Field(
        ReminderStatus.PENDING,
        description="提醒状态",
        json_schema_extra={"example": ReminderStatus.PENDING}
    )
    
    is_active: bool = Field(
        True,
        description="是否启用此提醒",
        json_schema_extra={"example": True}
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=300,
        description="备注信息",
        json_schema_extra={"example": "自动生成的还款提醒"}
    )


class ReminderCreate(ReminderBase):
    """
    创建还款提醒请求模型
    
    用于接收创建新还款提醒的请求数据。
    """
    pass


class ReminderUpdate(BaseModel):
    """
    更新还款提醒请求模型
    
    用于接收更新还款提醒的请求数据，所有字段均为可选。
    """
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="提醒标题",
        json_schema_extra={"example": "工商银行信用卡还款提醒"}
    )
    message: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=500, 
        description="提醒内容",
        json_schema_extra={"example": "您的工商银行信用卡账单已出，请及时还款"}
    )
    reminder_date: Optional[date] = Field(
        None, 
        description="提醒日期",
        json_schema_extra={"example": "2024-01-22"}
    )
    due_date: Optional[date] = Field(
        None, 
        description="到期日期",
        json_schema_extra={"example": "2024-01-28"}
    )
    amount: Optional[Decimal] = Field(
        None, 
        ge=0, 
        description="相关金额",
        json_schema_extra={"example": 4200.00}
    )
    status: Optional[ReminderStatus] = Field(
        None, 
        description="提醒状态",
        json_schema_extra={"example": ReminderStatus.READ}
    )
    is_active: Optional[bool] = Field(
        None, 
        description="是否启用此提醒",
        json_schema_extra={"example": True}
    )
    notes: Optional[str] = Field(
        None, 
        max_length=300, 
        description="备注信息",
        json_schema_extra={"example": "已提醒用户还款"}
    )


class Reminder(ReminderBase):
    """
    还款提醒响应模型
    
    用于返回还款提醒数据，包含完整的提醒信息和系统生成的字段。
    """
    id: UUID = Field(..., description="提醒ID，系统自动生成的唯一标识")
    user_id: UUID = Field(..., description="用户ID，提醒所属用户")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    sent_at: Optional[datetime] = Field(None, description="发送时间")
    read_at: Optional[datetime] = Field(None, description="已读时间")

    model_config = ConfigDict(from_attributes=True) 