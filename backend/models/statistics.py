"""
统计相关的Pydantic模型

定义各种统计数据的请求和响应模型。
"""

from decimal import Decimal
from typing import Dict, List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class CardStatistics(BaseModel):
    """
    信用卡统计信息
    """
    total_cards: int = Field(
        ..., 
        description="信用卡总数量",
        json_schema_extra={"example": 5}
    )
    active_cards: int = Field(
        ..., 
        description="激活的信用卡数量",
        json_schema_extra={"example": 4}
    )
    inactive_cards: int = Field(
        ..., 
        description="未激活的信用卡数量",
        json_schema_extra={"example": 1}
    )
    frozen_cards: int = Field(
        ..., 
        description="冻结的信用卡数量",
        json_schema_extra={"example": 0}
    )
    cancelled_cards: int = Field(
        ..., 
        description="已注销的信用卡数量",
        json_schema_extra={"example": 0}
    )
    expired_cards: int = Field(
        ..., 
        description="已过期的信用卡数量",
        json_schema_extra={"example": 0}
    )
    expiring_soon_cards: int = Field(
        ..., 
        description="即将到期的信用卡数量（未来3个月内到期）",
        json_schema_extra={"example": 1}
    )


class CreditLimitStatistics(BaseModel):
    """
    信用额度统计信息
    """
    total_credit_limit: Decimal = Field(
        ..., 
        description="总信用额度，单位：元",
        json_schema_extra={"example": "150000.00"}
    )
    total_used_amount: Decimal = Field(
        ..., 
        description="总已使用额度，单位：元",
        json_schema_extra={"example": "45000.00"}
    )
    total_available_amount: Decimal = Field(
        ..., 
        description="总可用额度，单位：元",
        json_schema_extra={"example": "105000.00"}
    )
    overall_utilization_rate: float = Field(
        ..., 
        description="总体额度使用率，百分比",
        json_schema_extra={"example": 30.0}
    )
    highest_utilization_rate: float = Field(
        ..., 
        description="最高单卡额度使用率，百分比",
        json_schema_extra={"example": 80.5}
    )
    lowest_utilization_rate: float = Field(
        ..., 
        description="最低单卡额度使用率，百分比",
        json_schema_extra={"example": 5.2}
    )
    average_utilization_rate: float = Field(
        ..., 
        description="平均额度使用率，百分比",
        json_schema_extra={"example": 42.3}
    )


class TransactionStatistics(BaseModel):
    """
    交易统计信息
    """
    total_transactions: int = Field(
        ..., 
        description="总交易笔数",
        json_schema_extra={"example": 156}
    )
    total_expense_amount: Decimal = Field(
        ..., 
        description="总消费金额，单位：元",
        json_schema_extra={"example": "89500.00"}
    )
    total_payment_amount: Decimal = Field(
        ..., 
        description="总还款金额，单位：元",
        json_schema_extra={"example": "92000.00"}
    )
    total_points_earned: Decimal = Field(
        ..., 
        description="总获得积分",
        json_schema_extra={"example": "8950.00"}
    )
    current_month_transactions: int = Field(
        ..., 
        description="本月交易笔数",
        json_schema_extra={"example": 23}
    )
    current_month_expense: Decimal = Field(
        ..., 
        description="本月消费金额，单位：元",
        json_schema_extra={"example": "12500.00"}
    )
    average_transaction_amount: Decimal = Field(
        ..., 
        description="平均交易金额，单位：元",
        json_schema_extra={"example": "573.72"}
    )


class CategoryStatistics(BaseModel):
    """
    分类统计信息
    """
    category: str = Field(
        ..., 
        description="消费分类",
        json_schema_extra={"example": "dining"}
    )
    category_name: str = Field(
        ..., 
        description="分类中文名称",
        json_schema_extra={"example": "餐饮美食"}
    )
    transaction_count: int = Field(
        ..., 
        description="交易笔数",
        json_schema_extra={"example": 45}
    )
    total_amount: Decimal = Field(
        ..., 
        description="总金额，单位：元",
        json_schema_extra={"example": "18900.00"}
    )
    percentage: float = Field(
        ..., 
        description="占总消费的百分比",
        json_schema_extra={"example": 21.1}
    )


class MonthlyStatistics(BaseModel):
    """
    月度统计信息
    """
    year_month: str = Field(
        ..., 
        description="年月，格式：YYYY-MM",
        json_schema_extra={"example": "2024-01"}
    )
    transaction_count: int = Field(
        ..., 
        description="交易笔数",
        json_schema_extra={"example": 32}
    )
    expense_amount: Decimal = Field(
        ..., 
        description="消费金额，单位：元",
        json_schema_extra={"example": "15600.00"}
    )
    payment_amount: Decimal = Field(
        ..., 
        description="还款金额，单位：元",
        json_schema_extra={"example": "14200.00"}
    )
    points_earned: Decimal = Field(
        ..., 
        description="获得积分",
        json_schema_extra={"example": "1560.00"}
    )


class AnnualFeeStatistics(BaseModel):
    """
    年费统计信息
    """
    total_annual_fee: Decimal = Field(
        ..., 
        description="年费总额，单位：元",
        json_schema_extra={"example": "2400.00"}
    )
    waived_count: int = Field(
        ..., 
        description="已减免年费的卡片数量",
        json_schema_extra={"example": 3}
    )
    pending_count: int = Field(
        ..., 
        description="待确认减免的卡片数量",
        json_schema_extra={"example": 1}
    )
    paid_count: int = Field(
        ..., 
        description="已缴费的卡片数量",
        json_schema_extra={"example": 1}
    )
    overdue_count: int = Field(
        ..., 
        description="逾期未缴的卡片数量",
        json_schema_extra={"example": 0}
    )
    current_year_fee_due: Decimal = Field(
        ..., 
        description="当前年度应缴年费，单位：元",
        json_schema_extra={"example": "800.00"}
    )
    savings_from_waiver: Decimal = Field(
        ..., 
        description="年费减免节省的金额，单位：元",
        json_schema_extra={"example": "1600.00"}
    )


class BankStatistics(BaseModel):
    """
    银行统计信息
    """
    bank_name: str = Field(
        ..., 
        description="银行名称",
        json_schema_extra={"example": "招商银行"}
    )
    card_count: int = Field(
        ..., 
        description="该银行的信用卡数量",
        json_schema_extra={"example": 2}
    )
    total_credit_limit: Decimal = Field(
        ..., 
        description="该银行的总信用额度，单位：元",
        json_schema_extra={"example": "60000.00"}
    )
    total_used_amount: Decimal = Field(
        ..., 
        description="该银行的总已使用额度，单位：元",
        json_schema_extra={"example": "18000.00"}
    )
    utilization_rate: float = Field(
        ..., 
        description="该银行的额度使用率，百分比",
        json_schema_extra={"example": 30.0}
    )


class OverallStatistics(BaseModel):
    """
    总体统计信息
    """
    # 信用卡统计
    card_stats: CardStatistics = Field(
        ..., 
        description="信用卡统计信息"
    )
    
    # 额度统计
    credit_stats: CreditLimitStatistics = Field(
        ..., 
        description="信用额度统计信息"
    )
    
    # 交易统计
    transaction_stats: TransactionStatistics = Field(
        ..., 
        description="交易统计信息"
    )
    
    # 年费统计
    annual_fee_stats: AnnualFeeStatistics = Field(
        ..., 
        description="年费统计信息"
    )
    
    # 分类统计（前10）
    top_categories: List[CategoryStatistics] = Field(
        ..., 
        description="消费分类统计（按金额排序，前10）"
    )
    
    # 月度统计（最近12个月）
    monthly_trends: List[MonthlyStatistics] = Field(
        ..., 
        description="月度统计趋势（最近12个月）"
    )
    
    # 银行统计
    bank_distribution: List[BankStatistics] = Field(
        ..., 
        description="各银行分布统计"
    )


class TimeRangeQuery(BaseModel):
    """
    时间范围查询参数
    """
    start_date: Optional[date] = Field(
        None,
        description="开始日期，格式：YYYY-MM-DD",
        json_schema_extra={"example": "2024-01-01"}
    )
    end_date: Optional[date] = Field(
        None,
        description="结束日期，格式：YYYY-MM-DD",
        json_schema_extra={"example": "2024-12-31"}
    )


class DetailedStatisticsQuery(BaseModel):
    """
    详细统计查询参数
    """
    # 时间范围
    start_date: Optional[date] = Field(
        None,
        description="开始日期，格式：YYYY-MM-DD",
        json_schema_extra={"example": "2024-01-01"}
    )
    end_date: Optional[date] = Field(
        None,
        description="结束日期，格式：YYYY-MM-DD",
        json_schema_extra={"example": "2024-12-31"}
    )
    
    # 特定银行
    bank_name: Optional[str] = Field(
        None,
        description="银行名称，筛选特定银行的统计",
        json_schema_extra={"example": "招商银行"}
    )
    
    # 特定信用卡
    card_id: Optional[str] = Field(
        None,
        description="信用卡ID，筛选特定信用卡的统计",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    # 包含已注销的卡片
    include_cancelled: bool = Field(
        False,
        description="是否包含已注销的信用卡",
        json_schema_extra={"example": False}
    ) 