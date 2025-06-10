"""
还款提醒管理 Pydantic 模型

本模块定义了还款提醒系统的所有数据模型，包括：
- 提醒设置模型 (ReminderSetting)
- 提醒记录模型 (ReminderLog)  
- 请求响应模型
- 查询请求模型
- 统计分析模型
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, validator, model_validator
from .common import BaseResponse, BasePaginatedResponse, BaseQueryParams


# ================================
# 枚举定义
# ================================

class ReminderType(str, Enum):
    """提醒类型"""
    PAYMENT_DUE = "payment_due"        # 还款日提醒
    ANNUAL_FEE = "annual_fee"          # 年费提醒
    BALANCE_ALERT = "balance_alert"    # 余额警报
    STATEMENT_READY = "statement_ready" # 账单生成提醒
    OVERDUE_WARNING = "overdue_warning" # 逾期警告
    PROMOTIONAL_OFFER = "promotional_offer" # 优惠活动提醒


class NotificationChannel(str, Enum):
    """通知渠道"""
    EMAIL = "email"                    # 邮件通知
    SMS = "sms"                       # 短信通知
    PUSH = "push"                     # 推送通知
    WECHAT = "wechat"                 # 微信通知
    IN_APP = "in_app"                 # 应用内通知


class ReminderFrequency(str, Enum):
    """提醒频率"""
    ONCE = "once"                     # 一次性
    DAILY = "daily"                   # 每日
    WEEKLY = "weekly"                 # 每周
    MONTHLY = "monthly"               # 每月
    YEARLY = "yearly"                 # 每年


class ReminderStatus(str, Enum):
    """提醒状态"""
    ACTIVE = "active"                 # 激活
    INACTIVE = "inactive"             # 未激活
    PAUSED = "paused"                 # 暂停
    COMPLETED = "completed"           # 已完成
    FAILED = "failed"                 # 失败


class DeliveryStatus(str, Enum):
    """发送状态"""
    PENDING = "pending"               # 待发送
    SENT = "sent"                     # 已发送
    DELIVERED = "delivered"           # 已送达
    FAILED = "failed"                 # 发送失败
    CLICKED = "clicked"               # 已点击
    READ = "read"                     # 已阅读


# ================================
# 提醒设置相关模型
# ================================

class ReminderSettingBase(BaseModel):
    """提醒设置基础模型"""
    reminder_type: ReminderType = Field(..., description="提醒类型")
    advance_days: int = Field(3, ge=0, le=30, description="提前天数，0-30天")
    reminder_time: time = Field(time(9, 0), description="提醒时间，默认09:00")
    
    # 通知渠道配置
    email_enabled: bool = Field(True, description="是否启用邮件提醒")
    sms_enabled: bool = Field(False, description="是否启用短信提醒")
    push_enabled: bool = Field(True, description="是否启用推送提醒")
    wechat_enabled: bool = Field(False, description="是否启用微信提醒")
    in_app_enabled: bool = Field(True, description="是否启用应用内提醒")
    
    # 重复和频率设置
    is_recurring: bool = Field(True, description="是否为循环提醒")
    frequency: ReminderFrequency = Field(ReminderFrequency.MONTHLY, description="提醒频率")
    custom_message: Optional[str] = Field(None, max_length=500, description="自定义消息内容")
    
    # 条件设置
    threshold_amount: Optional[Decimal] = Field(None, ge=0, description="触发金额阈值")
    threshold_percentage: Optional[int] = Field(None, ge=1, le=100, description="触发百分比阈值")
    
    is_enabled: bool = Field(True, description="是否启用此提醒设置")
    
    @validator('advance_days')
    def validate_advance_days(cls, v, values):
        """验证提前天数合理性"""
        reminder_type = values.get('reminder_type')
        if reminder_type == ReminderType.PAYMENT_DUE and v > 15:
            raise ValueError("还款日提醒的提前天数不应超过15天")
        if reminder_type == ReminderType.ANNUAL_FEE and v > 30:
            raise ValueError("年费提醒的提前天数不应超过30天")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_channels(cls, values):
        """验证至少启用一个通知渠道"""
        if isinstance(values, dict):
            channels = [
                values.get('email_enabled', False),
                values.get('sms_enabled', False),
                values.get('push_enabled', False),
                values.get('wechat_enabled', False),
                values.get('in_app_enabled', False)
            ]
            if not any(channels):
                raise ValueError("至少需要启用一个通知渠道")
        return values


class ReminderSettingCreate(ReminderSettingBase):
    """创建提醒设置请求模型"""
    card_id: Optional[UUID] = Field(None, description="关联信用卡ID，为空表示全局设置")
    
    class Config:
        schema_extra = {
            "example": {
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "reminder_type": "payment_due",
                "advance_days": 3,
                "reminder_time": "09:00:00",
                "email_enabled": True,
                "push_enabled": True,
                "sms_enabled": False,
                "is_recurring": True,
                "frequency": "monthly",
                "custom_message": "您的信用卡即将到期，请及时还款",
                "is_enabled": True
            }
        }


class ReminderSettingUpdate(BaseModel):
    """更新提醒设置请求模型"""
    advance_days: Optional[int] = Field(None, ge=0, le=30, description="提前天数")
    reminder_time: Optional[time] = Field(None, description="提醒时间")
    
    email_enabled: Optional[bool] = Field(None, description="邮件提醒")
    sms_enabled: Optional[bool] = Field(None, description="短信提醒")
    push_enabled: Optional[bool] = Field(None, description="推送提醒")
    wechat_enabled: Optional[bool] = Field(None, description="微信提醒")
    in_app_enabled: Optional[bool] = Field(None, description="应用内提醒")
    
    frequency: Optional[ReminderFrequency] = Field(None, description="提醒频率")
    custom_message: Optional[str] = Field(None, max_length=500, description="自定义消息")
    threshold_amount: Optional[Decimal] = Field(None, ge=0, description="金额阈值")
    threshold_percentage: Optional[int] = Field(None, ge=1, le=100, description="百分比阈值")
    
    is_enabled: Optional[bool] = Field(None, description="是否启用")

    class Config:
        schema_extra = {
            "example": {
                "advance_days": 5,
                "reminder_time": "10:00:00",
                "email_enabled": True,
                "push_enabled": True,
                "custom_message": "更新后的提醒消息",
                "is_enabled": True
            }
        }


class ReminderSettingResponse(ReminderSettingBase):
    """提醒设置响应模型"""
    id: UUID = Field(..., description="提醒设置ID")
    user_id: UUID = Field(..., description="用户ID")
    card_id: Optional[UUID] = Field(None, description="关联信用卡ID")
    card_name: Optional[str] = Field(None, description="信用卡名称")
    
    status: ReminderStatus = Field(ReminderStatus.ACTIVE, description="提醒状态")
    next_trigger_date: Optional[date] = Field(None, description="下次触发日期")
    
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-uuid-here",
                "card_id": "card-uuid-here",
                "card_name": "招商银行信用卡",
                "reminder_type": "payment_due",
                "advance_days": 3,
                "reminder_time": "09:00:00",
                "email_enabled": True,
                "push_enabled": True,
                "status": "active",
                "next_trigger_date": "2024-12-15",
                "created_at": "2024-12-01T10:00:00Z",
                "updated_at": "2024-12-01T10:00:00Z"
            }
        }


# ================================
# 提醒记录相关模型
# ================================

class ReminderLogBase(BaseModel):
    """提醒记录基础模型"""
    title: str = Field(..., max_length=200, description="提醒标题")
    content: str = Field(..., max_length=2000, description="提醒内容")
    
    # 相关数据
    related_amount: Optional[Decimal] = Field(None, description="相关金额")
    related_date: Optional[date] = Field(None, description="相关日期")
    action_url: Optional[str] = Field(None, max_length=500, description="操作链接")
    
    # 发送状态
    email_status: DeliveryStatus = Field(DeliveryStatus.PENDING, description="邮件发送状态")
    sms_status: DeliveryStatus = Field(DeliveryStatus.PENDING, description="短信发送状态")
    push_status: DeliveryStatus = Field(DeliveryStatus.PENDING, description="推送发送状态")
    wechat_status: DeliveryStatus = Field(DeliveryStatus.PENDING, description="微信发送状态")
    in_app_status: DeliveryStatus = Field(DeliveryStatus.PENDING, description="应用内状态")
    
    scheduled_at: datetime = Field(..., description="计划发送时间")
    sent_at: Optional[datetime] = Field(None, description="实际发送时间")
    read_at: Optional[datetime] = Field(None, description="阅读时间")
    
    # 错误信息
    error_message: Optional[str] = Field(None, max_length=1000, description="错误信息")
    retry_count: int = Field(0, ge=0, description="重试次数")


class ReminderLogResponse(ReminderLogBase):
    """提醒记录响应模型"""
    id: UUID = Field(..., description="提醒记录ID")
    setting_id: UUID = Field(..., description="提醒设置ID")
    user_id: UUID = Field(..., description="用户ID")
    card_id: Optional[UUID] = Field(None, description="关联信用卡ID")
    
    reminder_type: ReminderType = Field(..., description="提醒类型")
    card_name: Optional[str] = Field(None, description="信用卡名称")
    
    # 总体状态
    overall_status: DeliveryStatus = Field(..., description="总体发送状态")
    is_read: bool = Field(False, description="是否已读")
    
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "log-uuid-here",
                "setting_id": "setting-uuid-here",
                "user_id": "user-uuid-here",
                "card_id": "card-uuid-here",
                "reminder_type": "payment_due",
                "title": "信用卡还款提醒",
                "content": "您的招商银行信用卡将于3天后到期，请及时还款",
                "card_name": "招商银行信用卡",
                "related_amount": 1500.00,
                "related_date": "2024-12-15",
                "overall_status": "sent",
                "email_status": "delivered",
                "push_status": "sent",
                "is_read": False,
                "scheduled_at": "2024-12-12T09:00:00Z",
                "sent_at": "2024-12-12T09:00:30Z",
                "created_at": "2024-12-12T08:00:00Z"
            }
        }


# ================================
# 查询和过滤模型
# ================================

class ReminderSettingQuery(BaseQueryParams):
    """提醒设置查询参数"""
    card_id: Optional[UUID] = Field(None, description="信用卡ID筛选")
    reminder_type: Optional[ReminderType] = Field(None, description="提醒类型筛选")
    status: Optional[ReminderStatus] = Field(None, description="状态筛选")
    is_enabled: Optional[bool] = Field(None, description="启用状态筛选")
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "keyword": "还款",
                "card_id": "card-uuid-here",
                "reminder_type": "payment_due",
                "is_enabled": True
            }
        }


class ReminderLogQuery(BaseQueryParams):
    """提醒记录查询参数"""
    card_id: Optional[UUID] = Field(None, description="信用卡ID筛选")
    reminder_type: Optional[ReminderType] = Field(None, description="提醒类型筛选")
    overall_status: Optional[DeliveryStatus] = Field(None, description="发送状态筛选")
    is_read: Optional[bool] = Field(None, description="阅读状态筛选")
    
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError("结束日期不能早于开始日期")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "reminder_type": "payment_due",
                "overall_status": "sent",
                "is_read": False,
                "start_date": "2024-12-01",
                "end_date": "2024-12-31"
            }
        }


# ================================
# 批量操作模型
# ================================

class BatchReminderOperation(BaseModel):
    """批量提醒操作模型"""
    reminder_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="提醒ID列表")
    operation: str = Field(..., description="操作类型：enable/disable/delete")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['enable', 'disable', 'delete', 'mark_read']
        if v not in allowed_operations:
            raise ValueError(f"操作类型必须是：{', '.join(allowed_operations)}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "reminder_ids": ["uuid1", "uuid2", "uuid3"],
                "operation": "enable"
            }
        }


class BatchOperationResult(BaseModel):
    """批量操作结果模型"""
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    failed_items: List[Dict[str, Any]] = Field([], description="失败项详情")
    
    class Config:
        schema_extra = {
            "example": {
                "total_count": 3,
                "success_count": 2,
                "failed_count": 1,
                "failed_items": [
                    {
                        "id": "uuid3",
                        "error": "提醒不存在或已删除"
                    }
                ]
            }
        }


# ================================
# 统计分析模型
# ================================

class ReminderStatistics(BaseModel):
    """提醒统计模型"""
    total_settings: int = Field(0, description="总提醒设置数")
    active_settings: int = Field(0, description="活跃设置数")
    
    # 类型统计
    type_distribution: Dict[str, int] = Field({}, description="类型分布")
    channel_usage: Dict[str, int] = Field({}, description="渠道使用统计")
    
    # 发送统计
    total_sent: int = Field(0, description="总发送数")
    delivery_rate: float = Field(0.0, description="送达率")
    read_rate: float = Field(0.0, description="阅读率")
    
    # 近期活动
    recent_reminders: List[Dict[str, Any]] = Field([], description="近期提醒")
    
    class Config:
        schema_extra = {
            "example": {
                "total_settings": 15,
                "active_settings": 12,
                "type_distribution": {
                    "payment_due": 8,
                    "annual_fee": 4,
                    "balance_alert": 3
                },
                "channel_usage": {
                    "email": 12,
                    "push": 15,
                    "sms": 3
                },
                "total_sent": 156,
                "delivery_rate": 94.5,
                "read_rate": 67.3,
                "recent_reminders": []
            }
        }


class ReminderTrendData(BaseModel):
    """提醒趋势数据模型"""
    date: date = Field(..., description="日期")
    sent_count: int = Field(0, description="发送数量")
    delivered_count: int = Field(0, description="送达数量")
    read_count: int = Field(0, description="阅读数量")
    failed_count: int = Field(0, description="失败数量")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-12-01",
                "sent_count": 25,
                "delivered_count": 23,
                "read_count": 15,
                "failed_count": 2
            }
        }


# ================================
# 预设模板模型
# ================================

class ReminderTemplate(BaseModel):
    """提醒模板模型"""
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    reminder_type: ReminderType = Field(..., description="适用提醒类型")
    title_template: str = Field(..., description="标题模板")
    content_template: str = Field(..., description="内容模板")
    variables: List[str] = Field([], description="可用变量列表")
    is_system: bool = Field(True, description="是否系统模板")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "payment_due_default",
                "name": "默认还款提醒",
                "reminder_type": "payment_due",
                "title_template": "{card_name}还款提醒",
                "content_template": "您的{card_name}将于{days}天后到期，请及时还款{amount}元",
                "variables": ["card_name", "days", "amount", "due_date"],
                "is_system": True
            }
        }


# ================================
# 响应模型
# ================================

class ReminderSettingListResponse(BasePaginatedResponse):
    """提醒设置列表响应"""
    data: List[ReminderSettingResponse] = Field([], description="提醒设置列表")


class ReminderLogListResponse(BasePaginatedResponse):
    """提醒记录列表响应"""
    data: List[ReminderLogResponse] = Field([], description="提醒记录列表")


class ReminderTemplateListResponse(BaseResponse):
    """提醒模板列表响应"""
    data: List[ReminderTemplate] = Field([], description="模板列表")


class ReminderStatisticsResponse(BaseResponse):
    """提醒统计响应"""
    data: ReminderStatistics = Field(..., description="统计数据")


class ReminderTrendResponse(BaseResponse):
    """提醒趋势响应"""
    data: List[ReminderTrendData] = Field([], description="趋势数据")


# ================================
# 特殊操作模型
# ================================

class SnoozeReminderRequest(BaseModel):
    """延后提醒请求模型"""
    snooze_minutes: int = Field(..., ge=5, le=1440, description="延后分钟数，5分钟到24小时")
    reason: Optional[str] = Field(None, max_length=200, description="延后原因")
    
    class Config:
        schema_extra = {
            "example": {
                "snooze_minutes": 60,
                "reason": "暂时无法处理，1小时后提醒"
            }
        }


class TestReminderRequest(BaseModel):
    """测试提醒请求模型"""
    channels: List[NotificationChannel] = Field(..., min_items=1, description="测试渠道")
    test_message: Optional[str] = Field(None, max_length=200, description="测试消息")
    
    class Config:
        schema_extra = {
            "example": {
                "channels": ["email", "push"],
                "test_message": "这是一条测试提醒消息"
            }
        }


class QuickReminderSetup(BaseModel):
    """快速设置提醒模型"""
    preset_type: str = Field(..., description="预设类型：basic/advanced/custom")
    cards: Optional[List[UUID]] = Field(None, description="适用信用卡列表，为空表示所有卡片")
    
    @validator('preset_type')
    def validate_preset_type(cls, v):
        allowed_types = ['basic', 'advanced', 'custom']
        if v not in allowed_types:
            raise ValueError(f"预设类型必须是：{', '.join(allowed_types)}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "preset_type": "basic",
                "cards": ["card-uuid-1", "card-uuid-2"]
            }
        }