"""
交易管理相关的数据模型

本模块定义了交易管理功能所需的所有Pydantic模型，包括：
- 交易创建、更新、查询请求模型
- 交易响应模型
- 交易分类模型
- 统计分析模型

作者: LEO
邮箱: leoyfm@gmail.com
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

# 枚举定义
class TransactionType(str, Enum):
    """交易类型"""
    expense = "expense"      # 支出
    income = "income"        # 收入
    transfer = "transfer"    # 转账

class TransactionStatus(str, Enum):
    """交易状态"""
    pending = "pending"      # 待处理
    completed = "completed"  # 已完成
    failed = "failed"        # 失败
    refunded = "refunded"    # 已退款

class CurrencyType(str, Enum):
    """货币类型"""
    cny = "CNY"
    usd = "USD"
    hkd = "HKD"
    eur = "EUR"
    jpy = "JPY"

# 交易分类模型
class TransactionCategoryResponse(BaseModel):
    """交易分类响应"""
    id: UUID = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    icon: Optional[str] = Field(None, description="分类图标")
    color: Optional[str] = Field(None, description="分类颜色")
    parent_id: Optional[UUID] = Field(None, description="父分类ID")
    is_system: bool = Field(..., description="是否系统分类")
    is_active: bool = Field(..., description="是否激活")
    sort_order: int = Field(..., description="排序")
    children: List['TransactionCategoryResponse'] = Field(default_factory=list, description="子分类")

    class Config:
        from_attributes = True

# 交易创建请求
class TransactionCreateRequest(BaseModel):
    """创建交易请求"""
    card_id: UUID = Field(..., description="信用卡ID")
    category_id: Optional[UUID] = Field(None, description="交易分类ID")
    transaction_type: TransactionType = Field(..., description="交易类型")
    amount: Decimal = Field(..., gt=0, le=9999999, description="交易金额", example=150.50)
    currency: CurrencyType = Field(CurrencyType.cny, description="货币类型")
    description: str = Field(..., min_length=1, max_length=200, description="交易描述", example="超市购物")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称", example="永辉超市")
    merchant_category: Optional[str] = Field(None, max_length=50, description="商户类别", example="超市")
    location: Optional[str] = Field(None, max_length=200, description="交易地点", example="上海市浦东新区")
    transaction_date: Optional[datetime] = Field(None, description="交易时间，默认为当前时间")
    notes: Optional[str] = Field(None, max_length=500, description="备注")
    tags: List[str] = Field(default_factory=list, description="标签", example=["日常消费", "食物"])

    @validator('amount')
    def validate_amount(cls, v):
        """验证金额精度"""
        if v.as_tuple().exponent < -2:
            raise ValueError("金额最多保留2位小数")
        return v

    @validator('transaction_date')
    def validate_transaction_date(cls, v):
        """验证交易时间不能是未来时间"""
        if v and v > datetime.now():
            raise ValueError("交易时间不能是未来时间")
        return v

# 交易更新请求
class TransactionUpdateRequest(BaseModel):
    """更新交易请求"""
    category_id: Optional[UUID] = Field(None, description="交易分类ID")
    transaction_type: Optional[TransactionType] = Field(None, description="交易类型")
    amount: Optional[Decimal] = Field(None, gt=0, le=9999999, description="交易金额")
    currency: Optional[CurrencyType] = Field(None, description="货币类型")
    description: Optional[str] = Field(None, min_length=1, max_length=200, description="交易描述")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称")
    merchant_category: Optional[str] = Field(None, max_length=50, description="商户类别")
    location: Optional[str] = Field(None, max_length=200, description="交易地点")
    transaction_date: Optional[datetime] = Field(None, description="交易时间")
    notes: Optional[str] = Field(None, max_length=500, description="备注")
    tags: Optional[List[str]] = Field(None, description="标签")

    @validator('amount')
    def validate_amount(cls, v):
        """验证金额精度"""
        if v and v.as_tuple().exponent < -2:
            raise ValueError("金额最多保留2位小数")
        return v

    @validator('transaction_date')
    def validate_transaction_date(cls, v):
        """验证交易时间"""
        if v and v > datetime.now():
            raise ValueError("交易时间不能是未来时间")
        return v

# 交易状态更新请求
class TransactionStatusUpdateRequest(BaseModel):
    """交易状态更新请求"""
    status: TransactionStatus = Field(..., description="交易状态")
    reason: Optional[str] = Field(None, max_length=200, description="状态变更原因")

# 交易响应模型
class TransactionResponse(BaseModel):
    """交易信息响应"""
    id: UUID = Field(..., description="交易ID")
    user_id: UUID = Field(..., description="用户ID")
    card_id: UUID = Field(..., description="信用卡ID")
    card_name: str = Field(..., description="信用卡名称")
    bank_name: str = Field(..., description="银行名称")
    category_id: Optional[UUID] = Field(None, description="交易分类ID")
    category_name: Optional[str] = Field(None, description="交易分类名称")
    transaction_type: TransactionType = Field(..., description="交易类型")
    amount: Decimal = Field(..., description="交易金额")
    currency: CurrencyType = Field(..., description="货币类型")
    description: str = Field(..., description="交易描述")
    merchant_name: Optional[str] = Field(None, description="商户名称")
    merchant_category: Optional[str] = Field(None, description="商户类别")
    location: Optional[str] = Field(None, description="交易地点")
    points_earned: int = Field(0, description="获得积分")
    cashback_earned: Decimal = Field(Decimal("0"), description="获得返现")
    status: TransactionStatus = Field(..., description="交易状态")
    transaction_date: datetime = Field(..., description="交易时间")
    notes: Optional[str] = Field(None, description="备注")
    tags: List[str] = Field(..., description="标签")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 交易详细信息响应
class TransactionDetailResponse(TransactionResponse):
    """交易详细信息响应"""
    category_info: Optional[TransactionCategoryResponse] = Field(None, description="分类详细信息")
    exchange_rate: Optional[Decimal] = Field(None, description="汇率（如果涉及外币）")
    original_amount: Optional[Decimal] = Field(None, description="原始金额（外币）")
    original_currency: Optional[CurrencyType] = Field(None, description="原始货币")
    related_transactions: List['TransactionResponse'] = Field(default_factory=list, description="关联交易")

# 交易列表查询参数
class TransactionListQuery(BaseModel):
    """交易列表查询参数"""
    keyword: str = Field("", description="搜索关键词，支持描述、商户名称模糊搜索")
    transaction_type: Optional[TransactionType] = Field(None, description="交易类型筛选")
    status: Optional[TransactionStatus] = Field(None, description="交易状态筛选")
    card_id: Optional[UUID] = Field(None, description="信用卡筛选")
    category_id: Optional[UUID] = Field(None, description="交易分类筛选")
    merchant_name: Optional[str] = Field(None, description="商户名称筛选")
    currency: Optional[CurrencyType] = Field(None, description="货币类型筛选")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额筛选")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额筛选")
    start_date: Optional[date] = Field(None, description="开始日期筛选")
    end_date: Optional[date] = Field(None, description="结束日期筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    sort_by: str = Field("transaction_date", description="排序字段：transaction_date, amount, created_at")
    sort_order: str = Field("desc", description="排序方向：asc, desc")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError("结束日期不能早于开始日期")
        return v

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        """验证金额范围"""
        min_amount = values.get('min_amount')
        if min_amount and v and v < min_amount:
            raise ValueError("最大金额不能小于最小金额")
        return v

# 交易统计信息
class TransactionStatistics(BaseModel):
    """交易统计信息"""
    total_transactions: int = Field(0, description="交易总笔数")
    total_expense: Decimal = Field(Decimal("0"), description="总支出")
    total_income: Decimal = Field(Decimal("0"), description="总收入")
    average_expense: Decimal = Field(Decimal("0"), description="平均支出")
    max_transaction: Decimal = Field(Decimal("0"), description="最大单笔交易")
    min_transaction: Decimal = Field(Decimal("0"), description="最小单笔交易")
    transactions_by_type: Dict[str, int] = Field(default_factory=dict, description="按类型分组的交易数")
    transactions_by_category: Dict[str, Decimal] = Field(default_factory=dict, description="按分类分组的支出")
    transactions_by_merchant: Dict[str, Decimal] = Field(default_factory=dict, description="按商户分组的支出")
    transactions_by_month: Dict[str, Decimal] = Field(default_factory=dict, description="按月份分组的支出")
    transactions_by_card: Dict[str, Decimal] = Field(default_factory=dict, description="按卡片分组的支出")
    total_points_earned: int = Field(0, description="总获得积分")
    total_cashback_earned: Decimal = Field(Decimal("0"), description="总获得返现")
    currency_distribution: Dict[str, Decimal] = Field(default_factory=dict, description="货币分布")

# 月度交易统计
class MonthlyTransactionStats(BaseModel):
    """月度交易统计"""
    year: int = Field(..., description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")
    total_transactions: int = Field(0, description="交易笔数")
    total_expense: Decimal = Field(Decimal("0"), description="总支出")
    total_income: Decimal = Field(Decimal("0"), description="总收入")
    net_amount: Decimal = Field(Decimal("0"), description="净额（收入-支出）")
    average_daily_expense: Decimal = Field(Decimal("0"), description="日均支出")
    top_categories: List[Dict[str, Any]] = Field(default_factory=list, description="热门分类")
    top_merchants: List[Dict[str, Any]] = Field(default_factory=list, description="热门商户")

# 交易分析报告
class TransactionAnalysisReport(BaseModel):
    """交易分析报告"""
    period: str = Field(..., description="分析期间", example="2024-12")
    summary: TransactionStatistics = Field(..., description="统计摘要")
    trends: List[MonthlyTransactionStats] = Field(..., description="趋势分析")
    insights: List[str] = Field(default_factory=list, description="分析洞察")
    recommendations: List[str] = Field(default_factory=list, description="优化建议")

# 批量导入交易请求
class TransactionImportRequest(BaseModel):
    """交易批量导入请求"""
    transactions: List[TransactionCreateRequest] = Field(..., min_items=1, max_items=1000, description="交易列表")
    skip_duplicates: bool = Field(True, description="是否跳过重复交易")
    auto_categorize: bool = Field(True, description="是否自动分类")

# 批量导入响应
class TransactionImportResponse(BaseModel):
    """交易导入响应"""
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="导入失败数量")
    skipped_count: int = Field(..., description="跳过数量")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败项目详情")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    message: str = Field(..., description="导入结果消息")

# 批量操作请求
class TransactionBatchRequest(BaseModel):
    """批量操作交易请求"""
    transaction_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="交易ID列表")
    operation: str = Field(..., description="操作类型：delete, update_category, update_status")
    data: Dict[str, Any] = Field(..., description="操作数据")

# 批量操作响应
class TransactionBatchResponse(BaseModel):
    """批量操作响应"""
    success_count: int = Field(..., description="成功操作的数量")
    failed_count: int = Field(..., description="操作失败的数量")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败的项目详情")
    message: str = Field(..., description="操作结果消息")

# 交易建议模型
class TransactionSuggestion(BaseModel):
    """交易建议"""
    suggestion_type: str = Field(..., description="建议类型", example="category_suggestion")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    action_data: Dict[str, Any] = Field(default_factory=dict, description="行动数据")

# 交易分类建议响应
class TransactionCategorySuggestion(BaseModel):
    """交易分类建议响应"""
    transaction_id: UUID = Field(..., description="交易ID")
    suggestions: List[TransactionSuggestion] = Field(..., description="分类建议列表")
    auto_applied: bool = Field(False, description="是否已自动应用")

# 支出预算模型
class ExpenseBudget(BaseModel):
    """支出预算"""
    category_id: Optional[UUID] = Field(None, description="分类ID，为空表示总预算")
    category_name: Optional[str] = Field(None, description="分类名称")
    budget_amount: Decimal = Field(..., gt=0, description="预算金额")
    spent_amount: Decimal = Field(Decimal("0"), description="已支出金额")
    remaining_amount: Decimal = Field(..., description="剩余金额")
    usage_percentage: float = Field(..., ge=0, description="使用百分比")
    is_exceeded: bool = Field(False, description="是否超预算")
    period_type: str = Field("monthly", description="预算周期：monthly, yearly")
    period_value: str = Field(..., description="周期值", example="2024-12")

# 支出预警
class ExpenseAlert(BaseModel):
    """支出预警"""
    alert_type: str = Field(..., description="预警类型")
    category_name: Optional[str] = Field(None, description="分类名称")
    current_amount: Decimal = Field(..., description="当前金额")
    threshold_amount: Decimal = Field(..., description="阈值金额")
    message: str = Field(..., description="预警消息")
    severity: str = Field(..., description="严重程度：low, medium, high")
    created_at: datetime = Field(..., description="创建时间")

# 分类统计模型
class CategoryStats(BaseModel):
    """分类统计"""
    category_id: Optional[UUID] = Field(None, description="分类ID")
    category_name: str = Field(..., description="分类名称")
    transaction_count: int = Field(0, description="交易笔数")
    total_amount: Decimal = Field(Decimal("0"), description="总金额")
    percentage: float = Field(0.0, description="占比")
    
# 月度趋势模型
class MonthlyTrend(BaseModel):
    """月度趋势"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份") 
    transaction_count: int = Field(0, description="交易笔数")
    total_amount: Decimal = Field(Decimal("0"), description="总金额")
    expense_amount: Decimal = Field(Decimal("0"), description="支出金额")
    income_amount: Decimal = Field(Decimal("0"), description="收入金额")

# 基础交易模型（用于服务层）
class Transaction(TransactionResponse):
    """基础交易模型（继承自TransactionResponse）"""
    pass

# 别名定义
TransactionCreate = TransactionCreateRequest
TransactionUpdate = TransactionUpdateRequest
TransactionQueryFilter = TransactionListQuery
TransactionBatchOperation = TransactionBatchRequest
TransactionStats = TransactionStatistics
TransactionSummary = TransactionResponse  # 简化的交易摘要信息 