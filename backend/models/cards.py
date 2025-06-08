from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


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
    
    expiry_date: date = Field(
        ...,
        description="卡片有效期",
        example="2027-12-31"
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

    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        """验证有效期不能是过去的日期"""
        if v < date.today():
            raise ValueError('卡片有效期不能是过去的日期')
        return v

    @validator('due_day')
    def validate_due_day_after_billing_day(cls, v, values):
        """验证还款日应在账单日之后"""
        billing_day = values.get('billing_day')
        if billing_day and v <= billing_day:
            raise ValueError('还款日应在账单日之后')
        return v


class CardCreate(CardBase):
    """
    创建信用卡请求模型
    
    用于接收创建新信用卡的请求数据，继承基础模型的所有字段。
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
    expiry_date: Optional[date] = Field(None, description="卡片有效期")
    annual_fee_rule_id: Optional[UUID] = Field(None, description="年费规则ID")
    card_color: Optional[str] = Field(None, max_length=20, description="卡片颜色")
    status: Optional[CardStatus] = Field(None, description="卡片状态")
    is_active: Optional[bool] = Field(None, description="是否启用此卡片")
    activation_date: Optional[date] = Field(None, description="激活日期")
    notes: Optional[str] = Field(None, max_length=500, description="备注信息")


class Card(CardBase):
    """
    信用卡响应模型
    
    用于返回信用卡数据，包含完整的卡片信息和系统生成的字段。
    """
    id: UUID = Field(..., description="信用卡ID，系统自动生成的唯一标识")
    user_id: UUID = Field(..., description="用户ID，卡片所属用户")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
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