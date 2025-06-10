"""
统计分析相关的数据模型

本模块定义了统计分析功能所需的所有Pydantic模型，包括：
- 综合统计报表模型
- 趋势分析模型
- 对比分析模型
- 自定义报表模型

作者: LEO
邮箱: leoyfm@gmail.com
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any, Dict, Union
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

# 枚举定义
class StatisticsPeriod(str, Enum):
    """统计周期"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"
    custom = "custom"

class StatisticsType(str, Enum):
    """统计类型"""
    overview = "overview"          # 总览统计
    cards = "cards"               # 信用卡统计
    transactions = "transactions"  # 交易统计
    annual_fees = "annual_fees"   # 年费统计
    comparison = "comparison"      # 对比分析
    trend = "trend"               # 趋势分析

class ChartType(str, Enum):
    """图表类型"""
    line = "line"
    bar = "bar"
    pie = "pie"
    area = "area"
    scatter = "scatter"
    radar = "radar"

# 统计查询请求
class StatisticsQueryRequest(BaseModel):
    """统计查询请求"""
    statistics_type: StatisticsType = Field(..., description="统计类型")
    period: StatisticsPeriod = Field(..., description="统计周期")
    start_date: Optional[date] = Field(None, description="开始日期（custom周期时必需）")
    end_date: Optional[date] = Field(None, description="结束日期（custom周期时必需）")
    card_ids: Optional[List[UUID]] = Field(None, description="筛选的信用卡ID列表")
    category_ids: Optional[List[UUID]] = Field(None, description="筛选的交易分类ID列表")
    include_charts: bool = Field(True, description="是否包含图表数据")
    comparison_period: Optional[str] = Field(None, description="对比周期：last_period, same_period_last_year")
    group_by: Optional[List[str]] = Field(None, description="分组字段")
    metrics: Optional[List[str]] = Field(None, description="指定指标")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        start_date = values.get('start_date')
        period = values.get('period')
        
        if period == StatisticsPeriod.custom:
            if not start_date or not v:
                raise ValueError("自定义周期必须指定开始和结束日期")
            if v <= start_date:
                raise ValueError("结束日期必须晚于开始日期")
        
        return v

# 基础统计指标
class BaseMetrics(BaseModel):
    """基础统计指标"""
    count: int = Field(0, description="数量")
    total: Decimal = Field(Decimal("0"), description="总额")
    average: Decimal = Field(Decimal("0"), description="平均值")
    max_value: Decimal = Field(Decimal("0"), description="最大值")
    min_value: Decimal = Field(Decimal("0"), description="最小值")
    growth_rate: Optional[float] = Field(None, description="增长率（%）")
    period_label: str = Field(..., description="周期标签")

# 图表数据点
class ChartDataPoint(BaseModel):
    """图表数据点"""
    label: str = Field(..., description="数据标签")
    value: Union[float, int, Decimal] = Field(..., description="数据值")
    color: Optional[str] = Field(None, description="颜色")
    percentage: Optional[float] = Field(None, description="百分比")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

# 图表数据
class ChartData(BaseModel):
    """图表数据"""
    chart_type: ChartType = Field(..., description="图表类型")
    title: str = Field(..., description="图表标题")
    data_points: List[ChartDataPoint] = Field(..., description="数据点列表")
    x_axis_label: Optional[str] = Field(None, description="X轴标签")
    y_axis_label: Optional[str] = Field(None, description="Y轴标签")
    unit: Optional[str] = Field(None, description="数值单位")
    description: Optional[str] = Field(None, description="图表描述")

# 总览统计
class OverviewStatistics(BaseModel):
    """总览统计"""
    period: str = Field(..., description="统计周期")
    cards_summary: Dict[str, Any] = Field(..., description="信用卡摘要")
    transactions_summary: Dict[str, Any] = Field(..., description="交易摘要")
    annual_fees_summary: Dict[str, Any] = Field(..., description="年费摘要")
    financial_health: Dict[str, Any] = Field(..., description="财务健康度")
    key_insights: List[str] = Field(default_factory=list, description="关键洞察")
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")

# 信用卡统计
class CardsStatistics(BaseModel):
    """信用卡统计"""
    period: str = Field(..., description="统计周期")
    total_cards: int = Field(0, description="信用卡总数")
    active_cards: int = Field(0, description="活跃卡片数")
    total_credit_limit: Decimal = Field(Decimal("0"), description="总信用额度")
    credit_utilization: float = Field(0.0, description="信用利用率")
    cards_by_bank: Dict[str, int] = Field(default_factory=dict, description="按银行分组")
    cards_by_level: Dict[str, int] = Field(default_factory=dict, description="按等级分组")
    cards_by_network: Dict[str, int] = Field(default_factory=dict, description="按卡组织分组")
    expiring_soon: List[Dict[str, Any]] = Field(default_factory=list, description="即将过期卡片")
    performance_ranking: List[Dict[str, Any]] = Field(default_factory=list, description="卡片表现排名")
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")

# 交易统计
class TransactionsStatistics(BaseModel):
    """交易统计"""
    period: str = Field(..., description="统计周期")
    total_transactions: int = Field(0, description="交易总笔数")
    total_expense: Decimal = Field(Decimal("0"), description="总支出")
    total_income: Decimal = Field(Decimal("0"), description="总收入")
    net_amount: Decimal = Field(Decimal("0"), description="净额")
    average_transaction: Decimal = Field(Decimal("0"), description="平均单笔交易")
    transactions_by_type: Dict[str, int] = Field(default_factory=dict, description="按类型分组")
    transactions_by_category: Dict[str, Decimal] = Field(default_factory=dict, description="按分类分组")
    transactions_by_merchant: Dict[str, Decimal] = Field(default_factory=dict, description="按商户分组")
    transactions_by_card: Dict[str, Decimal] = Field(default_factory=dict, description="按卡片分组")
    daily_average: Decimal = Field(Decimal("0"), description="日均支出")
    spending_trend: List[Dict[str, Any]] = Field(default_factory=list, description="支出趋势")
    top_categories: List[Dict[str, Any]] = Field(default_factory=list, description="热门分类")
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")

# 年费统计
class AnnualFeesStatistics(BaseModel):
    """年费统计"""
    period: str = Field(..., description="统计周期")
    total_fees: Decimal = Field(Decimal("0"), description="年费总额")
    paid_fees: Decimal = Field(Decimal("0"), description="已缴费总额")
    waived_fees: Decimal = Field(Decimal("0"), description="已减免总额")
    pending_fees: Decimal = Field(Decimal("0"), description="待缴费总额")
    waiver_success_rate: float = Field(0.0, description="减免成功率")
    fees_by_type: Dict[str, Decimal] = Field(default_factory=dict, description="按类型分组")
    fees_by_bank: Dict[str, Decimal] = Field(default_factory=dict, description="按银行分组")
    fees_by_status: Dict[str, int] = Field(default_factory=dict, description="按状态分组")
    upcoming_dues: List[Dict[str, Any]] = Field(default_factory=list, description="即将到期")
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="优化机会")
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")

# 趋势分析
class TrendAnalysis(BaseModel):
    """趋势分析"""
    metric_name: str = Field(..., description="指标名称")
    period_type: StatisticsPeriod = Field(..., description="周期类型")
    data_points: List[Dict[str, Any]] = Field(..., description="数据点")
    trend_direction: str = Field(..., description="趋势方向：上升/下降/稳定")
    trend_strength: float = Field(..., ge=0, le=1, description="趋势强度")
    correlation_coefficient: Optional[float] = Field(None, description="相关系数")
    seasonal_pattern: Optional[Dict[str, Any]] = Field(None, description="季节性模式")
    forecast: Optional[List[Dict[str, Any]]] = Field(None, description="预测数据")
    insights: List[str] = Field(default_factory=list, description="趋势洞察")

# 对比分析
class ComparisonAnalysis(BaseModel):
    """对比分析"""
    comparison_type: str = Field(..., description="对比类型")
    current_period: Dict[str, Any] = Field(..., description="当前周期数据")
    comparison_period: Dict[str, Any] = Field(..., description="对比周期数据")
    changes: Dict[str, Any] = Field(..., description="变化情况")
    performance_indicators: Dict[str, Any] = Field(..., description="表现指标")
    ranking_changes: Optional[List[Dict[str, Any]]] = Field(None, description="排名变化")
    insights: List[str] = Field(default_factory=list, description="对比洞察")
    charts: List[ChartData] = Field(default_factory=list, description="对比图表")

# 综合统计报告
class ComprehensiveStatisticsReport(BaseModel):
    """综合统计报告"""
    report_id: str = Field(..., description="报告ID")
    period: str = Field(..., description="统计周期")
    generated_at: datetime = Field(..., description="生成时间")
    overview: OverviewStatistics = Field(..., description="总览统计")
    cards_stats: CardsStatistics = Field(..., description="信用卡统计")
    transactions_stats: TransactionsStatistics = Field(..., description="交易统计")
    annual_fees_stats: AnnualFeesStatistics = Field(..., description="年费统计")
    trends: List[TrendAnalysis] = Field(default_factory=list, description="趋势分析")
    comparisons: List[ComparisonAnalysis] = Field(default_factory=list, description="对比分析")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
    risk_alerts: List[str] = Field(default_factory=list, description="风险提醒")

# 自定义报表配置
class CustomReportConfig(BaseModel):
    """自定义报表配置"""
    name: str = Field(..., max_length=100, description="报表名称")
    description: Optional[str] = Field(None, max_length=500, description="报表描述")
    statistics_types: List[StatisticsType] = Field(..., description="包含的统计类型")
    default_period: StatisticsPeriod = Field(..., description="默认统计周期")
    filters: Dict[str, Any] = Field(default_factory=dict, description="默认筛选条件")
    charts: List[str] = Field(default_factory=list, description="包含的图表类型")
    auto_generate: bool = Field(False, description="是否自动生成")
    schedule: Optional[str] = Field(None, description="生成计划（cron表达式）")
    recipients: List[str] = Field(default_factory=list, description="接收人邮箱列表")

# 自定义报表
class CustomReport(BaseModel):
    """自定义报表"""
    id: UUID = Field(..., description="报表ID")
    name: str = Field(..., description="报表名称")
    config: CustomReportConfig = Field(..., description="报表配置")
    data: Dict[str, Any] = Field(..., description="报表数据")
    generated_at: datetime = Field(..., description="生成时间")
    file_url: Optional[str] = Field(None, description="报表文件URL")

# 财务健康度评估
class FinancialHealthAssessment(BaseModel):
    """财务健康度评估"""
    overall_score: int = Field(..., ge=0, le=100, description="总体评分")
    category_scores: Dict[str, int] = Field(..., description="分类评分")
    strengths: List[str] = Field(default_factory=list, description="优势领域")
    weaknesses: List[str] = Field(default_factory=list, description="薄弱环节")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
    risk_level: str = Field(..., description="风险等级：low/medium/high")
    benchmark_comparison: Dict[str, Any] = Field(..., description="基准对比")
    improvement_plan: List[Dict[str, Any]] = Field(default_factory=list, description="改进计划")

# 支出模式分析
class SpendingPatternAnalysis(BaseModel):
    """支出模式分析"""
    pattern_type: str = Field(..., description="模式类型")
    description: str = Field(..., description="模式描述")
    frequency: float = Field(..., description="出现频率")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    seasonal_indicators: Dict[str, Any] = Field(default_factory=dict, description="季节性指标")
    triggers: List[str] = Field(default_factory=list, description="触发因素")
    impact_analysis: Dict[str, Any] = Field(..., description="影响分析")
    recommendations: List[str] = Field(default_factory=list, description="建议")

# 异常检测结果
class AnomalyDetectionResult(BaseModel):
    """异常检测结果"""
    anomaly_type: str = Field(..., description="异常类型")
    detected_at: datetime = Field(..., description="检测时间")
    severity: str = Field(..., description="严重程度：low/medium/high/critical")
    description: str = Field(..., description="异常描述")
    affected_data: Dict[str, Any] = Field(..., description="受影响的数据")
    confidence_score: float = Field(..., ge=0, le=1, description="置信度")
    suggested_actions: List[str] = Field(default_factory=list, description="建议操作")
    historical_context: Optional[Dict[str, Any]] = Field(None, description="历史背景")

# 绩效指标
class PerformanceMetrics(BaseModel):
    """绩效指标"""
    metric_name: str = Field(..., description="指标名称")
    current_value: Union[float, int, Decimal] = Field(..., description="当前值")
    target_value: Optional[Union[float, int, Decimal]] = Field(None, description="目标值")
    previous_value: Optional[Union[float, int, Decimal]] = Field(None, description="上期值")
    unit: str = Field(..., description="单位")
    performance_level: str = Field(..., description="绩效水平：excellent/good/average/poor")
    improvement_rate: Optional[float] = Field(None, description="改进率")
    ranking: Optional[int] = Field(None, description="排名")
    benchmark: Optional[Union[float, int, Decimal]] = Field(None, description="基准值")

# 数据导出配置
class DataExportConfig(BaseModel):
    """数据导出配置"""
    export_format: str = Field(..., description="导出格式：excel/csv/pdf/json")
    include_charts: bool = Field(True, description="是否包含图表")
    include_raw_data: bool = Field(False, description="是否包含原始数据")
    date_range: Dict[str, date] = Field(..., description="日期范围")
    filters: Dict[str, Any] = Field(default_factory=dict, description="筛选条件")
    columns: Optional[List[str]] = Field(None, description="指定列（CSV格式）")
    template: Optional[str] = Field(None, description="模板名称")

# 数据导出响应
class DataExportResponse(BaseModel):
    """数据导出响应"""
    export_id: str = Field(..., description="导出任务ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    download_url: str = Field(..., description="下载链接")
    expires_at: datetime = Field(..., description="链接过期时间")
    generated_at: datetime = Field(..., description="生成时间")
    record_count: int = Field(..., description="记录数量")

# 实时统计
class RealTimeStatistics(BaseModel):
    """实时统计"""
    timestamp: datetime = Field(..., description="时间戳")
    active_cards: int = Field(0, description="活跃卡片数")
    today_transactions: int = Field(0, description="今日交易数")
    today_spending: Decimal = Field(Decimal("0"), description="今日支出")
    pending_fees: int = Field(0, description="待缴年费数")
    overdue_fees: int = Field(0, description="逾期年费数")
    alerts_count: int = Field(0, description="提醒数量")
    system_health: str = Field("healthy", description="系统健康状态")
    last_sync: datetime = Field(..., description="最后同步时间")

# 统计汇总响应
class StatisticsSummaryResponse(BaseModel):
    """统计汇总响应"""
    request_id: str = Field(..., description="请求ID")
    statistics_type: StatisticsType = Field(..., description="统计类型")
    period: str = Field(..., description="统计周期")
    data: Union[
        OverviewStatistics,
        CardsStatistics, 
        TransactionsStatistics,
        AnnualFeesStatistics,
        ComparisonAnalysis,
        TrendAnalysis
    ] = Field(..., description="统计数据")
    generated_at: datetime = Field(..., description="生成时间")
    cache_expires_at: Optional[datetime] = Field(None, description="缓存过期时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
# 统计仪表板数据
class DashboardData(BaseModel):
    """统计仪表板数据"""
    overview: Dict[str, Any] = Field(..., description="概览数据")
    quick_stats: List[Dict[str, Any]] = Field(..., description="快速统计")
    charts: List[ChartData] = Field(..., description="图表数据")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="提醒信息")
    recent_activities: List[Dict[str, Any]] = Field(default_factory=list, description="最近活动")
    performance_indicators: List[PerformanceMetrics] = Field(default_factory=list, description="绩效指标")
    last_updated: datetime = Field(..., description="最后更新时间") 