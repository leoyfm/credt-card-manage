"""
用户功能区 - 统计分析接口

本模块提供用户个人数据统计分析的所有接口：
- 综合统计报告
- 趋势分析
- 对比分析
- 自定义报表

权限等级: Level 2 (用户认证)
数据范围: 仅自有统计数据

作者: LEO
邮箱: leoyfm@gmail.com
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.schemas.user import UserProfile
from app.models.schemas.statistics import (
    StatisticsQueryRequest, StatisticsSummaryResponse,
    OverviewStatistics, CardsStatistics, TransactionsStatistics, AnnualFeesStatistics,
    TrendAnalysis, ComparisonAnalysis, ComprehensiveStatisticsReport,
    CustomReportConfig, CustomReport, FinancialHealthAssessment,
    SpendingPatternAnalysis, AnomalyDetectionResult, PerformanceMetrics,
    DataExportConfig, DataExportResponse, RealTimeStatistics, DashboardData
)
from app.models.schemas.common import ApiResponse, SuccessMessage
from app.services.statistics_service import StatisticsService
from app.utils.response import ResponseUtil

# 配置日志和路由
logger = get_logger(__name__)
router = APIRouter(
    prefix="/statistics",
    tags=["v1-用户-统计分析"]
)

@router.get(
    "/dashboard",
    response_model=ApiResponse[DashboardData],
    summary="获取统计仪表板数据",
    response_description="返回用户统计仪表板的综合数据"
)
async def get_dashboard_data(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取统计仪表板数据
    
    提供仪表板综合视图：
    - 关键指标概览
    - 实时统计数据
    - 重要提醒信息
    - 趋势图表展示
    - 最近活动记录
    
    为用户提供一目了然的数据洞察
    """
    try:
        logger.info("用户查看统计仪表板", 
                   user_id=current_user.id, 
                   username=current_user.username)
        
        statistics_service = StatisticsService(db)
        dashboard_data = statistics_service.get_user_dashboard_data(current_user.id)
        
        return ResponseUtil.success(
            data=dashboard_data,
            message="获取仪表板数据成功"
        )
        
    except Exception as e:
        logger.error("获取仪表板数据异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取仪表板数据失败，请稍后重试")


@router.get(
    "/overview",
    response_model=ApiResponse[OverviewStatistics],
    summary="获取总览统计",
    response_description="返回用户数据的总览统计"
)
async def get_overview_statistics(
    period: str = Query("current_month", description="统计周期：current_month, last_month, current_year, last_year, custom"),
    start_date: Optional[date] = Query(None, description="开始日期（period=custom时必需）"),
    end_date: Optional[date] = Query(None, description="结束日期（period=custom时必需）"),
    include_charts: bool = Query(True, description="是否包含图表数据"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取总览统计
    
    提供全方位数据概览：
    - 信用卡、交易、年费摘要
    - 财务健康度评估
    - 关键洞察和发现
    - 可视化图表数据
    
    支持多种时间周期分析
    """
    try:
        logger.info("用户查看总览统计", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   period=period)
        
        statistics_service = StatisticsService(db)
        overview_stats = statistics_service.get_user_overview_statistics(
            user_id=current_user.id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            include_charts=include_charts
        )
        
        return ResponseUtil.success(
            data=overview_stats,
            message="获取总览统计成功"
        )
        
    except ValueError as e:
        logger.warning("获取总览统计参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取总览统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取总览统计失败，请稍后重试")


@router.get(
    "/cards",
    response_model=ApiResponse[CardsStatistics],
    summary="获取信用卡统计",
    response_description="返回信用卡相关的统计数据"
)
async def get_cards_statistics(
    period: str = Query("current_month", description="统计周期"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    card_ids: Optional[str] = Query(None, description="筛选的信用卡ID，多个用逗号分隔"),
    include_charts: bool = Query(True, description="是否包含图表数据"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取信用卡统计
    
    提供信用卡深度分析：
    - 卡片数量和状态分布
    - 信用额度和利用率
    - 按银行、等级、网络分组
    - 过期提醒和表现排名
    
    支持多卡片筛选和对比
    """
    try:
        logger.info("用户查看信用卡统计", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   period=period)
        
        statistics_service = StatisticsService(db)
        
        # 解析卡片ID列表
        card_id_list = []
        if card_ids:
            try:
                card_id_list = [UUID(id.strip()) for id in card_ids.split(",")]
            except ValueError:
                return ResponseUtil.validation_error("无效的信用卡ID格式")
        
        cards_stats = statistics_service.get_user_cards_statistics(
            user_id=current_user.id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            card_ids=card_id_list,
            include_charts=include_charts
        )
        
        return ResponseUtil.success(
            data=cards_stats,
            message="获取信用卡统计成功"
        )
        
    except ValueError as e:
        logger.warning("获取信用卡统计参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取信用卡统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取信用卡统计失败，请稍后重试")


@router.get(
    "/transactions",
    response_model=ApiResponse[TransactionsStatistics],
    summary="获取交易统计",
    response_description="返回交易相关的统计数据"
)
async def get_transactions_statistics(
    period: str = Query("current_month", description="统计周期"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    card_ids: Optional[str] = Query(None, description="筛选的信用卡ID"),
    category_ids: Optional[str] = Query(None, description="筛选的分类ID"),
    include_charts: bool = Query(True, description="是否包含图表数据"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取交易统计
    
    提供交易深度分析：
    - 收支统计和净额计算
    - 按类型、分类、商户分组
    - 消费趋势和热门分类
    - 日均支出和单笔分析
    
    支持灵活的筛选条件
    """
    try:
        logger.info("用户查看交易统计", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   period=period)
        
        statistics_service = StatisticsService(db)
        
        # 解析筛选ID列表
        card_id_list = []
        category_id_list = []
        
        if card_ids:
            try:
                card_id_list = [UUID(id.strip()) for id in card_ids.split(",")]
            except ValueError:
                return ResponseUtil.validation_error("无效的信用卡ID格式")
        
        if category_ids:
            try:
                category_id_list = [UUID(id.strip()) for id in category_ids.split(",")]
            except ValueError:
                return ResponseUtil.validation_error("无效的分类ID格式")
        
        transactions_stats = statistics_service.get_user_transactions_statistics(
            user_id=current_user.id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            card_ids=card_id_list,
            category_ids=category_id_list,
            include_charts=include_charts
        )
        
        return ResponseUtil.success(
            data=transactions_stats,
            message="获取交易统计成功"
        )
        
    except ValueError as e:
        logger.warning("获取交易统计参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取交易统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取交易统计失败，请稍后重试")


@router.get(
    "/annual-fees",
    response_model=ApiResponse[AnnualFeesStatistics],
    summary="获取年费统计",
    response_description="返回年费相关的统计数据"
)
async def get_annual_fees_statistics(
    year: Optional[int] = Query(None, description="统计年度，默认当前年度"),
    card_ids: Optional[str] = Query(None, description="筛选的信用卡ID"),
    include_charts: bool = Query(True, description="是否包含图表数据"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取年费统计
    
    提供年费全面分析：
    - 年费总额和缴费状态
    - 减免成功率分析
    - 按类型、银行、状态分组
    - 即将到期提醒
    - 优化机会识别
    
    支持年度对比分析
    """
    try:
        logger.info("用户查看年费统计", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   year=year)
        
        statistics_service = StatisticsService(db)
        
        # 解析卡片ID列表
        card_id_list = []
        if card_ids:
            try:
                card_id_list = [UUID(id.strip()) for id in card_ids.split(",")]
            except ValueError:
                return ResponseUtil.validation_error("无效的信用卡ID格式")
        
        annual_fees_stats = statistics_service.get_user_annual_fees_statistics(
            user_id=current_user.id,
            year=year,
            card_ids=card_id_list,
            include_charts=include_charts
        )
        
        return ResponseUtil.success(
            data=annual_fees_stats,
            message="获取年费统计成功"
        )
        
    except ValueError as e:
        logger.warning("获取年费统计参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取年费统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费统计失败，请稍后重试")


@router.get(
    "/trends",
    response_model=ApiResponse[List[TrendAnalysis]],
    summary="获取趋势分析",
    response_description="返回数据趋势分析结果"
)
async def get_trend_analysis(
    metric_types: str = Query("spending,income,fees", description="分析指标类型，多个用逗号分隔"),
    period_type: str = Query("monthly", description="周期类型：daily, weekly, monthly, quarterly"),
    periods_count: int = Query(12, ge=3, le=60, description="分析周期数量"),
    include_forecast: bool = Query(True, description="是否包含预测数据"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取趋势分析
    
    提供数据趋势深度分析：
    - 支出、收入、年费趋势
    - 趋势方向和强度评估
    - 季节性模式识别
    - 未来数据预测
    - 趋势洞察和建议
    
    支持多指标对比分析
    """
    try:
        logger.info("用户查看趋势分析", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   metric_types=metric_types,
                   period_type=period_type)
        
        statistics_service = StatisticsService(db)
        
        # 解析指标类型
        metric_type_list = [metric.strip() for metric in metric_types.split(",")]
        
        trend_analyses = statistics_service.get_user_trend_analysis(
            user_id=current_user.id,
            metric_types=metric_type_list,
            period_type=period_type,
            periods_count=periods_count,
            include_forecast=include_forecast
        )
        
        return ResponseUtil.success(
            data=trend_analyses,
            message="获取趋势分析成功"
        )
        
    except ValueError as e:
        logger.warning("获取趋势分析参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取趋势分析异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取趋势分析失败，请稍后重试")


@router.get(
    "/comparison",
    response_model=ApiResponse[ComparisonAnalysis],
    summary="获取对比分析",
    response_description="返回数据对比分析结果"
)
async def get_comparison_analysis(
    comparison_type: str = Query("period_over_period", description="对比类型：period_over_period, year_over_year"),
    current_period: str = Query("current_month", description="当前周期"),
    comparison_period: str = Query("last_month", description="对比周期"),
    metrics: str = Query("spending,transactions,fees", description="对比指标，多个用逗号分隔"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取对比分析
    
    提供多维度对比分析：
    - 期间对比分析
    - 同比环比分析
    - 绩效指标对比
    - 排名变化分析
    - 对比洞察和建议
    
    帮助用户了解数据变化趋势
    """
    try:
        logger.info("用户查看对比分析", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   comparison_type=comparison_type)
        
        statistics_service = StatisticsService(db)
        
        # 解析对比指标
        metric_list = [metric.strip() for metric in metrics.split(",")]
        
        comparison_analysis = statistics_service.get_user_comparison_analysis(
            user_id=current_user.id,
            comparison_type=comparison_type,
            current_period=current_period,
            comparison_period=comparison_period,
            metrics=metric_list
        )
        
        return ResponseUtil.success(
            data=comparison_analysis,
            message="获取对比分析成功"
        )
        
    except ValueError as e:
        logger.warning("获取对比分析参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取对比分析异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取对比分析失败，请稍后重试")


@router.get(
    "/comprehensive-report",
    response_model=ApiResponse[ComprehensiveStatisticsReport],
    summary="获取综合统计报告",
    response_description="返回完整的综合统计报告"
)
async def get_comprehensive_report(
    period: str = Query("current_month", description="报告周期"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    include_trends: bool = Query(True, description="是否包含趋势分析"),
    include_comparisons: bool = Query(True, description="是否包含对比分析"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取综合统计报告
    
    提供最全面的数据报告：
    - 所有模块统计数据
    - 趋势和对比分析
    - 关键发现和洞察
    - 改进建议和风险提醒
    - 完整的可视化图表
    
    适用于全面的数据回顾和决策支持
    """
    try:
        logger.info("用户生成综合统计报告", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   period=period)
        
        statistics_service = StatisticsService(db)
        comprehensive_report = statistics_service.generate_comprehensive_report(
            user_id=current_user.id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            include_trends=include_trends,
            include_comparisons=include_comparisons
        )
        
        return ResponseUtil.success(
            data=comprehensive_report,
            message="生成综合统计报告成功"
        )
        
    except ValueError as e:
        logger.warning("生成综合统计报告参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("生成综合统计报告异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("生成综合统计报告失败，请稍后重试")


@router.get(
    "/financial-health",
    response_model=ApiResponse[FinancialHealthAssessment],
    summary="获取财务健康度评估",
    response_description="返回财务健康度评估结果"
)
async def get_financial_health_assessment(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取财务健康度评估
    
    提供全面的财务健康分析：
    - 总体评分和分类评分
    - 优势领域和薄弱环节
    - 风险等级评估
    - 基准对比分析
    - 个性化改进建议
    
    帮助用户了解和改善财务状况
    """
    try:
        logger.info("用户查看财务健康度评估", 
                   user_id=current_user.id, 
                   username=current_user.username)
        
        statistics_service = StatisticsService(db)
        health_assessment = statistics_service.get_user_financial_health_assessment(
            user_id=current_user.id
        )
        
        return ResponseUtil.success(
            data=health_assessment,
            message="获取财务健康度评估成功"
        )
        
    except Exception as e:
        logger.error("获取财务健康度评估异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取财务健康度评估失败，请稍后重试")


@router.get(
    "/spending-patterns",
    response_model=ApiResponse[List[SpendingPatternAnalysis]],
    summary="获取支出模式分析",
    response_description="返回支出模式分析结果"
)
async def get_spending_patterns(
    analysis_period: int = Query(12, ge=3, le=24, description="分析周期数（月）"),
    pattern_types: Optional[str] = Query(None, description="模式类型筛选，多个用逗号分隔"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取支出模式分析
    
    提供智能支出模式识别：
    - 消费习惯模式识别
    - 季节性和周期性分析
    - 触发因素识别
    - 影响分析和建议
    - 模式置信度评估
    
    帮助用户了解和优化消费行为
    """
    try:
        logger.info("用户查看支出模式分析", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   analysis_period=analysis_period)
        
        statistics_service = StatisticsService(db)
        
        # 解析模式类型
        pattern_type_list = []
        if pattern_types:
            pattern_type_list = [ptype.strip() for ptype in pattern_types.split(",")]
        
        spending_patterns = statistics_service.get_user_spending_patterns(
            user_id=current_user.id,
            analysis_period=analysis_period,
            pattern_types=pattern_type_list
        )
        
        return ResponseUtil.success(
            data=spending_patterns,
            message="获取支出模式分析成功"
        )
        
    except ValueError as e:
        logger.warning("获取支出模式分析参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取支出模式分析异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取支出模式分析失败，请稍后重试")


@router.get(
    "/anomalies",
    response_model=ApiResponse[List[AnomalyDetectionResult]],
    summary="获取异常检测结果",
    response_description="返回数据异常检测结果"
)
async def get_anomaly_detection(
    detection_period: int = Query(90, ge=30, le=365, description="检测周期（天）"),
    severity_filter: Optional[str] = Query(None, description="严重程度筛选：low, medium, high, critical"),
    anomaly_types: Optional[str] = Query(None, description="异常类型筛选，多个用逗号分隔"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取异常检测结果
    
    提供智能异常检测：
    - 支出异常检测
    - 模式变化检测
    - 风险行为识别
    - 严重程度评估
    - 处理建议提供
    
    帮助用户及时发现和处理异常情况
    """
    try:
        logger.info("用户查看异常检测结果", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   detection_period=detection_period)
        
        statistics_service = StatisticsService(db)
        
        # 解析异常类型
        anomaly_type_list = []
        if anomaly_types:
            anomaly_type_list = [atype.strip() for atype in anomaly_types.split(",")]
        
        anomaly_results = statistics_service.get_user_anomaly_detection(
            user_id=current_user.id,
            detection_period=detection_period,
            severity_filter=severity_filter,
            anomaly_types=anomaly_type_list
        )
        
        return ResponseUtil.success(
            data=anomaly_results,
            message="获取异常检测结果成功"
        )
        
    except ValueError as e:
        logger.warning("获取异常检测结果参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取异常检测结果异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取异常检测结果失败，请稍后重试")


@router.post(
    "/export",
    response_model=ApiResponse[DataExportResponse],
    summary="导出统计数据",
    response_description="返回数据导出任务信息"
)
async def export_statistics_data(
    export_config: DataExportConfig,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    导出统计数据
    
    支持多种格式导出：
    - Excel、CSV、PDF、JSON格式
    - 包含图表和原始数据
    - 自定义日期范围和筛选
    - 灵活的导出配置
    
    方便用户进行数据备份和分析
    """
    try:
        logger.info("用户导出统计数据", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   export_format=export_config.export_format)
        
        statistics_service = StatisticsService(db)
        export_result = statistics_service.export_user_statistics_data(
            user_id=current_user.id,
            export_config=export_config
        )
        
        logger.info("用户导出统计数据成功", 
                   user_id=current_user.id,
                   export_id=export_result.export_id,
                   file_name=export_result.file_name)
        
        return ResponseUtil.success(
            data=export_result,
            message=f"数据导出任务创建成功，文件：{export_result.file_name}"
        )
        
    except ValueError as e:
        logger.warning("导出统计数据参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("导出统计数据异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("导出统计数据失败，请稍后重试")


@router.get(
    "/real-time",
    response_model=ApiResponse[RealTimeStatistics],
    summary="获取实时统计",
    response_description="返回实时统计数据"
)
async def get_real_time_statistics(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取实时统计
    
    提供实时数据更新：
    - 今日交易和支出
    - 活跃卡片状态
    - 待处理提醒
    - 系统健康状态
    
    适用于频繁更新的数据监控
    """
    try:
        logger.info("用户查看实时统计", 
                   user_id=current_user.id, 
                   username=current_user.username)
        
        statistics_service = StatisticsService(db)
        real_time_stats = statistics_service.get_user_real_time_statistics(
            user_id=current_user.id
        )
        
        return ResponseUtil.success(
            data=real_time_stats,
            message="获取实时统计成功"
        )
        
    except Exception as e:
        logger.error("获取实时统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取实时统计失败，请稍后重试") 