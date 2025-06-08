from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

# 导入年费相关模型
from .annual_fee import FeeType, AnnualFeeRule, AnnualFeeRuleCreate


class CardType(str, Enum):
    """
    信用卡组织类型枚举
    
    定义不同的卡组织类型：
    - VISA: Visa卡组织
    - MASTERCARD: 万事达卡组织  
    - UNIONPAY: 银联卡组织
    - AMEX: 美国运通卡组织
    - JCB: JCB卡组织
    - DISCOVER: Discover卡组织
    - DINERS: 大来卡组织
    """
    VISA = "visa"           # Visa
    MASTERCARD = "mastercard"  # 万事达
    UNIONPAY = "unionpay"      # 银联
    AMEX = "amex"             # 美国运通
    JCB = "jcb"              # JCB
    DISCOVER = "discover"     # Discover
    DINERS = "diners"        # 大来卡


class CardStatus(str, Enum):
    """
    信用卡状态枚举
    
    定义信用卡的不同状态：
    - ACTIVE: 激活状态，正常使用中
    - INACTIVE: 未激活，新卡待激活
    - FROZEN: 冻结状态，暂时停用
    - CANCELLED: 已销卡，永久停用
    """
    ACTIVE = "active"      # 激活
    INACTIVE = "inactive"  # 未激活
    FROZEN = "frozen"      # 冻结
    CANCELLED = "cancelled"  # 已销卡


class CardBase(BaseModel):
    """
    信用卡基础模型
    
    定义信用卡的基础字段，包括银行信息、卡片信息、额度等。
    所有信用卡相关的模型都继承此基础模型。
    """
    bank_name: str = Field(
        ..., 
        min_length=2, 
        max_length=50,
        description="银行名称，如：招商银行、中国工商银行",
        example="招商银行"
    )
    
    card_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="信用卡名称，如：招行经典白金卡、工行环球旅行卡",
        example="招行经典白金卡"
    )
    
    card_number: str = Field(
        ..., 
        min_length=13, 
        max_length=19,
        description="信用卡号，支持13-19位数字",
        example="6225882888888888"
    )
    
    card_type: CardType = Field(
        ...,
        description="信用卡组织类型",
        example=CardType.VISA
    )
    
    credit_limit: Decimal = Field(
        ..., 
        ge=0, 
        le=9999999.99,
        description="信用额度，单位：元",
        example=50000.00
    )
    
    used_amount: Decimal = Field(
        0, 
        ge=0,
        description="已使用额度，单位：元",
        example=3500.50
    )
    
    available_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="可用额度，自动计算得出",
        example=46499.50
    )
    
    billing_day: int = Field(
        ..., 
        ge=1, 
        le=31,
        description="账单日，每月的哪一天生成账单",
        example=5
    )
    
    due_day: int = Field(
        ..., 
        ge=1, 
        le=31,
        description="还款日，每月的还款截止日期",
        example=25
    )
    
    expiry_month: int = Field(
        ..., 
        ge=1, 
        le=12,
        description="卡片有效期月份，1-12",
        example=10
    )
    
    expiry_year: int = Field(
        ..., 
        ge=2024, 
        le=2050,
        description="卡片有效期年份，如2024",
        example=2027
    )
    
    annual_fee_rule_id: Optional[UUID] = Field(
        None,
        description="年费规则ID，关联年费规则表"
    )
    
    card_color: str = Field(
        "#1890ff",
        max_length=20,
        description="卡片颜色，用于前端显示",
        example="#1890ff"
    )
    
    status: CardStatus = Field(
        CardStatus.INACTIVE,
        description="卡片状态",
        example=CardStatus.ACTIVE
    )
    
    is_active: bool = Field(
        True,
        description="是否启用此卡片",
        example=True
    )
    
    activation_date: Optional[date] = Field(
        None,
        description="激活日期",
        example="2024-01-15"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="备注信息",
        example="主要用于日常消费，享受餐饮优惠"
    )

    @validator('card_number')
    def validate_card_number(cls, v):
        """验证信用卡号格式"""
        if not v.isdigit():
            raise ValueError('信用卡号只能包含数字')
        return v

    @validator('expiry_year')
    def validate_expiry_not_past(cls, v, values):
        """验证有效期不能是过去的时间"""
        expiry_month = values.get('expiry_month')
        if expiry_month:
            today = date.today()
            # 如果是当前年份，月份不能早于当前月份
            if v == today.year and expiry_month < today.month:
                raise ValueError('卡片有效期不能是过去的时间')
            # 年份不能早于当前年份
            elif v < today.year:
                raise ValueError('卡片有效期不能是过去的时间')
        return v

    @validator('due_day')
    def validate_due_day_after_billing_day(cls, v, values):
        """验证还款日应在账单日之后"""
        billing_day = values.get('billing_day')
        if billing_day and v <= billing_day:
            raise ValueError('还款日应在账单日之后')
        return v


class CardWithAnnualFeeCreate(CardBase):
    """
    创建信用卡请求模型（集成年费信息）
    
    用于接收创建新信用卡的请求数据，支持同时创建年费规则。
    如果提供了年费信息，将自动创建对应的年费规则。
    """
    # 年费规则相关字段（可选）
    annual_fee_enabled: bool = Field(
        False,
        description="是否启用年费管理",
        example=True
    )
    
    fee_type: Optional[FeeType] = Field(
        None, 
        description="年费类型，启用年费管理时必填",
        example=FeeType.TRANSACTION_COUNT
    )
    
    base_fee: Optional[Decimal] = Field(
        None, 
        description="基础年费金额，启用年费管理时必填", 
        ge=0,
        example=200.00
    )
    
    waiver_condition_value: Optional[Decimal] = Field(
        None, 
        description="减免条件数值，如刷卡次数12或消费金额50000",
        example=12
    )
    
    points_per_yuan: Optional[Decimal] = Field(
        None, 
        description="积分兑换比例：1元对应的积分数，如1元=0.1积分。仅当fee_type为points_exchange时有效",
        example=0.1,
        ge=0
    )
    
    annual_fee_month: Optional[int] = Field(
        None, 
        description="年费扣除月份，1-12月。如每年2月扣费则填2",
        example=2,
        ge=1,
        le=12
    )
    
    annual_fee_day: Optional[int] = Field(
        None, 
        description="年费扣除日期，1-31日。如每年2月18日扣费则填18",
        example=18,
        ge=1,
        le=31
    )
    
    fee_description: Optional[str] = Field(
        None, 
        description="年费规则描述，详细说明减免条件",
        example="年内刷卡满12次可减免年费，每年2月18日扣除"
    )

    @validator('points_per_yuan')  
    def validate_annual_fee_required_fields(cls, v, values):
        """验证启用年费管理时的必填字段"""
        annual_fee_enabled = values.get('annual_fee_enabled', False)
        
        if annual_fee_enabled:
            fee_type = values.get('fee_type')
            base_fee = values.get('base_fee')
            
            if not fee_type:
                raise ValueError('启用年费管理时，年费类型为必填字段')
                
            if not base_fee or base_fee <= 0:
                raise ValueError('启用年费管理时，基础年费金额必须大于0')
                
            # 积分兑换类型必须提供积分比例
            if fee_type == FeeType.POINTS_EXCHANGE:
                if not v or v <= 0:
                    raise ValueError('积分兑换类型的年费规则必须设置积分兑换比例')
        
        return v


class CardCreate(CardBase):
    """
    创建信用卡请求模型（基础版本）
    
    用于接收创建新信用卡的请求数据，继承基础模型的所有字段。
    不包含年费管理功能，保持向后兼容。
    """
    pass


class CardUpdate(BaseModel):
    """
    更新信用卡请求模型
    
    用于接收更新信用卡的请求数据，所有字段均为可选，
    只更新提供的字段，未提供的字段保持原值不变。
    """
    bank_name: Optional[str] = Field(None, min_length=2, max_length=50, description="银行名称")
    card_name: Optional[str] = Field(None, min_length=2, max_length=100, description="信用卡名称")
    card_type: Optional[CardType] = Field(None, description="信用卡组织类型")
    credit_limit: Optional[Decimal] = Field(None, ge=0, le=9999999.99, description="信用额度")
    used_amount: Optional[Decimal] = Field(None, ge=0, description="已使用额度")
    billing_day: Optional[int] = Field(None, ge=1, le=31, description="账单日")
    due_day: Optional[int] = Field(None, ge=1, le=31, description="还款日")
    expiry_month: Optional[int] = Field(None, ge=1, le=12, description="卡片有效期月份")
    expiry_year: Optional[int] = Field(None, ge=2024, le=2050, description="卡片有效期年份")
    annual_fee_rule_id: Optional[UUID] = Field(None, description="年费规则ID")
    card_color: Optional[str] = Field(None, max_length=20, description="卡片颜色")
    status: Optional[CardStatus] = Field(None, description="卡片状态")
    is_active: Optional[bool] = Field(None, description="是否启用此卡片")
    activation_date: Optional[date] = Field(None, description="激活日期")
    notes: Optional[str] = Field(None, max_length=500, description="备注信息")


class CardWithAnnualFeeUpdate(CardUpdate):
    """
    更新信用卡请求模型（集成年费信息）
    
    支持同时更新信用卡基本信息和年费规则。
    """
    # 年费规则更新字段
    annual_fee_enabled: Optional[bool] = Field(
        None,
        description="是否启用年费管理。设为False将删除现有年费规则"
    )
    
    fee_type: Optional[FeeType] = Field(
        None, 
        description="年费类型"
    )
    
    base_fee: Optional[Decimal] = Field(
        None, 
        description="基础年费金额", 
        ge=0
    )
    
    waiver_condition_value: Optional[Decimal] = Field(
        None, 
        description="减免条件数值"
    )
    
    points_per_yuan: Optional[Decimal] = Field(
        None, 
        description="积分兑换比例",
        ge=0
    )
    
    annual_fee_month: Optional[int] = Field(
        None, 
        description="年费扣除月份", 
        ge=1, 
        le=12
    )
    
    annual_fee_day: Optional[int] = Field(
        None, 
        description="年费扣除日期", 
        ge=1, 
        le=31
    )
    
    fee_description: Optional[str] = Field(
        None, 
        description="年费规则描述"
    )


class Card(CardBase):
    """
    信用卡响应模型
    
    用于返回信用卡数据，包含完整的卡片信息和系统生成的字段。
    """
    id: UUID = Field(..., description="信用卡ID，系统自动生成的唯一标识")
    user_id: UUID = Field(..., description="用户ID，卡片所属用户")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    @property
    def expiry_display(self) -> str:
        """获取有效期的显示格式，如 '10/27'"""
        return f"{self.expiry_month:02d}/{str(self.expiry_year)[-2:]}"
    
    @property
    def is_expired(self) -> bool:
        """检查卡片是否已过期"""
        today = date.today()
        if self.expiry_year < today.year:
            return True
        elif self.expiry_year == today.year and self.expiry_month < today.month:
            return True
        return False
    
    def expires_soon(self, months_ahead: int = 3) -> bool:
        """检查卡片是否即将过期（默认3个月内）"""
        from datetime import timedelta
        today = date.today()
        check_date = today + timedelta(days=months_ahead * 30)  # 近似计算
        
        if self.expiry_year < check_date.year:
            return True
        elif self.expiry_year == check_date.year and self.expiry_month <= check_date.month:
            return True
        return False

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class CardWithAnnualFee(Card):
    """
    信用卡响应模型（包含年费信息）
    
    用于返回包含年费规则信息的完整信用卡数据。
    """
    annual_fee_rule: Optional[AnnualFeeRule] = Field(
        None,
        description="年费规则信息，如果卡片设置了年费规则则包含完整信息"
    )
    
    # 年费便捷信息字段
    has_annual_fee: bool = Field(
        ...,
        description="是否设置了年费规则"
    )
    
    current_year_fee_status: Optional[str] = Field(
        None,
        description="当前年份年费状态：pending/waived/paid/overdue"
    )
    
    next_fee_due_date: Optional[date] = Field(
        None,
        description="下一次年费到期日期"
    )

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class CardSummary(BaseModel):
    """
    信用卡摘要信息模型
    
    用于列表显示时的简化信息，包含核心字段。
    """
    id: UUID = Field(..., description="信用卡ID")
    bank_name: str = Field(..., description="银行名称")
    card_name: str = Field(..., description="信用卡名称")
    card_type: CardType = Field(..., description="信用卡组织类型")
    credit_limit: Decimal = Field(..., description="信用额度")
    used_amount: Decimal = Field(..., description="已使用额度")
    available_amount: Decimal = Field(..., description="可用额度")
    status: CardStatus = Field(..., description="卡片状态")
    card_color: str = Field(..., description="卡片颜色")

    class Config:
        from_attributes = True


class CardSummaryWithAnnualFee(CardSummary):
    """
    信用卡摘要信息模型（包含年费信息）
    
    用于列表显示时的简化信息，包含年费相关的关键字段。
    """
    has_annual_fee: bool = Field(..., description="是否设置了年费规则")
    annual_fee_amount: Optional[Decimal] = Field(None, description="年费金额")
    fee_type_display: Optional[str] = Field(None, description="年费类型显示名称")
    current_year_fee_status: Optional[str] = Field(None, description="当前年费状态")

    class Config:
        from_attributes = True 