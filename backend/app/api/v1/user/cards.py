"""
信用卡管理用户API路由

提供信用卡相关的用户接口
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path
from app.api.dependencies.auth import get_current_user
from app.models.database.user import User
from app.models.schemas.card import (
    CreditCardCreate, CreditCardUpdate, CreditCardResponse,
    CreditCardQueryParams, CreditCardStatusUpdate,
    CreditCardSummary, CreditCardStatistics,
    BankResponse
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse
from app.api.dependencies.services import get_card_service
from app.services.card_service import CardService
from app.utils.response import ResponseUtil
from app.core.exceptions.custom import ResourceNotFoundError

router = APIRouter(prefix="/cards", tags=["信用卡管理"])


@router.post(
    "",
    response_model=ApiResponse,
    summary="创建信用卡",
    response_description="返回创建的信用卡信息"
)
async def create_credit_card(
    card_data: CreditCardCreate,
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    创建新的信用卡
    
    - **card_name**: 卡片名称
    - **card_number**: 卡号（会进行加密存储）
    - **credit_limit**: 信用额度
    - **expiry_month**: 有效期月份
    - **expiry_year**: 有效期年份
    - **bank_id**: 银行ID（可选）
    - **bank_name**: 银行名称（如果不提供bank_id）
    """
    card = card_service.create_credit_card(current_user.id, card_data)
    return ResponseUtil.success(data=card, message="信用卡创建成功")


@router.get(
    "",
    response_model=ApiPagedResponse,
    summary="获取信用卡列表",
    response_description="返回用户的信用卡列表"
)
async def get_credit_cards(
    keyword: str = Query("", description="搜索关键词，支持卡片名称、银行名称模糊搜索"),
    status: Optional[str] = Query(None, description="状态筛选"),
    bank_id: Optional[UUID] = Query(None, description="银行ID筛选"),
    card_type: Optional[str] = Query(None, description="卡片类型筛选"),
    is_primary: Optional[bool] = Query(None, description="是否主卡筛选"),
    expiring_soon: Optional[bool] = Query(None, description="是否即将过期"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    获取用户的信用卡列表
    
    支持多种筛选条件：
    - 关键词搜索（卡片名称、银行名称）
    - 状态筛选
    - 银行筛选
    - 卡片类型筛选
    - 主卡筛选
    - 即将过期筛选
    """
    params = CreditCardQueryParams(
        keyword=keyword,
        status=status,
        bank_id=bank_id,
        card_type=card_type,
        is_primary=is_primary,
        expiring_soon=expiring_soon,
        page=page,
        page_size=page_size
    )
    
    cards, total = card_service.get_user_cards(current_user.id, params)
    
    return ResponseUtil.paginated(
        items=cards,
        total=total,
        page=page,
        page_size=page_size,
        message="获取信用卡列表成功"
    )


@router.get(
    "/{card_id}",
    response_model=ApiResponse,
    summary="获取信用卡详情",
    response_description="返回指定信用卡的详细信息"
)
async def get_credit_card(
    card_id: UUID = Path(..., description="信用卡ID"),
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    获取指定信用卡的详细信息
    """
    card = card_service.get_card_by_id(current_user.id, card_id)
    
    if not card:
        raise ResourceNotFoundError("信用卡不存在")
    
    return ResponseUtil.success(data=card, message="获取信用卡详情成功")


@router.put(
    "/{card_id}",
    response_model=ApiResponse,
    summary="更新信用卡",
    response_description="返回更新后的信用卡信息"
)
async def update_credit_card(
    card_id: UUID = Path(..., description="信用卡ID"),
    update_data: CreditCardUpdate = ...,
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    更新信用卡信息
    
    可更新的字段包括：
    - 卡片名称
    - 信用额度
    - 有效期
    - 账单日和还款日
    - 年费信息
    - 特色功能
    - 备注等
    """
    card = card_service.update_credit_card(current_user.id, card_id, update_data)
    return ResponseUtil.success(data=card, message="信用卡更新成功")


@router.patch(
    "/{card_id}/status",
    response_model=ApiResponse,
    summary="更新信用卡状态",
    response_description="返回更新后的信用卡信息"
)
async def update_card_status(
    card_id: UUID = Path(..., description="信用卡ID"),
    status_data: CreditCardStatusUpdate = ...,
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    更新信用卡状态
    
    支持的状态：
    - active: 激活
    - frozen: 冻结
    - closed: 关闭
    """
    card = card_service.update_card_status(
        current_user.id, 
        card_id, 
        status_data.status, 
        status_data.reason
    )
    return ResponseUtil.success(data=card, message="信用卡状态更新成功")


@router.delete(
    "/{card_id}",
    response_model=ApiResponse,
    summary="删除信用卡",
    response_description="返回删除结果"
)
async def delete_credit_card(
    card_id: UUID = Path(..., description="信用卡ID"),
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    删除信用卡
    
    注意：删除信用卡会同时删除相关的交易记录和年费记录
    """
    success = card_service.delete_credit_card(current_user.id, card_id)
    
    if success:
        return ResponseUtil.success(message="信用卡删除成功")
    else:
        return ResponseUtil.error(message="信用卡删除失败")


@router.get(
    "/summary/overview",
    response_model=ApiResponse,
    summary="获取信用卡摘要统计",
    response_description="返回信用卡的摘要统计信息"
)
async def get_card_summary(
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    获取信用卡摘要统计
    
    包括：
    - 信用卡总数
    - 激活卡片数
    - 总信用额度
    - 总已用额度
    - 总可用额度
    - 平均使用率
    - 即将过期卡片数
    """
    summary = card_service.get_card_summary(current_user.id)
    return ResponseUtil.success(data=summary, message="获取信用卡摘要成功")


@router.get(
    "/statistics/detailed",
    response_model=ApiResponse,
    summary="获取信用卡详细统计",
    response_description="返回信用卡的详细统计分析"
)
async def get_card_statistics(
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    获取信用卡详细统计
    
    包括：
    - 摘要信息
    - 按银行统计
    - 按状态统计
    - 按卡片等级统计
    - 使用率分布
    """
    statistics = card_service.get_card_statistics(current_user.id)
    return ResponseUtil.success(data=statistics, message="获取信用卡统计成功")


# ============ 银行相关接口 ============

@router.get(
    "/banks/list",
    response_model=ApiResponse,
    summary="获取银行列表",
    response_description="返回可用的银行列表"
)
async def get_banks(
    active_only: bool = Query(True, description="是否只返回激活的银行"),
    current_user: User = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    获取银行列表
    
    用于创建信用卡时选择银行
    """
    banks = card_service.get_banks(active_only=active_only)
    return ResponseUtil.success(data=banks, message="获取银行列表成功") 