import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models.response import ApiResponse, ApiPagedResponse
from models.cards import CardCreate, CardUpdate, Card
from services.cards_service import CardsService
from utils.response import ResponseUtil
from routers.auth import get_current_user
from models.users import UserProfile
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cards", tags=["信用卡"])


def get_cards_service(db: Session = Depends(get_db)) -> CardsService:
    """获取信用卡服务实例"""
    return CardsService(db)


@router.get(
    "/", 
    response_model=ApiPagedResponse[Card],
    summary="获取信用卡列表",
    response_description="返回分页的信用卡列表数据"
)
async def get_cards(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="模糊搜索关键词，支持银行名称、卡片名称搜索"),
    current_user: UserProfile = Depends(get_current_user),
    service: CardsService = Depends(get_cards_service)
):
    """
    获取信用卡列表
    
    支持分页和模糊搜索功能。可以根据银行名称、卡片名称等关键词进行搜索。
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量，默认20，最大100
    - keyword: 搜索关键词，支持银行名称、卡片名称模糊匹配
    """
    logger.info(f"获取信用卡列表请求 - page: {page}, page_size: {page_size}, keyword: {keyword}")
    
    try:
        # 计算跳过的记录数
        skip = (page - 1) * page_size
        
        # 调用服务层获取数据
        cards, total = service.get_cards(
            user_id=current_user.id,
            skip=skip,
            limit=page_size,
            keyword=keyword
        )
        
        logger.info(f"获取信用卡列表成功 - total: {total}")
        return ResponseUtil.paginated(
            items=cards,
            total=total,
            page=page,
            page_size=page_size,
            message="获取信用卡列表成功"
        )
    except Exception as e:
        logger.error(f"获取信用卡列表失败: {str(e)}")
        return ResponseUtil.server_error(message="获取信用卡列表失败")


@router.post(
    "/", 
    response_model=ApiResponse[Card],
    summary="创建信用卡",
    response_description="返回创建的信用卡信息"
)
async def create_card(
    card_data: CardCreate,
    current_user: UserProfile = Depends(get_current_user),
    service: CardsService = Depends(get_cards_service)
):
    """
    创建新的信用卡
    
    添加新的信用卡到系统中，包括基本信息、额度设置、年费规则等。
    """
    logger.info(f"创建信用卡请求 - bank_name: {card_data.bank_name}")
    
    try:
        # 调用服务层创建信用卡
        card = service.create_card(card_data, current_user.id)
        logger.info("信用卡创建成功")
        return ResponseUtil.created(data=card, message="创建信用卡成功")
    except ValueError as e:
        logger.warning(f"创建信用卡参数错误: {str(e)}")
        return ResponseUtil.validation_error(message=str(e))
    except Exception as e:
        logger.error(f"创建信用卡失败: {str(e)}")
        return ResponseUtil.server_error(message="创建信用卡失败")


@router.get(
    "/{card_id}",
    response_model=ApiResponse[Card],
    summary="获取信用卡详情",
    response_description="返回指定ID的信用卡详细信息"
)
async def get_card(
    card_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    service: CardsService = Depends(get_cards_service)
):
    """
    根据ID获取信用卡详情
    
    获取指定信用卡的详细信息，包括基本信息、额度、还款日期等。
    """
    logger.info(f"获取信用卡详情请求 - card_id: {card_id}")
    
    try:
        # 调用服务层获取信用卡详情
        card = service.get_card(card_id, current_user.id)
        if not card:
            logger.warning(f"信用卡不存在: {card_id}")
            return ResponseUtil.not_found(message="信用卡不存在")
        
        logger.info("获取信用卡详情成功")
        return ResponseUtil.success(data=card, message="获取信用卡详情成功")
    except Exception as e:
        logger.error(f"获取信用卡详情失败: {str(e)}")
        return ResponseUtil.server_error(message="获取信用卡详情失败")


@router.put(
    "/{card_id}",
    response_model=ApiResponse[Card],
    summary="更新信用卡信息",
    response_description="返回更新后的信用卡信息"
)
async def update_card(
    card_id: UUID,
    card_data: CardUpdate,
    current_user: UserProfile = Depends(get_current_user),
    service: CardsService = Depends(get_cards_service)
):
    """
    更新信用卡信息
    
    更新指定信用卡的信息，如额度调整、还款日期修改等。
    """
    logger.info(f"更新信用卡请求 - card_id: {card_id}")
    
    try:
        # 调用服务层更新信用卡
        card = service.update_card(card_id, current_user.id, card_data)
        if not card:
            logger.warning(f"信用卡不存在: {card_id}")
            return ResponseUtil.not_found(message="信用卡不存在")
        
        logger.info("信用卡更新成功")
        return ResponseUtil.success(data=card, message="信用卡更新成功")
    except Exception as e:
        logger.error(f"更新信用卡失败: {str(e)}")
        return ResponseUtil.server_error(message="更新信用卡失败")


@router.delete(
    "/{card_id}",
    response_model=ApiResponse[None],
    summary="删除信用卡",
    response_description="返回删除结果"
)
async def delete_card(
    card_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    service: CardsService = Depends(get_cards_service)
):
    """
    删除信用卡
    
    从系统中删除指定的信用卡记录。
    """
    logger.info(f"删除信用卡请求 - card_id: {card_id}")
    
    try:
        # 调用服务层删除信用卡
        success = service.delete_card(card_id, current_user.id)
        if not success:
            logger.warning(f"信用卡不存在: {card_id}")
            return ResponseUtil.not_found(message="信用卡不存在")
        
        logger.info("信用卡删除成功")
        return ResponseUtil.deleted(message="信用卡删除成功")
    except Exception as e:
        logger.error(f"删除信用卡失败: {str(e)}")
        return ResponseUtil.server_error(message="删除信用卡失败") 