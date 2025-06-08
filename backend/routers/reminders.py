import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from models.response import ApiResponse, ApiPagedResponse
from models.reminders import ReminderCreate, ReminderUpdate, Reminder
from services.reminders_service import RemindersService
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reminders", tags=["还款提醒"])


def get_reminders_service() -> RemindersService:
    """获取还款提醒服务实例"""
    # TODO: 实现依赖注入
    pass


@router.get(
    "/", 
    response_model=ApiPagedResponse[Reminder],
    summary="获取还款提醒列表",
    response_description="返回分页的还款提醒数据"
)
async def get_reminders(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="模糊搜索关键词，支持卡片名称、银行名称搜索"),
    service: RemindersService = Depends(get_reminders_service)
):
    """
    获取还款提醒列表
    
    获取用户的还款提醒信息，支持分页和模糊搜索。
    包括还款日期、金额、状态等信息。
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量，默认20，最大100
    - keyword: 搜索关键词，支持卡片名称、银行名称模糊匹配
    """
    logger.info(f"获取还款提醒列表请求 - page: {page}, page_size: {page_size}, keyword: {keyword}")
    
    try:
        # TODO: 调用服务层获取数据
        reminders = []
        total = 0
        
        logger.info(f"获取还款提醒列表成功 - total: {total}")
        return ResponseUtil.paginated(
            items=reminders,
            total=total,
            page=page,
            page_size=page_size,
            message="获取还款提醒列表成功"
        )
    except Exception as e:
        logger.error(f"获取还款提醒列表失败: {str(e)}")
        return ResponseUtil.server_error(message="获取还款提醒列表失败")


@router.post(
    "/", 
    response_model=ApiResponse[Reminder],
    summary="创建还款提醒",
    response_description="返回创建的还款提醒信息"
)
async def create_reminder(
    reminder_data: ReminderCreate,
    service: RemindersService = Depends(get_reminders_service)
):
    """
    创建新的还款提醒
    
    为指定信用卡创建还款提醒，包括提醒时间、金额等信息。
    """
    logger.info(f"创建还款提醒请求 - card_id: {reminder_data.card_id}")
    
    try:
        # TODO: 调用服务层创建还款提醒
        logger.info("还款提醒创建成功")
        return ResponseUtil.created(message="创建还款提醒成功")
    except Exception as e:
        logger.error(f"创建还款提醒失败: {str(e)}")
        return ResponseUtil.server_error(message="创建还款提醒失败")


@router.get(
    "/{reminder_id}",
    response_model=ApiResponse[Reminder],
    summary="获取还款提醒详情",
    response_description="返回指定ID的还款提醒详细信息"
)
async def get_reminder(
    reminder_id: UUID,
    service: RemindersService = Depends(get_reminders_service)
):
    """
    根据ID获取还款提醒详情
    
    获取指定还款提醒的详细信息。
    """
    logger.info(f"获取还款提醒详情请求 - reminder_id: {reminder_id}")
    
    try:
        # TODO: 调用服务层获取还款提醒详情
        logger.info("获取还款提醒详情成功")
        return ResponseUtil.success(message="获取还款提醒详情成功")
    except Exception as e:
        logger.error(f"获取还款提醒详情失败: {str(e)}")
        return ResponseUtil.not_found(message="还款提醒不存在")


@router.put(
    "/{reminder_id}",
    response_model=ApiResponse[Reminder],
    summary="更新还款提醒",
    response_description="返回更新后的还款提醒信息"
)
async def update_reminder(
    reminder_id: UUID,
    reminder_data: ReminderUpdate,
    service: RemindersService = Depends(get_reminders_service)
):
    """
    更新还款提醒信息
    
    更新指定还款提醒的信息，如提醒时间、金额等。
    """
    logger.info(f"更新还款提醒请求 - reminder_id: {reminder_id}")
    
    try:
        # TODO: 调用服务层更新还款提醒
        logger.info("还款提醒更新成功")
        return ResponseUtil.success(message="还款提醒更新成功")
    except Exception as e:
        logger.error(f"更新还款提醒失败: {str(e)}")
        return ResponseUtil.server_error(message="更新还款提醒失败")


@router.delete(
    "/{reminder_id}",
    response_model=ApiResponse[None],
    summary="删除还款提醒",
    response_description="返回删除结果"
)
async def delete_reminder(
    reminder_id: UUID,
    service: RemindersService = Depends(get_reminders_service)
):
    """
    删除还款提醒
    
    从系统中删除指定的还款提醒记录。
    """
    logger.info(f"删除还款提醒请求 - reminder_id: {reminder_id}")
    
    try:
        # TODO: 调用服务层删除还款提醒
        logger.info("还款提醒删除成功")
        return ResponseUtil.deleted(message="还款提醒删除成功")
    except Exception as e:
        logger.error(f"删除还款提醒失败: {str(e)}")
        return ResponseUtil.server_error(message="删除还款提醒失败")


@router.put(
    "/{reminder_id}/mark-read",
    response_model=ApiResponse[None],
    summary="标记提醒已读",
    response_description="返回标记结果"
)
async def mark_reminder_read(
    reminder_id: UUID,
    service: RemindersService = Depends(get_reminders_service)
):
    """
    标记还款提醒为已读状态
    
    将指定的还款提醒标记为已读，避免重复提醒。
    """
    logger.info(f"标记还款提醒已读请求 - reminder_id: {reminder_id}")
    
    try:
        # TODO: 调用服务层标记已读
        logger.info("还款提醒标记已读成功")
        return ResponseUtil.success(message="还款提醒标记已读成功")
    except Exception as e:
        logger.error(f"标记还款提醒已读失败: {str(e)}")
        return ResponseUtil.server_error(message="标记还款提醒已读失败") 