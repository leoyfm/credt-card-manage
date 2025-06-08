"""
交易记录Pydantic模型

定义交易记录相关的请求和响应模型。
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# 导入枚举类型
from db_models.transactions import TransactionType, TransactionCategory, TransactionStatus


# ==================== 基础模型 ====================

class TransactionBase(BaseModel):
    """交易记录基础模型"""
    card_id: UUID = Field(
        ..., 
        description="信用卡ID",
        example="f47ac10b-58cc-4372-a567-0e02b2c3d479"
    )
    transaction_type: TransactionType = Field(
        ..., 
        description="交易类型",
        example=TransactionType.EXPENSE
    )
    amount: Decimal = Field(
        ..., 
        description="交易金额，单位：元", 
        ge=0,
        example=199.50
    )
    transaction_date: datetime = Field(
        ..., 
        description="交易时间",
        example="2024-06-08T14:30:00"
    )
    merchant_name: Optional[str] = Field(
        None, 
        description="商户名称",
        max_length=200,
        example="星巴克咖啡"
    )
    description: Optional[str] = Field(
        None, 
        description="交易描述",
        max_length=500,
        example="购买咖啡和蛋糕"
    )
    category: TransactionCategory = Field(
        TransactionCategory.OTHER, 
        description="交易分类",
        example=TransactionCategory.DINING
    )
    status: TransactionStatus = Field(
        TransactionStatus.COMPLETED, 
        description="交易状态",
        example=TransactionStatus.COMPLETED
    )
    points_earned: Optional[Decimal] = Field(
        0, 
        description="获得积分数", 
        ge=0,
        example=19.95
    )
    points_rate: Optional[Decimal] = Field(
        None, 
        description="积分倍率",
        ge=0,
        example=1.5
    )
    reference_number: Optional[str] = Field(
        None, 
        description="交易参考号/凭证号",
        max_length=100,
        example="TXN202406081430001"
    )
    location: Optional[str] = Field(
        None, 
        description="交易地点",
        max_length=200,
        example="北京市朝阳区三里屯"
    )
    is_installment: bool = Field(
        False, 
        description="是否分期交易",
        example=False
    )
    installment_count: Optional[int] = Field(
        None, 
        description="分期期数",
        ge=2,
        le=36,
        example=None
    )
    notes: Optional[str] = Field(
        None, 
        description="备注信息",
        example="使用优惠券消费"
    )

    @field_validator('installment_count')
    def validate_installment_count(cls, v, values):
        """验证分期期数"""
        is_installment = values.data.get('is_installment', False)
        if is_installment and v is None:
            raise ValueError('分期交易必须指定分期期数')
        if not is_installment and v is not None:
            raise ValueError('非分期交易不能指定分期期数')
        return v


# ==================== 请求模型 ====================

class TransactionCreate(TransactionBase):
    """创建交易记录请求模型"""
    pass


class TransactionUpdate(BaseModel):
    """更新交易记录请求模型"""
    transaction_type: Optional[TransactionType] = Field(
        None, 
        description="交易类型"
    )
    amount: Optional[Decimal] = Field(
        None, 
        description="交易金额，单位：元", 
        ge=0
    )
    transaction_date: Optional[datetime] = Field(
        None, 
        description="交易时间"
    )
    merchant_name: Optional[str] = Field(
        None, 
        description="商户名称",
        max_length=200
    )
    description: Optional[str] = Field(
        None, 
        description="交易描述",
        max_length=500
    )
    category: Optional[TransactionCategory] = Field(
        None, 
        description="交易分类"
    )
    status: Optional[TransactionStatus] = Field(
        None, 
        description="交易状态"
    )
    points_earned: Optional[Decimal] = Field(
        None, 
        description="获得积分数", 
        ge=0
    )
    points_rate: Optional[Decimal] = Field(
        None, 
        description="积分倍率",
        ge=0
    )
    reference_number: Optional[str] = Field(
        None, 
        description="交易参考号/凭证号",
        max_length=100
    )
    location: Optional[str] = Field(
        None, 
        description="交易地点",
        max_length=200
    )
    is_installment: Optional[bool] = Field(
        None, 
        description="是否分期交易"
    )
    installment_count: Optional[int] = Field(
        None, 
        description="分期期数",
        ge=2,
        le=36
    )
    notes: Optional[str] = Field(
        None, 
        description="备注信息"
    )


# ==================== 响应模型 ====================

class Transaction(TransactionBase):
    """交易记录响应模型"""
    id: UUID = Field(
        ..., 
        description="交易记录ID",
        example="a1b2c3d4-5e6f-7890-abcd-ef1234567890"
    )
    user_id: UUID = Field(
        ..., 
        description="用户ID",
        example="489f8b55-5e75-4f18-982f-fca23b9d3ee4"
    )
    created_at: datetime = Field(
        ..., 
        description="创建时间",
        example="2024-06-08T14:30:00"
    )
    updated_at: datetime = Field(
        ..., 
        description="更新时间",
        example="2024-06-08T14:30:00"
    )

    class Config:
        from_attributes = True


class TransactionWithCard(Transaction):
    """包含信用卡信息的交易记录响应模型"""
    card_name: str = Field(
        ..., 
        description="信用卡名称",
        example="招商银行信用卡"
    )
    bank_name: str = Field(
        ..., 
        description="银行名称",
        example="招商银行"
    )
    card_number_masked: str = Field(
        ..., 
        description="脱敏的信用卡号",
        example="**** **** **** 1234"
    )


# ==================== 查询参数模型 ====================

class TransactionQueryParams(BaseModel):
    """交易记录查询参数"""
    card_id: Optional[UUID] = Field(
        None, 
        description="信用卡ID过滤"
    )
    transaction_type: Optional[TransactionType] = Field(
        None, 
        description="交易类型过滤"
    )
    category: Optional[TransactionCategory] = Field(
        None, 
        description="交易分类过滤"
    )
    status: Optional[TransactionStatus] = Field(
        None, 
        description="交易状态过滤"
    )
    start_date: Optional[datetime] = Field(
        None, 
        description="开始时间",
        example="2024-01-01T00:00:00"
    )
    end_date: Optional[datetime] = Field(
        None, 
        description="结束时间",
        example="2024-12-31T23:59:59"
    )
    merchant_name: Optional[str] = Field(
        None, 
        description="商户名称模糊搜索"
    )
    min_amount: Optional[Decimal] = Field(
        None, 
        description="最小金额",
        ge=0
    )
    max_amount: Optional[Decimal] = Field(
        None, 
        description="最大金额",
        ge=0
    )
    keyword: str = Field(
        "", 
        description="关键词模糊搜索，支持商户名称、交易描述、备注",
        example=""
    )


# ==================== 统计模型 ====================

class TransactionStatistics(BaseModel):
    """交易统计模型"""
    total_transactions: int = Field(
        ..., 
        description="总交易笔数",
        example=156
    )
    total_amount: Decimal = Field(
        ..., 
        description="总交易金额",
        example=12580.50
    )
    expense_amount: Decimal = Field(
        ..., 
        description="总支出金额",
        example=11200.30
    )
    income_amount: Decimal = Field(
        ..., 
        description="总收入金额",
        example=1380.20
    )
    points_earned: Decimal = Field(
        ..., 
        description="总获得积分",
        example=1125.50
    )
    categories: List[dict] = Field(
        ..., 
        description="分类统计",
        example=[
            {"category": "dining", "count": 45, "amount": 3200.50},
            {"category": "shopping", "count": 32, "amount": 5800.80}
        ]
    )


class TransactionCategoryStatistics(BaseModel):
    """交易分类统计模型"""
    category: TransactionCategory = Field(
        ..., 
        description="交易分类",
        example=TransactionCategory.DINING
    )
    category_display: str = Field(
        ..., 
        description="分类显示名称",
        example="餐饮美食"
    )
    transaction_count: int = Field(
        ..., 
        description="交易笔数",
        example=45
    )
    total_amount: Decimal = Field(
        ..., 
        description="总金额",
        example=3200.50
    )
    average_amount: Decimal = Field(
        ..., 
        description="平均金额",
        example=71.12
    )
    percentage: float = Field(
        ..., 
        description="占比百分比",
        example=28.6
    )


class MonthlyTransactionTrend(BaseModel):
    """月度交易趋势模型"""
    year: int = Field(
        ..., 
        description="年份",
        example=2024
    )
    month: int = Field(
        ..., 
        description="月份",
        example=6
    )
    transaction_count: int = Field(
        ..., 
        description="交易笔数",
        example=25
    )
    total_amount: Decimal = Field(
        ..., 
        description="总金额",
        example=2580.50
    )
    expense_amount: Decimal = Field(
        ..., 
        description="支出金额",
        example=2380.30
    )
    income_amount: Decimal = Field(
        ..., 
        description="收入金额",
        example=200.20
    )


# ==================== 工具函数 ====================

def get_transaction_type_display(transaction_type: TransactionType) -> str:
    """获取交易类型的中文显示名称"""
    type_display = {
        TransactionType.EXPENSE: "消费",
        TransactionType.PAYMENT: "还款",
        TransactionType.REFUND: "退款",
        TransactionType.WITHDRAWAL: "取现",
        TransactionType.TRANSFER: "转账",
        TransactionType.FEE: "手续费"
    }
    return type_display.get(transaction_type, "未知")


def get_transaction_category_display(category: TransactionCategory) -> str:
    """获取交易分类的中文显示名称"""
    category_display = {
        TransactionCategory.DINING: "餐饮美食",
        TransactionCategory.SHOPPING: "购物消费",
        TransactionCategory.TRANSPORT: "交通出行",
        TransactionCategory.ENTERTAINMENT: "娱乐休闲",
        TransactionCategory.MEDICAL: "医疗健康",
        TransactionCategory.EDUCATION: "教育培训",
        TransactionCategory.TRAVEL: "旅游酒店",
        TransactionCategory.FUEL: "加油充值",
        TransactionCategory.SUPERMARKET: "超市便利",
        TransactionCategory.ONLINE: "网上购物",
        TransactionCategory.OTHER: "其他消费"
    }
    return category_display.get(category, "未知分类")


def get_transaction_status_display(status: TransactionStatus) -> str:
    """获取交易状态的中文显示名称"""
    status_display = {
        TransactionStatus.PENDING: "待处理",
        TransactionStatus.COMPLETED: "已完成",
        TransactionStatus.FAILED: "交易失败",
        TransactionStatus.CANCELLED: "已取消",
        TransactionStatus.REFUNDED: "已退款"
    }
    return status_display.get(status, "未知状态") 