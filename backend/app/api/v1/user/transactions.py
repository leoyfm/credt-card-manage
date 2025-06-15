"""
用户交易管理API路由
提供交易记录的增删改查、统计分析、分类管理等功能
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.models.database.user import User
from app.models.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionStatisticsResponse, CategoryStatisticsResponse,
    MonthlyTrendResponse, TransactionCategoryResponse
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse
from app.api.dependencies.services import get_transaction_service
from app.services.transaction_service import TransactionService
from app.utils.response import ResponseUtil
from app.core.logging.logger import app_logger as logger

router = APIRouter(prefix="/transactions", tags=["用户-交易管理"])


@router.post(
    "/create",
    response_model=ApiResponse[TransactionResponse],
    summary="创建交易记录",
    description="创建新的交易记录，支持消费、收入、退款等类型"
)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """创建交易记录"""
    try:
        transaction = transaction_service.create_transaction(current_user.id, transaction_data)
        
        logger.info(f"用户 {current_user.username} 创建交易记录成功: {transaction.id}")
        return ResponseUtil.success(
            data=transaction,
            message="交易记录创建成功"
        )
    except Exception as e:
        logger.error(f"创建交易记录失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/list",
    response_model=ApiPagedResponse[TransactionResponse],
    summary="获取交易记录列表",
    description="获取当前用户的交易记录列表，支持分页、筛选和搜索"
)
async def get_transactions(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    card_id: Optional[UUID] = Query(None, description="信用卡ID筛选"),
    category_id: Optional[UUID] = Query(None, description="分类ID筛选"),
    transaction_type: Optional[str] = Query(None, description="交易类型筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    keyword: Optional[str] = Query("", description="关键词搜索（描述、商户、地点、备注）"),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """获取交易记录列表"""
    try:
        transactions, total = transaction_service.get_user_transactions(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            card_id=card_id,
            category_id=category_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            keyword=keyword
        )
        
        return ResponseUtil.paginated(
            items=transactions,
            total=total,
            page=page,
            page_size=page_size,
            message="获取交易记录列表成功"
        )
    except Exception as e:
        logger.error(f"获取交易记录列表失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{transaction_id}/details",
    response_model=ApiResponse[TransactionResponse],
    summary="获取交易记录详情",
    description="根据交易ID获取详细的交易记录信息"
)
async def get_transaction_details(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """获取交易记录详情"""
    try:
        transaction = transaction_service.get_transaction(current_user.id, transaction_id)
        
        return ResponseUtil.success(
            data=transaction,
            message="获取交易记录详情成功"
        )
    except Exception as e:
        logger.error(f"获取交易记录详情失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{transaction_id}/update",
    response_model=ApiResponse[TransactionResponse],
    summary="更新交易记录",
    description="更新指定的交易记录信息"
)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """更新交易记录"""
    try:
        transaction = transaction_service.update_transaction(current_user.id, transaction_id, transaction_data)
        
        logger.info(f"用户 {current_user.username} 更新交易记录成功: {transaction_id}")
        return ResponseUtil.success(
            data=transaction,
            message="交易记录更新成功"
        )
    except Exception as e:
        logger.error(f"更新交易记录失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{transaction_id}/delete",
    response_model=ApiResponse[bool],
    summary="删除交易记录",
    description="删除指定的交易记录"
)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """删除交易记录"""
    try:
        success = transaction_service.delete_transaction(current_user.id, transaction_id)
        
        logger.info(f"用户 {current_user.username} 删除交易记录成功: {transaction_id}")
        return ResponseUtil.success(
            data=success,
            message="交易记录删除成功"
        )
    except Exception as e:
        logger.error(f"删除交易记录失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/statistics/overview",
    response_model=ApiResponse[TransactionStatisticsResponse],
    summary="获取交易统计概览",
    description="获取指定时间范围内的交易统计数据，包括总额、笔数、积分等"
)
async def get_transaction_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期，默认30天前"),
    end_date: Optional[datetime] = Query(None, description="结束日期，默认今天"),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """获取交易统计概览"""
    try:
        statistics = transaction_service.get_transaction_statistics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return ResponseUtil.success(
            data=statistics,
            message="获取交易统计概览成功"
        )
    except Exception as e:
        logger.error(f"获取交易统计概览失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/statistics/categories",
    response_model=ApiResponse[CategoryStatisticsResponse],
    summary="获取分类统计数据",
    description="获取指定时间范围内的交易分类统计，包括各分类的支出分布"
)
async def get_category_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期，默认30天前"),
    end_date: Optional[datetime] = Query(None, description="结束日期，默认今天"),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """获取分类统计数据"""
    try:
        statistics = transaction_service.get_category_statistics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return ResponseUtil.success(
            data=statistics,
            message="获取分类统计数据成功"
        )
    except Exception as e:
        logger.error(f"获取分类统计数据失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/statistics/monthly-trends",
    response_model=ApiResponse[MonthlyTrendResponse],
    summary="获取月度趋势分析",
    description="获取指定月数的月度交易趋势分析数据"
)
async def get_monthly_trends(
    months: int = Query(12, ge=1, le=24, description="分析月数，最多24个月"),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """获取月度趋势分析"""
    try:
        trends = transaction_service.get_monthly_trends(
            user_id=current_user.id,
            months=months
        )
        
        return ResponseUtil.success(
            data=trends,
            message="获取月度趋势分析成功"
        )
    except Exception as e:
        logger.error(f"获取月度趋势分析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/categories",
    response_model=ApiResponse[List[TransactionCategoryResponse]],
    summary="获取交易分类列表",
    description="获取所有可用的交易分类，用于创建和编辑交易时选择"
)
async def get_transaction_categories(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """获取交易分类列表"""
    try:
        categories = transaction_service.get_transaction_categories()
        
        # 转换为响应模型
        category_responses = [
            TransactionCategoryResponse(
                id=UUID(cat['id']),
                name=cat['name'],
                icon=cat['icon'],
                color=cat['color'],
                parent_id=UUID(cat['parent_id']) if cat['parent_id'] else None,
                is_system=cat['is_system']
            )
            for cat in categories
        ]
        
        return ResponseUtil.success(
            data=category_responses,
            message="获取交易分类列表成功"
        )
    except Exception as e:
        logger.error(f"获取交易分类列表失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 