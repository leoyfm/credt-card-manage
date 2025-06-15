"""
年费管理相关的Pydantic模型
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


# ========== 年费减免规则模型 ==========

class FeeWaiverRuleBase(BaseModel):
    """年费减免规则基础模型"""
    rule_group_id: Optional[UUID] = Field(None, description="规则组ID")
    rule_name: str = Field(..., max_length=100, description="规则名称")
    condition_type: str = Field(..., description="条件类型: spending_amount, transaction_count, points_redeem, specific_category")
    condition_value: Optional[Decimal] = Field(None, description="条件数值")
    condition_count: Optional[int] = Field(None, description="条件次数")
    condition_period: Optional[str] = Field(None, description="统计周期: monthly, quarterly, yearly")
    logical_operator: Optional[str] = Field(None, description="逻辑操作符: AND, OR")
    priority: Optional[int] = Field(None, description="优先级")
    is_enabled: bool = Field(True, description="是否启用")
    effective_from: Optional[date] = Field(None, description="生效日期")
    effective_to: Optional[date] = Field(None, description="失效日期")
    description: Optional[str] = Field(None, max_length=500, description="规则说明")

    model_config = ConfigDict(
        from_attributes=True,
    )

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器，处理 Decimal、datetime 和 date 类型"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Decimal):
                data[field_name] = float(field_value) if field_value is not None else None
            elif isinstance(field_value, datetime):
                data[field_name] = field_value.isoformat() if field_value is not None else None
            elif isinstance(field_value, date):
                data[field_name] = field_value.isoformat() if field_value is not None else None
            else:
                data[field_name] = field_value
        return data

    @field_validator('condition_value')
    @classmethod
    def validate_condition_value(cls, v):
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class FeeWaiverRuleCreate(FeeWaiverRuleBase):
    """创建年费减免规则请求模型"""
    card_id: UUID = Field(..., description="信用卡ID")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "card_id": "123e4567-e89b-12d3-a456-426614174000",
                "rule_group_id": "123e4567-e89b-12d3-a456-426614174000",
                "rule_name": "年消费满5万免年费",
                "condition_type": "spending_amount",
                "condition_value": 50000.00,
                "condition_count": None,
                "condition_period": None,
                "logical_operator": None,
                "priority": None,
                "is_enabled": True,
                "effective_from": "2024-01-01",
                "effective_to": "2024-12-31",
                "description": "年消费满5万免年费"
            }
        }
    )


class FeeWaiverRuleUpdate(BaseModel):
    """更新年费减免规则请求模型"""
    rule_name: Optional[str] = Field(None, max_length=100, description="规则名称")
    condition_type: Optional[str] = Field(None, description="条件类型")
    condition_value: Optional[Decimal] = Field(None, description="条件数值")
    condition_count: Optional[int] = Field(None, description="条件次数")
    condition_period: Optional[str] = Field(None, description="统计周期")
    logical_operator: Optional[str] = Field(None, description="逻辑操作符")
    priority: Optional[int] = Field(None, description="优先级")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    effective_from: Optional[date] = Field(None, description="生效日期")
    effective_to: Optional[date] = Field(None, description="失效日期")
    description: Optional[str] = Field(None, max_length=500, description="规则说明")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "rule_name": "年消费满6万免年费",
                "condition_type": "spending_amount",
                "condition_value": 60000.00,
                "is_enabled": True,
                "description": "调整为年消费满6万免年费"
            }
        }
    )

    @field_validator('condition_value')
    @classmethod
    def validate_condition_value(cls, v):
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class FeeWaiverRuleResponse(FeeWaiverRuleBase):
    """年费减免规则响应模型"""
    id: UUID = Field(..., description="规则ID")
    card_id: UUID = Field(..., description="信用卡ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "card_id": "123e4567-e89b-12d3-a456-426614174001",
                "rule_group_id": "123e4567-e89b-12d3-a456-426614174001",
                "rule_name": "年消费满5万免年费",
                "condition_type": "spending_amount",
                "condition_value": 50000.00,
                "condition_count": None,
                "condition_period": None,
                "logical_operator": None,
                "priority": None,
                "is_enabled": True,
                "effective_from": "2024-01-01",
                "effective_to": "2024-12-31",
                "description": "年消费满5万免年费",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
    )


# ========== 年费记录模型 ==========

class AnnualFeeRecordBase(BaseModel):
    """年费记录基础模型"""
    waiver_rule_id: Optional[UUID] = Field(None, description="年费规则ID")
    fee_year: int = Field(..., ge=2020, le=2050, description="年费年份")
    base_fee: Decimal = Field(..., ge=0, description="基础年费")
    actual_fee: Decimal = Field(..., ge=0, description="实际年费")
    waiver_amount: Optional[Decimal] = Field(Decimal("0"), description="减免金额")
    waiver_reason: Optional[str] = Field(None, max_length=200, description="减免原因")
    status: str = Field("pending", description="状态: pending, paid, waived, overdue")
    due_date: Optional[date] = Field(None, description="应缴日期")
    paid_date: Optional[date] = Field(None, description="实际缴费日期")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

    model_config = ConfigDict(
        from_attributes=True,
    )

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """自定义序列化器，处理 Decimal、datetime 和 date 类型"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Decimal):
                data[field_name] = float(field_value) if field_value is not None else None
            elif isinstance(field_value, datetime):
                data[field_name] = field_value.isoformat() if field_value is not None else None
            elif isinstance(field_value, date):
                data[field_name] = field_value.isoformat() if field_value is not None else None
            else:
                data[field_name] = field_value
        return data

    @field_validator('base_fee', 'actual_fee', 'waiver_amount')
    @classmethod
    def validate_decimal_fields(cls, v):
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'paid', 'waived', 'overdue']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是: {", ".join(allowed_statuses)}')
        return v


class AnnualFeeRecordCreate(AnnualFeeRecordBase):
    """创建年费记录请求模型"""
    card_id: Optional[UUID] = Field(None, description="信用卡ID（当没有waiver_rule_id时必需）")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "waiver_rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "card_id": "123e4567-e89b-12d3-a456-426614174001",
                "fee_year": 2024,
                "base_fee": 300.00,
                "actual_fee": 0.00,
                "waiver_amount": 300.00,
                "waiver_reason": "年消费满5万，符合减免条件",
                "status": "waived",
                "due_date": "2024-12-31",
                "notes": "自动减免"
            }
        }
    )


class AnnualFeeRecordUpdate(BaseModel):
    """更新年费记录请求模型"""
    actual_fee: Optional[Decimal] = Field(None, ge=0, description="实际年费")
    waiver_amount: Optional[Decimal] = Field(None, description="减免金额")
    waiver_reason: Optional[str] = Field(None, max_length=200, description="减免原因")
    status: Optional[str] = Field(None, description="状态")
    due_date: Optional[date] = Field(None, description="应缴日期")
    paid_date: Optional[date] = Field(None, description="实际缴费日期")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "actual_fee": 300.00,
                "status": "paid",
                "paid_date": "2024-01-15",
                "notes": "已缴费"
            }
        }
    )

    @field_validator('actual_fee', 'waiver_amount')
    @classmethod
    def validate_decimal_fields(cls, v):
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class AnnualFeeRecordResponse(AnnualFeeRecordBase):
    """年费记录响应模型"""
    id: UUID = Field(..., description="记录ID")
    card_id: UUID = Field(..., description="信用卡ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 关联数据
    card_name: Optional[str] = Field(None, description="信用卡名称")
    waiver_type: Optional[str] = Field(None, description="减免类型")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "card_id": "123e4567-e89b-12d3-a456-426614174001",
                "waiver_rule_id": "123e4567-e89b-12d3-a456-426614174001",
                "fee_year": 2024,
                "base_fee": 300.00,
                "actual_fee": 0.00,
                "waiver_amount": 300.00,
                "waiver_reason": "年消费满5万，符合减免条件",
                "status": "waived",
                "due_date": "2024-12-31",
                "paid_date": None,
                "notes": "自动减免",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "card_name": "招商银行经典白金卡",
                "waiver_type": "spending_amount"
            }
        }
    )


# ========== 减免评估模型 ==========

class WaiverEvaluationResponse(BaseModel):
    """年费减免评估响应模型"""
    waiver_rule_id: UUID = Field(..., description="规则ID")
    waiver_type: str = Field(..., description="减免类型")
    is_eligible: bool = Field(..., description="是否符合减免条件")
    current_progress: float = Field(..., description="当前进度")
    required_target: float = Field(..., description="目标要求")
    completion_percentage: float = Field(..., description="完成百分比")
    estimated_waiver_amount: Decimal = Field(..., description="预计减免金额")
    evaluation_message: str = Field(..., description="评估说明")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "waiver_rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "waiver_type": "spending_amount",
                "is_eligible": True,
                "current_progress": 55000.00,
                "required_target": 50000.00,
                "completion_percentage": 110.0,
                "estimated_waiver_amount": 300.00,
                "evaluation_message": "当前消费金额: ¥55,000.00, 需要: ¥50,000.00"
            }
        }
    )

    @field_validator('estimated_waiver_amount')
    @classmethod
    def validate_decimal_fields(cls, v):
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


# ========== 年费统计模型 ==========

class AnnualFeeStatisticsResponse(BaseModel):
    """年费统计响应模型"""
    year: int = Field(..., description="统计年份")
    total_cards_with_fee: int = Field(..., description="有年费的卡片总数")
    total_base_fee: Decimal = Field(..., description="基础年费总额")
    total_actual_fee: Decimal = Field(..., description="实际年费总额")
    total_waived_amount: Decimal = Field(..., description="减免总金额")
    waiver_rate: Decimal = Field(..., description="减免率(%)")
    status_distribution: Dict[str, int] = Field(..., description="状态分布")
    waiver_type_distribution: Dict[str, int] = Field(..., description="减免类型分布")
    upcoming_due_fees: List[Dict[str, Any]] = Field(..., description="即将到期的年费")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "year": 2024,
                "total_cards_with_fee": 5,
                "total_base_fee": 1500.00,
                "total_actual_fee": 600.00,
                "total_waived_amount": 900.00,
                "waiver_rate": 60.0,
                "status_distribution": {
                    "paid": 2,
                    "waived": 3
                },
                "waiver_type_distribution": {
                    "spending_amount": 3,
                    "transaction_count": 1,
                    "rigid": 1
                },
                "upcoming_due_fees": [
                    {
                        "record_id": "123e4567-e89b-12d3-a456-426614174000",
                        "card_name": "招商银行经典白金卡",
                        "base_fee": 300.00,
                        "actual_fee": 300.00,
                        "due_date": "2024-12-31",
                        "days_until_due": 15
                    }
                ]
            }
        }
    )

    @field_validator('total_base_fee', 'total_actual_fee', 'total_waived_amount', 'waiver_rate')
    @classmethod
    def validate_decimal_fields(cls, v):
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v 