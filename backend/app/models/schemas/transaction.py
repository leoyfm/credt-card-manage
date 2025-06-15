"""
交易管理相关的Pydantic模型
"""
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
import uuid


class TransactionCreate(BaseModel):
    """创建交易请求模型"""
    card_id: UUID = Field(..., description="信用卡ID")
    category_id: Optional[UUID] = Field(None, description="交易分类ID")
    transaction_type: str = Field(..., description="交易类型")
    amount: Decimal = Field(..., gt=0, description="交易金额")
    currency: Optional[str] = Field("CNY", description="货币类型")
    description: Optional[str] = Field(None, max_length=200, description="交易描述")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称")
    merchant_category: Optional[str] = Field(None, max_length=50, description="商户类别")
    location: Optional[str] = Field(None, max_length=200, description="交易地点")
    transaction_date: Optional[datetime] = Field(None, description="交易时间")
    notes: Optional[str] = Field(None, description="备注")
    tags: Optional[List[str]] = Field([], description="标签")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "card_id": str(uuid.uuid4()),
                "transaction_type": "expense",
                "amount": "299.50",
                "description": "星巴克咖啡",
                "merchant_name": "星巴克",
                "merchant_category": "餐饮美食",
                "location": "北京市朝阳区"
            }
        }
    )


class TransactionUpdate(BaseModel):
    """更新交易请求模型"""
    card_id: Optional[UUID] = Field(None, description="信用卡ID")
    category_id: Optional[UUID] = Field(None, description="交易分类ID")
    transaction_type: Optional[str] = Field(None, description="交易类型")
    amount: Optional[Decimal] = Field(None, gt=0, description="交易金额")
    currency: Optional[str] = Field(None, description="货币类型")
    description: Optional[str] = Field(None, max_length=200, description="交易描述")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称")
    merchant_category: Optional[str] = Field(None, max_length=50, description="商户类别")
    location: Optional[str] = Field(None, max_length=200, description="交易地点")
    transaction_date: Optional[datetime] = Field(None, description="交易时间")
    notes: Optional[str] = Field(None, description="备注")
    tags: Optional[List[str]] = Field(None, description="标签")


class TransactionResponse(BaseModel):
    """交易响应模型"""
    id: UUID = Field(..., description="交易ID")
    card_id: UUID = Field(..., description="信用卡ID")
    category_id: Optional[UUID] = Field(None, description="交易分类ID")
    transaction_type: str = Field(..., description="交易类型")
    amount: Decimal = Field(..., description="交易金额")
    currency: str = Field(..., description="货币类型")
    description: Optional[str] = Field(None, description="交易描述")
    merchant_name: Optional[str] = Field(None, description="商户名称")
    merchant_category: Optional[str] = Field(None, description="商户类别")
    location: Optional[str] = Field(None, description="交易地点")
    points_earned: int = Field(0, description="获得积分")
    cashback_earned: Decimal = Field(Decimal("0.00"), description="获得返现")
    status: str = Field(..., description="状态")
    transaction_date: Optional[datetime] = Field(None, description="交易时间")
    notes: Optional[str] = Field(None, description="备注")
    tags: List[str] = Field([], description="标签")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 关联数据
    card_name: Optional[str] = Field(None, description="信用卡名称")
    card_number: Optional[str] = Field(None, description="信用卡卡号后四位")
    category_name: Optional[str] = Field(None, description="分类名称")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid.uuid4()),
                "card_id": str(uuid.uuid4()),
                "transaction_type": "expense",
                "amount": "299.50",
                "currency": "CNY",
                "description": "星巴克咖啡",
                "merchant_name": "星巴克",
                "merchant_category": "餐饮美食",
                "location": "北京市朝阳区",
                "points_earned": 299,
                "cashback_earned": "2.99",
                "status": "completed",
                "card_name": "招商银行信用卡",
                "card_number": "1234",
                "category_name": "餐饮美食"
            }
        }
    )


class TransactionListResponse(BaseModel):
    """交易列表响应模型"""
    transactions: List[TransactionResponse] = Field(..., description="交易列表")
    total: int = Field(..., description="总数")


class TransactionStatisticsResponse(BaseModel):
    """交易统计响应模型"""
    period_start: datetime = Field(..., description="统计开始时间")
    period_end: datetime = Field(..., description="统计结束时间")
    total_transactions: int = Field(..., description="交易总笔数")
    total_expense: float = Field(..., description="总支出")
    total_income: float = Field(..., description="总收入")
    net_amount: float = Field(..., description="净额")
    average_transaction: float = Field(..., description="平均交易额")
    total_points_earned: int = Field(..., description="总获得积分")
    total_cashback_earned: float = Field(..., description="总获得返现")
    type_distribution: Dict[str, Dict[str, Any]] = Field(..., description="类型分布")
    monthly_trends: List[Dict[str, Any]] = Field(..., description="月度趋势")


class CategoryStatisticsResponse(BaseModel):
    """分类统计响应模型"""
    period_start: datetime = Field(..., description="统计开始时间")
    period_end: datetime = Field(..., description="统计结束时间")
    total_categories: int = Field(..., description="分类总数")
    total_expense: float = Field(..., description="总支出")
    category_distribution: List[Dict[str, Any]] = Field(..., description="分类分布")
    top_categories: List[Dict[str, Any]] = Field(..., description="前5大分类")


class MonthlyTrendResponse(BaseModel):
    """月度趋势响应模型"""
    analysis_period: str = Field(..., description="分析周期")
    monthly_trends: List[Dict[str, Any]] = Field(..., description="月度趋势数据")
    expense_trend: str = Field(..., description="支出趋势")
    total_months: int = Field(..., description="分析月数")


class TransactionCategoryResponse(BaseModel):
    """交易分类响应模型"""
    id: UUID = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    icon: Optional[str] = Field(None, description="图标")
    color: Optional[str] = Field(None, description="颜色")
    parent_id: Optional[UUID] = Field(None, description="父分类ID")
    is_system: bool = Field(..., description="是否系统分类")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": str(uuid.uuid4()),
                "name": "餐饮美食",
                "icon": "food",
                "color": "#FF6B6B",
                "parent_id": None,
                "is_system": True
            }
        }
    ) 