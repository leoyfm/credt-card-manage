"""
信用卡管理模块Pydantic模型

包含信用卡和银行相关的请求响应模型定义
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_serializer, ConfigDict
from uuid import UUID

from app.models.schemas.common import PaginationInfo, PaginationParams


# ============ 银行相关模型 ============

class BankBase(BaseModel):
    """银行基础模型"""
    bank_code: str = Field(..., max_length=20, description="银行代码", json_schema_extra={"example": "CMB"})
    bank_name: str = Field(..., max_length=100, description="银行名称", json_schema_extra={"example": "招商银行"})
    bank_logo: Optional[str] = Field(None, max_length=500, description="银行logo", json_schema_extra={"example": "https://example.com/cmb-logo.png"})
    is_active: bool = Field(True, description="是否激活", json_schema_extra={"example": True})
    sort_order: int = Field(0, description="排序", json_schema_extra={"example": 1})


class BankCreate(BankBase):
    """创建银行请求模型"""
    pass


class BankUpdate(BaseModel):
    """更新银行请求模型"""
    bank_name: Optional[str] = Field(None, max_length=100, description="银行名称", json_schema_extra={"example": "招商银行"})
    bank_logo: Optional[str] = Field(None, max_length=500, description="银行logo")
    is_active: Optional[bool] = Field(None, description="是否激活")
    sort_order: Optional[int] = Field(None, description="排序")


class BankResponse(BankBase):
    """银行响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="银行ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    @model_serializer
    def serialize_model(self) -> dict:
        """自定义序列化器，处理Decimal类型"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Decimal):
                data[field_name] = float(field_value) if field_value is not None else None
            else:
                data[field_name] = field_value
        return data


# ============ 信用卡相关模型 ============

class CreditCardBase(BaseModel):
    """信用卡基础模型"""
    card_name: str = Field(..., max_length=100, description="卡片名称", json_schema_extra={"example": "招商银行信用卡"})
    card_number: str = Field(..., max_length=100, description="卡号后4位", json_schema_extra={"example": "1234"})
    card_type: str = Field("credit", max_length=20, description="卡片类型", json_schema_extra={"example": "credit"})
    card_network: Optional[str] = Field(None, max_length=20, description="卡组织", json_schema_extra={"example": "VISA"})
    card_level: Optional[str] = Field(None, max_length=20, description="卡片等级", json_schema_extra={"example": "白金卡"})
    bank_color: str = Field("#EF4444", max_length=20, description="卡片颜色", json_schema_extra={"example": "#EF4444"})
    credit_limit: Decimal = Field(..., ge=0, description="信用额度", json_schema_extra={"example": 50000.00})
    expiry_month: int = Field(..., ge=1, le=12, description="有效期月份", json_schema_extra={"example": 12})
    expiry_year: int = Field(..., ge=2024, description="有效期年份", json_schema_extra={"example": 2027})
    billing_date: Optional[int] = Field(None, ge=1, le=31, description="账单日", json_schema_extra={"example": 5})
    due_date: Optional[int] = Field(None, ge=1, le=31, description="还款日", json_schema_extra={"example": 25})
    annual_fee: Decimal = Field(Decimal("0"), ge=0, description="年费金额", json_schema_extra={"example": 300.00})
    fee_waivable: bool = Field(False, description="年费是否可减免", json_schema_extra={"example": True})
    fee_auto_deduct: bool = Field(False, description="是否自动扣费", json_schema_extra={"example": False})
    fee_due_month: Optional[int] = Field(None, ge=1, le=12, description="年费到期月份", json_schema_extra={"example": 12})
    features: List[str] = Field(default_factory=list, description="特色功能", json_schema_extra={"example": ["积分兑换", "免费洗车"]})
    points_rate: Decimal = Field(Decimal("1.00"), ge=0, description="积分倍率", json_schema_extra={"example": 1.50})
    cashback_rate: Decimal = Field(Decimal("0.00"), ge=0, le=100, description="返现比例", json_schema_extra={"example": 1.00})
    is_primary: bool = Field(False, description="是否主卡", json_schema_extra={"example": False})
    notes: Optional[str] = Field(None, description="备注", json_schema_extra={"example": "主要用于日常消费"})

    @field_validator('expiry_year')
    @classmethod
    def validate_expiry_year(cls, v):
        """验证有效期年份不能是过去的年份"""
        from datetime import datetime
        current_year = datetime.now().year
        if v < current_year:
            raise ValueError('有效期年份不能是过去的年份')
        return v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v, info):
        """验证还款日的合理性"""
        if v is not None:
            # 只需要确保还款日在合理范围内（1-31）
            # 允许跨月还款（还款日可以小于账单日）
            if not (1 <= v <= 31):
                raise ValueError('还款日必须在1-31之间')
        return v

    @field_validator('credit_limit', 'annual_fee', 'points_rate', 'cashback_rate')
    @classmethod
    def validate_decimal_fields(cls, v):
        """自动转换数值类型为Decimal，避免序列化警告"""
        if v is None:
            return v
        return Decimal(str(v))


class CreditCardCreate(CreditCardBase):
    """创建信用卡请求模型"""
    bank_id: Optional[UUID] = Field(None, description="银行ID")
    bank_name: Optional[str] = Field(None, max_length=100, description="银行名称（如果不提供bank_id）", json_schema_extra={"example": "招商银行"})


class CreditCardUpdate(BaseModel):
    """更新信用卡请求模型"""
    card_name: Optional[str] = Field(None, max_length=100, description="卡片名称")
    card_type: Optional[str] = Field(None, max_length=20, description="卡片类型")
    card_network: Optional[str] = Field(None, max_length=20, description="卡组织")
    card_level: Optional[str] = Field(None, max_length=20, description="卡片等级")
    bank_color: Optional[str] = Field(None, max_length=20, description="卡片颜色", json_schema_extra={"example": "#EF4444"})
    credit_limit: Optional[Decimal] = Field(None, ge=0, description="信用额度")
    available_limit: Optional[Decimal] = Field(None, ge=0, description="可用额度")
    used_limit: Optional[Decimal] = Field(None, ge=0, description="已用额度")
    expiry_month: Optional[int] = Field(None, ge=1, le=12, description="有效期月份")
    expiry_year: Optional[int] = Field(None, ge=2024, description="有效期年份")
    billing_date: Optional[int] = Field(None, ge=1, le=31, description="账单日")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="还款日")
    annual_fee: Optional[Decimal] = Field(None, ge=0, description="年费金额")
    fee_waivable: Optional[bool] = Field(None, description="年费是否可减免")
    fee_auto_deduct: Optional[bool] = Field(None, description="是否自动扣费")
    fee_due_month: Optional[int] = Field(None, ge=1, le=12, description="年费到期月份")
    features: Optional[List[str]] = Field(None, description="特色功能")
    points_rate: Optional[Decimal] = Field(None, ge=0, description="积分倍率")
    cashback_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="返现比例")
    status: Optional[str] = Field(None, description="状态", json_schema_extra={"example": "active"})
    is_primary: Optional[bool] = Field(None, description="是否主卡")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator('credit_limit', 'available_limit', 'used_limit', 'annual_fee', 'points_rate', 'cashback_rate')
    @classmethod
    def validate_decimal_fields(cls, v):
        """自动转换数值类型为Decimal，避免序列化警告"""
        if v is None:
            return v
        return Decimal(str(v))


class CreditCardStatusUpdate(BaseModel):
    """信用卡状态更新模型"""
    status: str = Field(..., description="状态", json_schema_extra={"example": "active"})
    reason: Optional[str] = Field(None, description="状态变更原因", json_schema_extra={"example": "用户申请冻结"})

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """验证状态值"""
        valid_statuses = ['active', 'frozen', 'closed']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v


class CreditCardResponse(BaseModel):
    """信用卡响应模型"""
    id: UUID = Field(..., description="信用卡ID")
    user_id: UUID = Field(..., description="用户ID")
    bank_id: Optional[UUID] = Field(None, description="银行ID")
    card_name: str = Field(..., max_length=100, description="卡片名称", json_schema_extra={"example": "招商银行信用卡"})
    card_number: str = Field(..., max_length=100, description="卡号后4位", json_schema_extra={"example": "1234"})
    card_type: str = Field("credit", max_length=20, description="卡片类型", json_schema_extra={"example": "credit"})
    card_network: Optional[str] = Field(None, max_length=20, description="卡组织", json_schema_extra={"example": "VISA"})
    card_level: Optional[str] = Field(None, max_length=20, description="卡片等级", json_schema_extra={"example": "白金卡"})
    bank_color: str = Field("#EF4444", max_length=20, description="卡片颜色", json_schema_extra={"example": "#EF4444"})
    credit_limit: Decimal = Field(..., ge=0, description="信用额度", json_schema_extra={"example": 50000.00})
    available_limit: Optional[Decimal] = Field(None, description="可用额度", json_schema_extra={"example": 45000.00})
    used_limit: Decimal = Field(Decimal("0"), description="已用额度", json_schema_extra={"example": 5000.00})
    expiry_month: int = Field(..., ge=1, le=12, description="有效期月份", json_schema_extra={"example": 12})
    expiry_year: int = Field(..., description="有效期年份（响应模型不验证过期）", json_schema_extra={"example": 2027})
    billing_date: Optional[int] = Field(None, ge=1, le=31, description="账单日", json_schema_extra={"example": 5})
    due_date: Optional[int] = Field(None, ge=1, le=31, description="还款日", json_schema_extra={"example": 25})
    annual_fee: Decimal = Field(Decimal("0"), ge=0, description="年费金额", json_schema_extra={"example": 300.00})
    fee_waivable: bool = Field(False, description="年费是否可减免", json_schema_extra={"example": True})
    fee_auto_deduct: bool = Field(False, description="是否自动扣费", json_schema_extra={"example": False})
    fee_due_month: Optional[int] = Field(None, ge=1, le=12, description="年费到期月份", json_schema_extra={"example": 12})
    features: List[str] = Field(default_factory=list, description="特色功能", json_schema_extra={"example": ["积分兑换", "免费洗车"]})
    points_rate: Decimal = Field(Decimal("1.00"), ge=0, description="积分倍率", json_schema_extra={"example": 1.50})
    cashback_rate: Decimal = Field(Decimal("0.00"), ge=0, le=100, description="返现比例", json_schema_extra={"example": 1.00})
    status: str = Field("active", description="状态", json_schema_extra={"example": "active"})
    is_primary: bool = Field(False, description="是否主卡", json_schema_extra={"example": False})
    notes: Optional[str] = Field(None, description="备注", json_schema_extra={"example": "主要用于日常消费"})
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 关联数据
    bank: Optional[BankResponse] = Field(None, description="银行信息")
    
    # 计算属性
    expiry_display: Optional[str] = Field(None, description="有效期显示", json_schema_extra={"example": "12/27"})
    is_expired: Optional[bool] = Field(None, description="是否已过期", json_schema_extra={"example": False})
    credit_utilization_rate: Optional[float] = Field(None, description="信用额度使用率", json_schema_extra={"example": 10.0})

    @field_validator('credit_limit', 'available_limit', 'used_limit', 'annual_fee', 'points_rate', 'cashback_rate')
    @classmethod
    def validate_decimal_fields(cls, v):
        """自动转换数值类型为Decimal，避免序列化警告"""
        if v is None:
            return v
        return Decimal(str(v))

    @model_serializer
    def serialize_model(self) -> dict:
        """自定义序列化器，处理Decimal类型"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Decimal):
                data[field_name] = float(field_value) if field_value is not None else None
            else:
                data[field_name] = field_value
        return data

    model_config = ConfigDict(from_attributes=True)


class CreditCardListResponse(BaseModel):
    """信用卡列表响应模型"""
    items: List[CreditCardResponse] = Field(..., description="信用卡列表")
    pagination: PaginationInfo = Field(..., description="分页信息")


class CreditCardSummary(BaseModel):
    """信用卡摘要信息"""
    total_cards: int = Field(..., description="信用卡总数", json_schema_extra={"example": 5})
    active_cards: int = Field(..., description="激活卡片数", json_schema_extra={"example": 4})
    total_credit_limit: Decimal = Field(..., description="总信用额度", json_schema_extra={"example": 250000.00})
    total_used_limit: Decimal = Field(..., description="总已用额度", json_schema_extra={"example": 25000.00})
    total_available_limit: Decimal = Field(..., description="总可用额度", json_schema_extra={"example": 225000.00})
    average_utilization_rate: float = Field(..., description="平均使用率", json_schema_extra={"example": 10.0})
    cards_expiring_soon: int = Field(..., description="即将过期卡片数", json_schema_extra={"example": 1})
    max_interest_free_days: int = Field(..., description="最长免息天数", json_schema_extra={"example": 56})

    @field_validator('total_credit_limit', 'total_used_limit', 'total_available_limit')
    @classmethod
    def validate_decimal_fields(cls, v):
        """自动转换数值类型为Decimal，避免序列化警告"""
        if v is None:
            return v
        return Decimal(str(v))


# ============ 查询参数模型 ============

class CreditCardQueryParams(PaginationParams):
    """信用卡查询参数"""
    keyword: str = Field("", description="搜索关键词，支持卡片名称、银行名称模糊搜索", json_schema_extra={"example": "招商"})
    status: Optional[str] = Field(None, description="状态筛选", json_schema_extra={"example": "active"})
    bank_id: Optional[UUID] = Field(None, description="银行ID筛选")
    card_type: Optional[str] = Field(None, description="卡片类型筛选", json_schema_extra={"example": "credit"})
    is_primary: Optional[bool] = Field(None, description="是否主卡筛选", json_schema_extra={"example": True})
    expiring_soon: Optional[bool] = Field(None, description="是否即将过期", json_schema_extra={"example": False})


# ============ 批量操作模型 ============

class CreditCardBatchUpdate(BaseModel):
    """信用卡批量更新模型"""
    card_ids: List[UUID] = Field(..., description="信用卡ID列表")
    update_data: CreditCardUpdate = Field(..., description="更新数据")


class CreditCardBatchStatusUpdate(BaseModel):
    """信用卡批量状态更新模型"""
    card_ids: List[UUID] = Field(..., description="信用卡ID列表")
    status: str = Field(..., description="新状态")
    reason: Optional[str] = Field(None, description="状态变更原因")


class CreditCardBatchResponse(BaseModel):
    """批量操作响应模型"""
    success_count: int = Field(..., description="成功数量", json_schema_extra={"example": 3})
    failed_count: int = Field(..., description="失败数量", json_schema_extra={"example": 1})
    success_ids: List[UUID] = Field(..., description="成功的ID列表")
    failed_items: List[Dict[str, Any]] = Field(..., description="失败的项目详情")


# ============ 统计模型 ============

class CreditCardStatistics(BaseModel):
    """信用卡统计模型"""
    summary: CreditCardSummary = Field(..., description="摘要信息")
    by_bank: List[Dict[str, Any]] = Field(..., description="按银行统计")
    by_status: List[Dict[str, Any]] = Field(..., description="按状态统计")
    by_card_level: List[Dict[str, Any]] = Field(..., description="按卡片等级统计")
    utilization_distribution: List[Dict[str, Any]] = Field(..., description="使用率分布") 