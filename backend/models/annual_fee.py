from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FeeType(str, Enum):
    """
    年费类型枚举
    
    定义年费的不同类型和减免方式：
    - RIGID: 刚性年费，无条件收取，不可减免
    - TRANSACTION_COUNT: 根据刷卡次数减免年费
    - TRANSACTION_AMOUNT: 根据刷卡金额减免年费  
    - POINTS_EXCHANGE: 使用积分兑换减免年费
    """
    RIGID = "rigid"  # 刚性年费，不可减免
    TRANSACTION_COUNT = "transaction_count"  # 刷卡次数减免
    POINTS_EXCHANGE = "points_exchange"  # 积分兑换减免
    TRANSACTION_AMOUNT = "transaction_amount"  # 刷卡金额减免


class WaiverStatus(str, Enum):
    """
    年费减免状态枚举
    
    定义年费记录的不同状态：
    - PENDING: 待处理，年费记录已生成但尚未处理
    - WAIVED: 已减免，满足减免条件并已免除年费
    - PAID: 已支付，用户已支付年费
    - OVERDUE: 逾期，超过支付期限未处理
    """
    PENDING = "pending"  # 待处理
    WAIVED = "waived"  # 已减免
    PAID = "paid"  # 已支付
    OVERDUE = "overdue"  # 逾期


class AnnualFeeRuleBase(BaseModel):
    """
    年费规则基础模型
    
    定义年费规则的基础字段，包括规则名称、类型、金额、减免条件等。
    所有年费规则相关的模型都继承此基础模型。
    """
    rule_name: str = Field(
        ..., 
        description="规则名称，如：刷卡次数减免-标准",
        example="刷卡次数减免-标准"
    )
    fee_type: FeeType = Field(
        ..., 
        description="年费类型，决定减免条件的计算方式",
        example=FeeType.TRANSACTION_COUNT
    )
    base_fee: Decimal = Field(
        ..., 
        description="基础年费金额，单位：元", 
        ge=0,
        example=200.00
    )
    waiver_condition_value: Optional[Decimal] = Field(
        None, 
        description="减免条件数值，如刷卡次数12或消费金额50000",
        example=12
    )
    waiver_period_months: int = Field(
        12, 
        description="考核周期（月），通常为12个月", 
        ge=1, 
        le=36,
        example=12
    )
    description: Optional[str] = Field(
        None, 
        description="规则描述，详细说明减免条件",
        example="年内刷卡满12次可减免年费"
    )


class AnnualFeeRuleCreate(AnnualFeeRuleBase):
    """
    创建年费规则请求模型
    
    用于接收创建新年费规则的请求数据，继承基础模型的所有字段。
    """
    pass


class AnnualFeeRuleUpdate(BaseModel):
    """
    更新年费规则请求模型
    
    用于接收更新年费规则的请求数据，所有字段均为可选，
    只更新提供的字段，未提供的字段保持原值不变。
    """
    rule_name: Optional[str] = Field(
        None, 
        description="规则名称",
        example="刷卡次数减免-高级"
    )
    fee_type: Optional[FeeType] = Field(
        None, 
        description="年费类型",
        example=FeeType.TRANSACTION_AMOUNT
    )
    base_fee: Optional[Decimal] = Field(
        None, 
        description="基础年费金额", 
        ge=0,
        example=500.00
    )
    waiver_condition_value: Optional[Decimal] = Field(
        None, 
        description="减免条件数值",
        example=50000
    )
    waiver_period_months: Optional[int] = Field(
        None, 
        description="考核周期（月）", 
        ge=1, 
        le=36,
        example=12
    )
    description: Optional[str] = Field(
        None, 
        description="规则描述",
        example="年内刷卡满5万元可减免年费"
    )


class AnnualFeeRule(AnnualFeeRuleBase):
    """
    年费规则响应模型
    
    用于返回年费规则数据，包含完整的规则信息和系统生成的字段。
    """
    id: UUID = Field(..., description="规则ID，系统自动生成的唯一标识")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class AnnualFeeRecordBase(BaseModel):
    """年费记录基础模型"""
    card_id: UUID = Field(
        ..., 
        description="信用卡ID",
        example="f47ac10b-58cc-4372-a567-0e02b2c3d479"
    )
    fee_year: int = Field(
        ..., 
        description="年费所属年份",
        example=2024
    )
    due_date: date = Field(
        ..., 
        description="年费到期日期",
        example="2024-12-31"
    )
    fee_amount: Decimal = Field(
        ..., 
        description="应付年费金额", 
        ge=0,
        example=200.00
    )
    waiver_status: WaiverStatus = Field(
        WaiverStatus.PENDING, 
        description="减免状态",
        example=WaiverStatus.PENDING
    )
    waiver_condition_met: bool = Field(
        False, 
        description="是否满足减免条件",
        example=False
    )
    current_progress: Decimal = Field(
        0, 
        description="当前进度", 
        ge=0,
        example=8
    )
    payment_date: Optional[date] = Field(
        None, 
        description="实际支付日期",
        example="2024-01-15"
    )
    notes: Optional[str] = Field(
        None, 
        description="备注",
        example="自动生成的年费记录"
    )


class AnnualFeeRecordCreate(AnnualFeeRecordBase):
    """创建年费记录"""
    pass


class AnnualFeeRecordUpdate(BaseModel):
    """更新年费记录"""
    waiver_status: Optional[WaiverStatus] = None
    waiver_condition_met: Optional[bool] = None
    current_progress: Optional[Decimal] = None
    payment_date: Optional[date] = None
    notes: Optional[str] = None


class AnnualFeeRecord(AnnualFeeRecordBase):
    """年费记录响应模型"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnualFeeRecordWithRule(AnnualFeeRecord):
    """包含规则信息的年费记录"""
    rule: AnnualFeeRule


class AnnualFeeWaiverCheck(BaseModel):
    """
    年费减免检查结果模型
    
    包含年费减免条件检查的完整结果，包括当前进度、
    是否符合减免条件、剩余时间等信息。
    """
    card_id: UUID = Field(..., description="信用卡ID")
    fee_year: int = Field(..., description="年费年份")
    waiver_eligible: bool = Field(..., description="是否符合减免条件")
    current_progress: Decimal = Field(..., description="当前进度，如已刷卡次数或金额")
    required_progress: Optional[Decimal] = Field(None, description="要求进度，减免所需的目标值")
    progress_description: str = Field(..., description="进度描述，易于理解的文字说明")
    days_remaining: int = Field(..., description="距离年费到期的剩余天数")


class AnnualFeeStatistics(BaseModel):
    """
    年费统计信息模型
    
    提供用户年费的统计数据，包括总金额、减免金额、
    支付状态分布等统计信息。
    """
    total_cards: int = Field(..., description="信用卡总数")
    total_annual_fees: Decimal = Field(..., description="年费总金额")
    waived_fees: Decimal = Field(..., description="已减免年费金额")
    paid_fees: Decimal = Field(..., description="已支付年费金额")
    pending_fees: Decimal = Field(..., description="待处理年费金额")
    overdue_fees: Decimal = Field(..., description="逾期年费金额")
    waiver_rate: float = Field(..., description="年费减免率，百分比形式")  # 减免率 