"""
交易记录路由

提供交易记录相关的API接口。
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.response import ApiResponse, ApiPagedResponse
from models.transactions import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TransactionStatistics,
    TransactionCategoryStatistics,
    MonthlyTransactionTrend,
)
from db_models.transactions import TransactionType, TransactionCategory, TransactionStatus
from services.transactions_service import TransactionsService
from routers.auth import get_current_user
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== CRUD接口 ====================

@router.post(
    "/",
    response_model=ApiResponse[Transaction],
    tags=["交易记录"],
    summary="创建交易记录",
    response_description="返回创建的交易记录信息"
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建新的交易记录
    
    支持记录各种类型的交易：
    - 消费交易：日常购物、餐饮等消费
    - 还款交易：信用卡还款
    - 退款交易：商户退款
    - 取现交易：ATM取现
    - 转账交易：转账操作
    - 手续费：年费、取现手续费等
    
    系统会自动：
    - 验证信用卡归属
    - 计算积分（如果未提供）
    - 更新年费减免进度（消费交易）
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        transaction = service.create_transaction(user_id, transaction_data)
        logger.info(f"交易记录创建成功: {transaction.id}")
        
        return ResponseUtil.success(
            data=transaction,
            message="交易记录创建成功"
        )
    except ValueError as e:
        logger.warning(f"创建交易记录参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建交易记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建交易记录失败")


@router.get(
    "/",
    response_model=ApiPagedResponse[Transaction],
    tags=["交易记录"],
    summary="获取交易记录列表",
    response_description="返回分页的交易记录列表"
)
def get_transactions(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    card_id: Optional[UUID] = Query(None, description="信用卡ID过滤"),
    transaction_type: Optional[TransactionType] = Query(None, description="交易类型过滤"),
    category: Optional[TransactionCategory] = Query(None, description="交易分类过滤"),
    status: Optional[TransactionStatus] = Query(None, description="交易状态过滤"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    merchant_name: Optional[str] = Query(None, description="商户名称模糊搜索"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="最小金额"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="最大金额"),
    keyword: str = Query("", description="关键词模糊搜索，支持商户名称、交易描述、备注"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取交易记录列表
    
    支持多种筛选条件：
    - card_id: 按信用卡筛选
    - transaction_type: 按交易类型筛选（expense/payment/refund/withdrawal/transfer/fee）
    - category: 按消费分类筛选（dining/shopping/transport等）
    - status: 按交易状态筛选（pending/completed/failed/cancelled/refunded）
    - start_date/end_date: 按交易时间范围筛选
    - merchant_name: 按商户名称模糊搜索
    - min_amount/max_amount: 按金额范围筛选
    - keyword: 关键词模糊搜索，搜索范围包括商户名称、交易描述、备注、地点
    
    返回结果按交易时间倒序排列。
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        skip = (page - 1) * page_size
        
        transactions, total = service.get_transactions(
            user_id=user_id,
            card_id=card_id,
            transaction_type=transaction_type,
            category=category,
            status=status,
            start_date=start_date,
            end_date=end_date,
            merchant_name=merchant_name,
            min_amount=min_amount,
            max_amount=max_amount,
            keyword=keyword,
            skip=skip,
            limit=page_size
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
        raise HTTPException(status_code=500, detail="获取交易记录列表失败")


@router.get(
    "/{transaction_id}",
    response_model=ApiResponse[Transaction],
    tags=["交易记录"],
    summary="获取交易记录详情",
    response_description="返回指定的交易记录详情"
)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    根据ID获取交易记录详情
    
    返回完整的交易记录信息，包括：
    - 基本交易信息（金额、时间、类型等）
    - 商户信息
    - 分类和状态
    - 积分信息
    - 分期信息
    - 备注等
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        transaction = service.get_transaction(transaction_id, user_id)
        
        if not transaction:
            logger.warning(f"交易记录不存在: {transaction_id}")
            return ResponseUtil.not_found(message="交易记录不存在")
        
        return ResponseUtil.success(
            data=transaction,
            message="获取交易记录成功"
        )
    except Exception as e:
        logger.error(f"获取交易记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取交易记录失败")


@router.put(
    "/{transaction_id}",
    response_model=ApiResponse[Transaction],
    tags=["交易记录"],
    summary="更新交易记录",
    response_description="返回更新后的交易记录信息"
)
def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    更新交易记录信息
    
    支持更新以下字段：
    - 交易类型和金额
    - 商户信息
    - 交易描述和分类
    - 积分信息
    - 分期信息
    - 备注等
    
    注意：
    - 如果修改了影响年费进度的字段（金额、类型、状态），系统会重新计算年费进度
    - 只有用户自己的交易记录才能被修改
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        transaction = service.update_transaction(transaction_id, user_id, transaction_data)
        
        if not transaction:
            logger.warning(f"交易记录不存在: {transaction_id}")
            return ResponseUtil.not_found(message="交易记录不存在")
        
        logger.info(f"交易记录更新成功: {transaction_id}")
        return ResponseUtil.success(
            data=transaction,
            message="交易记录更新成功"
        )
    except Exception as e:
        logger.error(f"更新交易记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新交易记录失败")


@router.delete(
    "/{transaction_id}",
    response_model=ApiResponse[None],
    tags=["交易记录"],
    summary="删除交易记录",
    response_description="返回删除结果"
)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除交易记录
    
    注意：
    - 删除交易记录会触发年费进度的重新计算
    - 只有用户自己的交易记录才能被删除
    - 删除操作不可恢复，请谨慎操作
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        success = service.delete_transaction(transaction_id, user_id)
        
        if not success:
            logger.warning(f"交易记录不存在: {transaction_id}")
            return ResponseUtil.not_found(message="交易记录不存在")
        
        logger.info(f"交易记录删除成功: {transaction_id}")
        return ResponseUtil.deleted(message="交易记录删除成功")
    except Exception as e:
        logger.error(f"删除交易记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除交易记录失败")


# ==================== 统计分析接口 ====================

@router.get(
    "/statistics/overview",
    response_model=ApiResponse[TransactionStatistics],
    tags=["交易统计"],
    summary="获取交易统计概览",
    response_description="返回交易统计信息"
)
def get_transaction_statistics(
    card_id: Optional[UUID] = Query(None, description="信用卡ID过滤"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取交易统计概览
    
    提供以下统计信息：
    - 总交易笔数
    - 总交易金额
    - 支出金额
    - 收入金额
    - 总获得积分
    - 各分类消费统计
    
    支持按信用卡和时间范围筛选。
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        statistics = service.get_transaction_statistics(
            user_id=user_id,
            card_id=card_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return ResponseUtil.success(
            data=statistics,
            message="获取交易统计成功"
        )
    except Exception as e:
        logger.error(f"获取交易统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取交易统计失败")


@router.get(
    "/statistics/categories",
    response_model=ApiResponse[List[TransactionCategoryStatistics]],
    tags=["交易统计"],
    summary="获取分类消费统计",
    response_description="返回各分类的消费统计信息"
)
def get_category_statistics(
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取分类消费统计
    
    按消费分类统计：
    - 各分类的交易笔数
    - 各分类的总金额
    - 各分类的平均金额
    - 各分类占总消费的百分比
    
    结果按消费金额降序排列。
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        statistics = service.get_category_statistics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return ResponseUtil.success(
            data=statistics,
            message="获取分类统计成功"
        )
    except Exception as e:
        logger.error(f"获取分类统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取分类统计失败")


@router.get(
    "/statistics/monthly-trend",
    response_model=ApiResponse[List[MonthlyTransactionTrend]],
    tags=["交易统计"],
    summary="获取月度交易趋势",
    response_description="返回月度交易趋势数据"
)
def get_monthly_trend(
    year: Optional[int] = Query(None, description="年份，默认当前年份"),
    card_id: Optional[UUID] = Query(None, description="信用卡ID过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取月度交易趋势
    
    按月统计交易数据：
    - 每月交易笔数
    - 每月总金额
    - 每月支出金额
    - 每月收入金额
    
    返回指定年份全年12个月的数据，没有交易的月份用0填充。
    """
    try:
        service = TransactionsService(db)
        user_id = UUID(current_user["sub"])
        
        trend = service.get_monthly_trend(
            user_id=user_id,
            year=year,
            card_id=card_id
        )
        
        return ResponseUtil.success(
            data=trend,
            message="获取月度趋势成功"
        )
    except Exception as e:
        logger.error(f"获取月度趋势失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取月度趋势失败") 