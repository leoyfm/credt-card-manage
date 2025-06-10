"""
用户功能区 - 信用卡管理接口

本模块提供用户个人信用卡管理的所有接口：
- 信用卡CRUD操作
- 信用卡状态管理
- 信用卡统计查询
- 银行信息查询

权限等级: Level 2 (用户认证)
数据范围: 仅自有信用卡数据

作者: LEO
邮箱: leoyfm@gmail.com
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.schemas.user import UserProfile
from app.models.schemas.card import (
    CardCreateRequest, CardUpdateRequest, CardStatusUpdateRequest,
    CardResponse, CardDetailResponse, CardStatistics, BankListResponse,
    CardListQuery, CardBatchUpdateRequest, CardBatchUpdateResponse
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse, SuccessMessage
from app.services.cards_service import CardsService
from app.utils.response import ResponseUtil

# 配置日志和路由
logger = get_logger(__name__)
router = APIRouter(
    prefix="/cards",
    tags=["v1-用户-信用卡管理"]
)

@router.get(
    "/list",
    response_model=ApiPagedResponse[CardResponse],
    summary="获取我的信用卡列表",
    response_description="返回当前用户的信用卡列表"
)
async def get_my_cards(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="搜索关键词，支持卡片名称、银行名称模糊搜索"),
    status: Optional[str] = Query(None, description="卡片状态筛选：active, frozen, closed"),
    card_type: Optional[str] = Query(None, description="卡片类型筛选：credit, debit"),
    bank_name: Optional[str] = Query(None, description="银行名称筛选"),
    is_primary: Optional[bool] = Query(None, description="是否主卡筛选"),
    expires_soon: Optional[bool] = Query(None, description="是否即将过期筛选（3个月内）"),
    sort_by: str = Query("created_at", description="排序字段：created_at, credit_limit, card_name"),
    sort_order: str = Query("desc", description="排序方向：asc, desc"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的信用卡列表
    
    支持多种筛选和排序条件：
    - 关键词模糊搜索（卡片名称、银行名称）
    - 按状态、类型、银行筛选
    - 按创建时间、信用额度、名称排序
    - 分页显示，避免数据过载
    
    返回脱敏的信用卡信息，保护用户隐私
    """
    try:
        logger.info("用户查询信用卡列表", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   page=page, 
                   page_size=page_size,
                   keyword=keyword)
        
        cards_service = CardsService(db)
        
        # 构建查询参数
        query_params = CardListQuery(
            keyword=keyword,
            status=status,
            card_type=card_type,
            bank_name=bank_name,
            is_primary=is_primary,
            expires_soon=expires_soon,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # 获取用户信用卡列表
        cards, total = cards_service.get_user_cards_list(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            query_params=query_params
        )
        
        return ResponseUtil.paginated(
            items=cards,
            total=total,
            page=page,
            page_size=page_size,
            message="获取信用卡列表成功"
        )
        
    except Exception as e:
        logger.error("获取信用卡列表异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取信用卡列表失败，请稍后重试")


@router.post(
    "/create",
    response_model=ApiResponse[CardResponse],
    summary="添加新信用卡",
    response_description="返回新创建的信用卡信息"
)
async def create_card(
    card_data: CardCreateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加新的信用卡
    
    用户可以添加自己的信用卡信息：
    - 自动加密存储卡号，保护隐私
    - 自动验证卡号格式和有效期
    - 支持设置年费规则和特色功能
    - 可设置为主卡（每个用户只能有一张主卡）
    
    创建成功后会自动生成脱敏的卡号显示
    """
    try:
        logger.info("用户添加信用卡", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_name=card_data.card_name,
                   bank_name=card_data.bank_name)
        
        cards_service = CardsService(db)
        
        # 检查卡号是否重复
        existing_card = cards_service.check_card_number_exists(
            user_id=current_user.id,
            card_number=card_data.card_number
        )
        if existing_card:
            return ResponseUtil.validation_error("该卡号已存在，请检查后重试")
        
        # 创建信用卡
        new_card = cards_service.create_user_card(
            user_id=current_user.id,
            card_data=card_data
        )
        
        if not new_card:
            return ResponseUtil.error("创建信用卡失败")
        
        logger.info("用户添加信用卡成功", 
                   user_id=current_user.id, 
                   card_id=new_card.id,
                   card_name=new_card.card_name)
        
        return ResponseUtil.created(
            data=new_card,
            message="信用卡添加成功"
        )
        
    except ValueError as e:
        logger.warning("添加信用卡参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("添加信用卡异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("添加信用卡失败，请稍后重试")


@router.get(
    "/{card_id}/details",
    response_model=ApiResponse[CardDetailResponse],
    summary="获取信用卡详情",
    response_description="返回指定信用卡的详细信息"
)
async def get_card_details(
    card_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定信用卡的详细信息
    
    包含完整的信用卡信息：
    - 完整卡号（仅卡片所有者可见）
    - 银行详细信息和特色功能
    - 最近交易统计和年费状态
    - 下次账单日和还款日
    
    只能查看自己的信用卡详情
    """
    try:
        logger.info("用户查看信用卡详情", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_id=card_id)
        
        cards_service = CardsService(db)
        
        # 获取信用卡详情
        card_detail = cards_service.get_user_card_detail(
            user_id=current_user.id,
            card_id=card_id
        )
        
        if not card_detail:
            return ResponseUtil.not_found("信用卡不存在或无权访问")
        
        return ResponseUtil.success(
            data=card_detail,
            message="获取信用卡详情成功"
        )
        
    except Exception as e:
        logger.error("获取信用卡详情异常", error=str(e), user_id=current_user.id, card_id=card_id)
        return ResponseUtil.error("获取信用卡详情失败，请稍后重试")


@router.put(
    "/{card_id}/update",
    response_model=ApiResponse[CardResponse],
    summary="更新信用卡信息",
    response_description="返回更新后的信用卡信息"
)
async def update_card(
    card_id: UUID,
    card_data: CardUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新信用卡信息
    
    用户可以更新自己信用卡的信息：
    - 修改卡片名称、信用额度、账单日等
    - 调整年费设置和特色功能
    - 更新积分倍率和返现比例
    - 添加或修改备注信息
    
    不能修改卡号和银行信息
    """
    try:
        logger.info("用户更新信用卡信息", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_id=card_id)
        
        cards_service = CardsService(db)
        
        # 更新信用卡信息
        updated_card = cards_service.update_user_card(
            user_id=current_user.id,
            card_id=card_id,
            card_data=card_data
        )
        
        if not updated_card:
            return ResponseUtil.not_found("信用卡不存在或无权访问")
        
        logger.info("用户更新信用卡成功", 
                   user_id=current_user.id, 
                   card_id=card_id)
        
        return ResponseUtil.success(
            data=updated_card,
            message="信用卡信息更新成功"
        )
        
    except ValueError as e:
        logger.warning("更新信用卡参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新信用卡异常", error=str(e), user_id=current_user.id, card_id=card_id)
        return ResponseUtil.error("更新信用卡失败，请稍后重试")


@router.put(
    "/{card_id}/status",
    response_model=ApiResponse[SuccessMessage],
    summary="更新信用卡状态",
    response_description="返回状态更新结果"
)
async def update_card_status(
    card_id: UUID,
    status_data: CardStatusUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新信用卡状态
    
    用户可以更改自己信用卡的状态：
    - active: 激活卡片，正常使用
    - frozen: 冻结卡片，暂停使用
    - closed: 关闭卡片，永久停用
    
    状态变更会影响相关功能和统计
    """
    try:
        logger.info("用户更新信用卡状态", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_id=card_id,
                   new_status=status_data.status,
                   reason=status_data.reason)
        
        cards_service = CardsService(db)
        
        # 更新卡片状态
        success = cards_service.update_user_card_status(
            user_id=current_user.id,
            card_id=card_id,
            status=status_data.status,
            reason=status_data.reason
        )
        
        if not success:
            return ResponseUtil.not_found("信用卡不存在或无权访问")
        
        status_text = {
            "active": "激活",
            "frozen": "冻结", 
            "closed": "关闭"
        }.get(status_data.status, "未知")
        
        logger.info("用户更新信用卡状态成功", 
                   user_id=current_user.id, 
                   card_id=card_id,
                   status=status_data.status)
        
        return ResponseUtil.success(
            data={"message": f"信用卡状态已更新为{status_text}", "timestamp": None},
            message=f"信用卡状态更新成功，已{status_text}"
        )
        
    except ValueError as e:
        logger.warning("更新信用卡状态参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新信用卡状态异常", error=str(e), user_id=current_user.id, card_id=card_id)
        return ResponseUtil.error("更新信用卡状态失败，请稍后重试")


@router.delete(
    "/{card_id}/delete",
    response_model=ApiResponse[SuccessMessage],
    summary="删除信用卡",
    response_description="返回删除结果"
)
async def delete_card(
    card_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除信用卡
    
    用户可以删除自己的信用卡：
    - 删除前会检查是否有未处理的交易
    - 删除后相关的年费规则也会被删除
    - 操作不可逆转，请谨慎使用
    
    ⚠️ 注意：删除信用卡会同时删除相关的交易记录和年费记录
    """
    try:
        logger.warning("用户请求删除信用卡", 
                      user_id=current_user.id, 
                      username=current_user.username,
                      card_id=card_id)
        
        cards_service = CardsService(db)
        
        # 检查是否可以删除
        can_delete, reason = cards_service.check_card_can_delete(
            user_id=current_user.id,
            card_id=card_id
        )
        
        if not can_delete:
            return ResponseUtil.validation_error(reason or "信用卡无法删除")
        
        # 删除信用卡
        success = cards_service.delete_user_card(
            user_id=current_user.id,
            card_id=card_id
        )
        
        if not success:
            return ResponseUtil.not_found("信用卡不存在或无权访问")
        
        logger.warning("用户删除信用卡成功", 
                      user_id=current_user.id, 
                      card_id=card_id)
        
        return ResponseUtil.success(
            data={"message": "信用卡已删除", "timestamp": None},
            message="信用卡删除成功"
        )
        
    except Exception as e:
        logger.error("删除信用卡异常", error=str(e), user_id=current_user.id, card_id=card_id)
        return ResponseUtil.error("删除信用卡失败，请稍后重试")


@router.get(
    "/statistics",
    response_model=ApiResponse[CardStatistics],
    summary="获取我的信用卡统计",
    response_description="返回当前用户的信用卡统计数据"
)
async def get_my_card_statistics(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的信用卡统计数据
    
    包含全面的统计信息：
    - 信用卡数量和状态分布
    - 总信用额度和利用率
    - 按银行、卡组织分组统计
    - 年费总额和减免情况
    - 即将过期的卡片提醒
    """
    try:
        logger.info("用户查看信用卡统计", 
                   user_id=current_user.id, 
                   username=current_user.username)
        
        cards_service = CardsService(db)
        statistics = cards_service.get_user_card_statistics(current_user.id)
        
        return ResponseUtil.success(
            data=statistics,
            message="获取信用卡统计成功"
        )
        
    except Exception as e:
        logger.error("获取信用卡统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取信用卡统计失败，请稍后重试")


@router.get(
    "/banks",
    response_model=ApiResponse[BankListResponse],
    summary="获取银行列表",
    response_description="返回可用的银行列表"
)
async def get_banks_list(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取可用银行列表
    
    返回系统支持的银行信息：
    - 银行名称和代码
    - 银行logo和状态
    - 按排序顺序返回
    
    用于创建信用卡时的银行选择
    """
    try:
        logger.info("用户查询银行列表", 
                   user_id=current_user.id, 
                   username=current_user.username)
        
        cards_service = CardsService(db)
        banks_list = cards_service.get_active_banks_list()
        
        return ResponseUtil.success(
            data=banks_list,
            message="获取银行列表成功"
        )
        
    except Exception as e:
        logger.error("获取银行列表异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取银行列表失败，请稍后重试")


@router.put(
    "/batch-update",
    response_model=ApiResponse[CardBatchUpdateResponse],
    summary="批量更新信用卡",
    response_description="返回批量更新结果"
)
async def batch_update_cards(
    update_data: CardBatchUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量更新信用卡
    
    支持批量操作：
    - 批量更新卡片状态
    - 批量修改银行信息
    - 批量调整年费设置
    
    只能操作自己的信用卡
    """
    try:
        logger.info("用户批量更新信用卡", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_count=len(update_data.card_ids),
                   operation=update_data.operation)
        
        cards_service = CardsService(db)
        
        # 执行批量更新
        result = cards_service.batch_update_user_cards(
            user_id=current_user.id,
            update_data=update_data
        )
        
        logger.info("用户批量更新信用卡完成", 
                   user_id=current_user.id,
                   success_count=result.success_count,
                   failed_count=result.failed_count)
        
        return ResponseUtil.success(
            data=result,
            message=f"批量更新完成，成功{result.success_count}个，失败{result.failed_count}个"
        )
        
    except ValueError as e:
        logger.warning("批量更新信用卡参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("批量更新信用卡异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("批量更新信用卡失败，请稍后重试") 