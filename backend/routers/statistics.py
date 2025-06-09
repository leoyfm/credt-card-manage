"""
统计路由

提供统计相关的API接口。
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from services.statistics import StatisticsService
from models.statistics import (
    OverallStatistics, DetailedStatisticsQuery, 
    CardStatistics, CreditLimitStatistics, TransactionStatistics,
    AnnualFeeStatistics, CategoryStatistics, MonthlyStatistics, BankStatistics
)
from models.response import ApiResponse, ApiPagedResponse
from utils.response import ResponseUtil
from db_models.users import User
from models.users import UserProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statistics", tags=["统计分析"])


def get_statistics_service(db: Session = Depends(get_db)) -> StatisticsService:
    """获取统计服务实例"""
    return StatisticsService(db)


@router.get(
    "/overview",
    response_model=ApiResponse[OverallStatistics],
    summary="获取统计概览",
    response_description="返回包括信用卡、额度、交易、年费等全方位的统计数据"
)
async def get_statistics_overview(
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD，可选筛选时间范围", examples=["2024-01-01"]),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD，可选筛选时间范围", examples=["2024-12-31"]),
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    card_id: Optional[str] = Query(None, description="信用卡ID，可选筛选特定信用卡", examples=["123e4567-e89b-12d3-a456-426614174000"]),
    include_cancelled: bool = Query(False, description="是否包含已注销的信用卡", examples=[False]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[OverallStatistics]:
    """
    获取统计概览
    
    包括以下统计数据：
    - 信用卡统计：总数、状态分布
    - 信用额度统计：总额度、使用情况、利用率
    - 交易统计：交易笔数、金额、积分
    - 年费统计：年费总额、减免情况
    - 银行分布统计
    """
    try:
        logger.info(f"用户 {current_user.id} 请求统计概览")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            start_date=start_date,
            end_date=end_date,
            bank_name=bank_name,
            card_id=card_id,
            include_cancelled=include_cancelled
        )
        
        # 获取统计数据
        overview_stats = await service.get_overall_statistics(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(overview_stats, "获取统计概览成功")
        
    except Exception as e:
        logger.error(f"获取统计概览失败: {str(e)}")
        return ResponseUtil.error(f"获取统计概览失败: {str(e)}")


@router.get(
    "/cards",
    response_model=ApiResponse[CardStatistics],
    summary="获取信用卡统计",
    response_description="返回信用卡数量及状态分布统计"
)
async def get_card_statistics(
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    include_cancelled: bool = Query(False, description="是否包含已注销的信用卡", examples=[False]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[CardStatistics]:
    """
    获取信用卡统计信息
    
    包括：
    - 总卡数
    - 激活卡数
    - 未激活卡数  
    - 冻结卡数
    - 已注销卡数
    - 过期卡数
    - 即将过期卡数
    """
    try:
        logger.info(f"用户 {current_user.id} 请求信用卡统计信息")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            bank_name=bank_name,
            include_cancelled=include_cancelled
        )
        
        # 获取统计数据
        card_stats = await service.get_card_statistics(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(card_stats, "获取信用卡统计成功")
        
    except Exception as e:
        logger.error(f"获取信用卡统计失败: {str(e)}")
        return ResponseUtil.error(f"获取信用卡统计失败: {str(e)}")


@router.get(
    "/credit-limit",
    response_model=ApiResponse[CreditLimitStatistics],
    summary="获取信用额度统计",
    response_description="返回信用额度使用情况及利用率统计"
)
async def get_credit_limit_statistics(
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    include_cancelled: bool = Query(False, description="是否包含已注销的信用卡", examples=[False]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[CreditLimitStatistics]:
    """
    获取信用额度统计信息
    
    包括：
    - 总信用额度
    - 已使用金额
    - 可用金额
    - 整体利用率
    - 最高利用率
    - 最低利用率
    - 平均利用率
    """
    try:
        logger.info(f"用户 {current_user.id} 请求信用额度统计信息")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            bank_name=bank_name,
            include_cancelled=include_cancelled
        )
        
        # 获取统计数据
        credit_stats = await service.get_credit_limit_statistics(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(credit_stats, "获取信用额度统计成功")
        
    except Exception as e:
        logger.error(f"获取信用额度统计失败: {str(e)}")
        return ResponseUtil.error(f"获取信用额度统计失败: {str(e)}")


@router.get(
    "/transactions",
    response_model=ApiResponse[TransactionStatistics],
    summary="获取交易统计",
    response_description="返回交易笔数、金额及积分统计"
)
async def get_transaction_statistics(
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD", examples=["2024-01-01"]),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD", examples=["2024-12-31"]),
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    card_id: Optional[str] = Query(None, description="信用卡ID，可选筛选特定信用卡", examples=["123e4567-e89b-12d3-a456-426614174000"]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[TransactionStatistics]:
    """
    获取交易统计信息
    
    包括：
    - 总交易笔数
    - 总消费金额  
    - 总还款金额
    - 总积分收入
    - 本月交易统计
    - 平均交易金额
    """
    try:
        logger.info(f"用户 {current_user.id} 请求交易统计信息")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            start_date=start_date,
            end_date=end_date,
            bank_name=bank_name,
            card_id=card_id
        )
        
        # 获取统计数据
        transaction_stats = await service.get_transaction_statistics(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(transaction_stats, "获取交易统计成功")
        
    except Exception as e:
        logger.error(f"获取交易统计失败: {str(e)}")
        return ResponseUtil.error(f"获取交易统计失败: {str(e)}")


@router.get(
    "/annual-fee",
    response_model=ApiResponse[AnnualFeeStatistics],
    summary="获取年费统计",
    response_description="返回年费缴费情况及减免统计"
)
async def get_annual_fee_statistics(
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    include_cancelled: bool = Query(False, description="是否包含已注销的信用卡", examples=[False]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[AnnualFeeStatistics]:
    """
    获取年费统计信息
    
    包括：
    - 年费总额
    - 减免次数
    - 待缴费次数
    - 已缴费次数
    - 逾期次数
    - 本年度应缴费用
    - 减免节省金额
    """
    try:
        logger.info(f"用户 {current_user.id} 请求年费统计信息")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            bank_name=bank_name,
            include_cancelled=include_cancelled
        )
        
        # 获取统计数据
        annual_fee_stats = await service.get_annual_fee_statistics(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(annual_fee_stats, "获取年费统计成功")
        
    except Exception as e:
        logger.error(f"获取年费统计失败: {str(e)}")
        return ResponseUtil.error(f"获取年费统计失败: {str(e)}")


@router.get(
    "/categories",
    response_model=ApiResponse[List[CategoryStatistics]],
    summary="获取消费分类统计",
    response_description="返回按消费类别统计的支出分布"
)
async def get_category_statistics(
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD", examples=["2024-01-01"]),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD", examples=["2024-12-31"]),
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    card_id: Optional[str] = Query(None, description="信用卡ID，可选筛选特定信用卡", examples=["123e4567-e89b-12d3-a456-426614174000"]),
    limit: int = Query(10, ge=1, le=20, description="返回前N个分类，最大20", examples=[10]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[List[CategoryStatistics]]:
    """
    获取消费分类统计
    
    按消费类别统计支出金额和占比，包括：
    - 分类代码和名称
    - 交易笔数
    - 总金额
    - 占比百分比
    
    支持的分类：
    - dining: 餐饮美食
    - shopping: 购物消费  
    - transportation: 交通出行
    - entertainment: 娱乐休闲
    - healthcare: 医疗健康
    - education: 教育培训
    - travel: 旅游度假
    - utilities: 生活缴费
    - other: 其他消费
    """
    try:
        logger.info(f"用户 {current_user.id} 请求消费分类统计")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            start_date=start_date,
            end_date=end_date,
            bank_name=bank_name,
            card_id=card_id
        )
        
        # 获取统计数据
        category_stats = await service.get_category_statistics(
            user_id=str(current_user.id),
            query=query,
            limit=limit
        )
        
        return ResponseUtil.success(category_stats, "获取消费分类统计成功")
        
    except Exception as e:
        logger.error(f"获取消费分类统计失败: {str(e)}")
        return ResponseUtil.error(f"获取消费分类统计失败: {str(e)}")


@router.get(
    "/monthly-trends",
    response_model=ApiResponse[List[MonthlyStatistics]],
    summary="获取月度统计趋势",
    response_description="返回按月统计的交易趋势数据"
)
async def get_monthly_trends(
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD，默认为最近12个月", examples=["2024-01-01"]),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD，默认为当前月", examples=["2024-12-31"]),
    bank_name: Optional[str] = Query(None, description="银行名称，可选筛选特定银行", examples=["招商银行"]),
    card_id: Optional[str] = Query(None, description="信用卡ID，可选筛选特定信用卡", examples=["123e4567-e89b-12d3-a456-426614174000"]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[List[MonthlyStatistics]]:
    """
    获取月度统计趋势
    
    按月份统计交易数据，包括：
    - 年月(YYYY-MM格式)
    - 交易笔数
    - 消费金额
    - 还款金额
    - 积分收入
    
    默认返回最近12个月的数据，可通过日期参数自定义时间范围
    """
    try:
        logger.info(f"用户 {current_user.id} 请求月度统计趋势")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            start_date=start_date,
            end_date=end_date,
            bank_name=bank_name,
            card_id=card_id
        )
        
        # 获取统计数据
        monthly_trends = await service.get_monthly_trends(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(monthly_trends, "获取月度统计趋势成功")
        
    except Exception as e:
        logger.error(f"获取月度统计趋势失败: {str(e)}")
        return ResponseUtil.error(f"获取月度统计趋势失败: {str(e)}")


@router.get(
    "/banks",
    response_model=ApiResponse[List[BankStatistics]],
    summary="获取银行分布统计",
    response_description="返回按银行统计的信用卡分布和使用情况"
)
async def get_bank_statistics(
    include_cancelled: bool = Query(False, description="是否包含已注销的信用卡", examples=[False]),
    current_user: UserProfile = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
) -> ApiResponse[List[BankStatistics]]:
    """
    获取银行分布统计
    
    按银行统计信用卡分布和使用情况，包括：
    - 银行名称
    - 信用卡数量
    - 总信用额度
    - 已使用金额
    - 利用率
    
    帮助了解在各银行的信用卡分布和使用情况
    """
    try:
        logger.info(f"用户 {current_user.id} 请求银行分布统计")
        
        # 构建查询条件
        query = DetailedStatisticsQuery(
            include_cancelled=include_cancelled
        )
        
        # 获取统计数据
        bank_stats = await service.get_bank_statistics(
            user_id=str(current_user.id),
            query=query
        )
        
        return ResponseUtil.success(bank_stats, "获取银行分布统计成功")
        
    except Exception as e:
        logger.error(f"获取银行分布统计失败: {str(e)}")
        return ResponseUtil.error(f"获取银行分布统计失败: {str(e)}") 