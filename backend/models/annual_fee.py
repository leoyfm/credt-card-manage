from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FeeType(str, Enum):
    """年费类型枚举"""
    RIGID = "rigid"  # 刚性年费，不可减免
    TRANSACTION_COUNT = "transaction_count"  # 刷卡次数减免
    POINTS_EXCHANGE = "points_exchange"  # 积分兑换减免
    TRANSACTION_AMOUNT = "transaction_amount"  # 刷卡金额减免


class WaiverStatus(str, Enum):
    """年费减免状态枚举"""
    PENDING = "pending"  # 待处理
    WAIVED = "waived"  # 已减免
    PAID = "paid"  # 已支付
    OVERDUE = "overdue"  # 逾期


class AnnualFeeRuleBase(BaseModel):
    """年费规则基础模型"""
    rule_name: str = Field(..., description="规则名称")
    fee_type: FeeType = Field(..., description="年费类型")
    base_fee: Decimal = Field(..., description="基础年费金额", ge=0)
    waiver_condition_value: Optional[Decimal] = Field(None, description="减免条件数值")
    waiver_period_months: int = Field(12, description="考核周期（月）", ge=1, le=36)
    description: Optional[str] = Field(None, description="规则描述")


class AnnualFeeRuleCreate(AnnualFeeRuleBase):
    """创建年费规则"""
    pass


class AnnualFeeRuleUpdate(BaseModel):
    """更新年费规则"""
    rule_name: Optional[str] = None
    fee_type: Optional[FeeType] = None
    base_fee: Optional[Decimal] = None
    waiver_condition_value: Optional[Decimal] = None
    waiver_period_months: Optional[int] = None
    description: Optional[str] = None


class AnnualFeeRule(AnnualFeeRuleBase):
    """年费规则响应模型"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AnnualFeeRecordBase(BaseModel):
    """年费记录基础模型"""
    card_id: UUID = Field(..., description="信用卡ID")
    fee_year: int = Field(..., description="年费所属年份")
    due_date: date = Field(..., description="年费到期日期")
    fee_amount: Decimal = Field(..., description="应付年费金额", ge=0)
    waiver_status: WaiverStatus = Field(WaiverStatus.PENDING, description="减免状态")
    waiver_condition_met: bool = Field(False, description="是否满足减免条件")
    current_progress: Decimal = Field(0, description="当前进度", ge=0)
    payment_date: Optional[date] = Field(None, description="实际支付日期")
    notes: Optional[str] = Field(None, description="备注")


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
    """年费减免检查结果"""
    card_id: UUID
    fee_year: int
    waiver_eligible: bool
    current_progress: Decimal
    required_progress: Optional[Decimal]
    progress_description: str
    days_remaining: int


class AnnualFeeStatistics(BaseModel):
    """年费统计信息"""
    total_cards: int
    total_annual_fees: Decimal
    waived_fees: Decimal
    paid_fees: Decimal
    pending_fees: Decimal
    overdue_fees: Decimal
    waiver_rate: float  # 减免率 