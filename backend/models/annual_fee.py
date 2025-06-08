from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


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
    
    定义年费规则的基础字段，包括类型、金额、减免条件、扣费周期等。
    所有年费规则相关的模型都继承此基础模型。
    """
    fee_type: FeeType = Field(
        ..., 
        description="年费类型，决定减免条件的计算方式",
        json_schema_extra={"example": FeeType.TRANSACTION_COUNT}
    )
    base_fee: Decimal = Field(
        ..., 
        description="基础年费金额，单位：元", 
        ge=0,
        json_schema_extra={"example": 200.00}
    )
    waiver_condition_value: Optional[Decimal] = Field(
        None, 
        description="减免条件数值，如刷卡次数12或消费金额50000",
        json_schema_extra={"example": 12}
    )
    points_per_yuan: Optional[Decimal] = Field(
        None, 
        description="积分兑换比例：1元对应的积分数，如1元=0.1积分。仅当fee_type为points_exchange时有效",
        json_schema_extra={"example": 0.1},
        ge=0
    )
    annual_fee_month: Optional[int] = Field(
        None, 
        description="年费扣除月份，1-12月。如每年2月扣费则填2",
        json_schema_extra={"example": 2},
        ge=1,
        le=12
    )
    annual_fee_day: Optional[int] = Field(
        None, 
        description="年费扣除日期，1-31日。如每年2月18日扣费则填18",
        json_schema_extra={"example": 18},
        ge=1,
        le=31
    )
    description: Optional[str] = Field(
        None, 
        description="规则描述，详细说明减免条件",
        json_schema_extra={"example": "年内刷卡满12次可减免年费，每年2月18日扣除"}
    )

    @field_validator('points_per_yuan')
    @classmethod
    def validate_points_per_yuan(cls, v, info):
        """验证积分兑换比例"""
        if info.data and 'fee_type' in info.data:
            fee_type = info.data.get('fee_type')
            if fee_type == FeeType.POINTS_EXCHANGE and v is None:
                raise ValueError('积分兑换类型的年费规则必须设置积分兑换比例')
        return v

    @field_validator('annual_fee_day')
    @classmethod
    def validate_annual_fee_day(cls, v, info):
        """验证年费扣除日期的合理性"""
        if v is not None and info.data and 'annual_fee_month' in info.data:
            month = info.data.get('annual_fee_month')
            if month is not None:
                # 验证2月份不超过29日
                if month == 2 and v > 29:
                    raise ValueError('2月份的日期不能超过29日')
                # 验证30天月份不超过30日
                elif month in [4, 6, 9, 11] and v > 30:
                    raise ValueError('4、6、9、11月份的日期不能超过30日')
        return v


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
    fee_type: Optional[FeeType] = Field(
        None, 
        description="年费类型",
        json_schema_extra={"example": FeeType.TRANSACTION_AMOUNT}
    )
    base_fee: Optional[Decimal] = Field(
        None, 
        description="基础年费金额", 
        ge=0,
        json_schema_extra={"example": 500.00}
    )
    waiver_condition_value: Optional[Decimal] = Field(
        None, 
        description="减免条件数值",
        json_schema_extra={"example": 50000}
    )
    points_per_yuan: Optional[Decimal] = Field(
        None, 
        description="积分兑换比例",
        json_schema_extra={"example": 0.05},
        ge=0
    )
    annual_fee_month: Optional[int] = Field(
        None, 
        description="年费扣除月份", 
        ge=1, 
        le=12,
        json_schema_extra={"example": 3}
    )
    annual_fee_day: Optional[int] = Field(
        None, 
        description="年费扣除日期", 
        ge=1, 
        le=31,
        json_schema_extra={"example": 15}
    )
    description: Optional[str] = Field(
        None, 
        description="规则描述",
        json_schema_extra={"example": "年内刷卡满5万元可减免年费，每年3月15日扣除"}
    )


class AnnualFeeRule(AnnualFeeRuleBase):
    """
    年费规则响应模型
    
    用于返回年费规则数据，包含完整的规则信息和系统生成的字段。
    """
    id: UUID = Field(..., description="规则ID，系统自动生成的唯一标识")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)

    def calculate_points_required(self, fee_amount: Decimal) -> Optional[Decimal]:
        """
        计算减免年费所需的积分数量
        
        参数:
        - fee_amount: 年费金额
        
        返回:
        - 所需积分数量，如果不是积分兑换类型则返回None
        """
        if self.fee_type == FeeType.POINTS_EXCHANGE and self.points_per_yuan:
            return fee_amount * self.points_per_yuan
        return None

    def get_annual_due_date(self, year: int) -> Optional[date]:
        """
        获取指定年份的年费到期日期
        
        参数:
        - year: 年份
        
        返回:
        - 年费到期日期，如果未设置扣费月日则返回None
        """
        if self.annual_fee_month and self.annual_fee_day:
            try:
                return date(year, self.annual_fee_month, self.annual_fee_day)
            except ValueError:
                # 处理2月29日等无效日期
                if self.annual_fee_month == 2 and self.annual_fee_day == 29:
                    # 非闰年时使用2月28日
                    return date(year, 2, 28)
                return None
        return None

    def get_fee_type_display(self) -> str:
        """获取年费类型的中文显示名称"""
        type_display = {
            FeeType.RIGID: "刚性年费",
            FeeType.TRANSACTION_COUNT: "刷卡次数减免",
            FeeType.TRANSACTION_AMOUNT: "刷卡金额减免",
            FeeType.POINTS_EXCHANGE: "积分兑换减免"
        }
        return type_display.get(self.fee_type, "未知类型")


class AnnualFeeRecordBase(BaseModel):
    """年费记录基础模型"""
    card_id: UUID = Field(
        ..., 
        description="信用卡ID",
        json_schema_extra={"example": "f47ac10b-58cc-4372-a567-0e02b2c3d479"}
    )
    fee_year: int = Field(
        ..., 
        description="年费所属年份",
        json_schema_extra={"example": 2024}
    )
    due_date: date = Field(
        ..., 
        description="年费到期日期",
        json_schema_extra={"example": "2024-12-31"}
    )
    fee_amount: Decimal = Field(
        ..., 
        description="应付年费金额", 
        ge=0,
        json_schema_extra={"example": 200.00}
    )
    waiver_status: WaiverStatus = Field(
        WaiverStatus.PENDING, 
        description="减免状态",
        json_schema_extra={"example": WaiverStatus.PENDING}
    )
    waiver_condition_met: bool = Field(
        False, 
        description="是否满足减免条件",
        json_schema_extra={"example": False}
    )
    current_progress: Decimal = Field(
        0, 
        description="当前进度", 
        ge=0,
        json_schema_extra={"example": 8}
    )
    payment_date: Optional[date] = Field(
        None, 
        description="实际支付日期",
        json_schema_extra={"example": "2024-01-15"}
    )
    notes: Optional[str] = Field(
        None, 
        description="备注",
        json_schema_extra={"example": "自动生成的年费记录"}
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

    model_config = ConfigDict(from_attributes=True)


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