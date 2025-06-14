"""
用户提醒管理API路由
提供提醒设置、提醒记录、未读提醒等功能
"""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.api.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.database.user import User
from app.models.schemas.reminder import (
    ReminderSettingCreate, ReminderSettingUpdate, ReminderSettingResponse,
    ReminderRecordCreate, ReminderRecordUpdate, ReminderRecordResponse,
    ReminderStatisticsResponse, UpcomingRemindersResponse,
    UnreadRemindersCountResponse, MarkAllReadResponse
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse
from app.services.reminder_service import ReminderService
from app.utils.response import ResponseUtil
from app.core.logging.logger import app_logger as logger

router = APIRouter(prefix="/reminders", tags=["用户-提醒管理"])


# ========== 提醒设置管理 ==========

@router.post(
    "/settings",
    response_model=ApiResponse[ReminderSettingResponse],
    summary="创建提醒设置",
    description="为用户创建新的提醒设置，可以是全局提醒或特定信用卡的提醒"
)
async def create_reminder_setting(
    setting_data: ReminderSettingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建提醒设置"""
    try:
        reminder_service = ReminderService(db)
        setting = reminder_service.create_reminder_setting(
            user_id=current_user.id,
            setting_data=setting_data.model_dump()
        )
        
        logger.info(f"用户 {current_user.username} 创建提醒设置成功")
        return ResponseUtil.success(data=setting, message="提醒设置创建成功")
        
    except Exception as e:
        logger.error(f"创建提醒设置失败: {str(e)}")
        return ResponseUtil.error(message=f"创建提醒设置失败: {str(e)}")


@router.get(
    "/settings",
    response_model=ApiPagedResponse[ReminderSettingResponse],
    summary="获取提醒设置列表",
    description="获取用户的提醒设置列表，支持按信用卡、类型、状态筛选和分页"
)
async def get_reminder_settings(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    card_id: Optional[UUID] = Query(None, description="信用卡ID筛选"),
    reminder_type: Optional[str] = Query(None, description="提醒类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="启用状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒设置列表"""
    try:
        reminder_service = ReminderService(db)
        settings, total = reminder_service.get_user_reminder_settings(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            card_id=card_id,
            reminder_type=reminder_type,
            is_enabled=is_enabled
        )
        
        return ResponseUtil.paginated(
            items=settings,
            total=total,
            page=page,
            page_size=page_size,
            message="获取提醒设置列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取提醒设置列表失败: {str(e)}")
        return ResponseUtil.error(message=f"获取提醒设置列表失败: {str(e)}")


@router.get(
    "/settings/{setting_id}",
    response_model=ApiResponse[ReminderSettingResponse],
    summary="获取提醒设置详情",
    description="获取指定提醒设置的详细信息"
)
async def get_reminder_setting(
    setting_id: UUID = Path(..., description="提醒设置ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒设置详情"""
    try:
        reminder_service = ReminderService(db)
        setting = reminder_service.get_reminder_setting(
            user_id=current_user.id,
            setting_id=setting_id
        )
        
        return ResponseUtil.success(data=setting, message="获取提醒设置详情成功")
        
    except Exception as e:
        logger.error(f"获取提醒设置详情失败: {str(e)}")
        return ResponseUtil.error(message=f"获取提醒设置详情失败: {str(e)}")


@router.put(
    "/settings/{setting_id}",
    response_model=ApiResponse[ReminderSettingResponse],
    summary="更新提醒设置",
    description="更新指定的提醒设置信息"
)
async def update_reminder_setting(
    setting_id: UUID = Path(..., description="提醒设置ID"),
    setting_data: ReminderSettingUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新提醒设置"""
    try:
        reminder_service = ReminderService(db)
        setting = reminder_service.update_reminder_setting(
            user_id=current_user.id,
            setting_id=setting_id,
            setting_data=setting_data.model_dump(exclude_unset=True)
        )
        
        logger.info(f"用户 {current_user.username} 更新提醒设置成功: {setting_id}")
        return ResponseUtil.success(data=setting, message="提醒设置更新成功")
        
    except Exception as e:
        logger.error(f"更新提醒设置失败: {str(e)}")
        return ResponseUtil.error(message=f"更新提醒设置失败: {str(e)}")


@router.delete(
    "/settings/{setting_id}",
    response_model=ApiResponse[bool],
    summary="删除提醒设置",
    description="删除指定的提醒设置及其关联的提醒记录"
)
async def delete_reminder_setting(
    setting_id: UUID = Path(..., description="提醒设置ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除提醒设置"""
    try:
        reminder_service = ReminderService(db)
        result = reminder_service.delete_reminder_setting(
            user_id=current_user.id,
            setting_id=setting_id
        )
        
        logger.info(f"用户 {current_user.username} 删除提醒设置成功: {setting_id}")
        return ResponseUtil.success(data=result, message="提醒设置删除成功")
        
    except Exception as e:
        logger.error(f"删除提醒设置失败: {str(e)}")
        return ResponseUtil.error(message=f"删除提醒设置失败: {str(e)}")


# ========== 提醒记录管理 ==========

@router.post(
    "/records",
    response_model=ApiResponse[ReminderRecordResponse],
    summary="创建提醒记录",
    description="为用户创建新的提醒记录"
)
async def create_reminder_record(
    record_data: ReminderRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建提醒记录"""
    try:
        reminder_service = ReminderService(db)
        record = reminder_service.create_reminder_record(
            user_id=current_user.id,
            record_data=record_data.model_dump()
        )
        
        logger.info(f"用户 {current_user.username} 创建提醒记录成功: {record['id']}")
        return ResponseUtil.success(data=record, message="提醒记录创建成功")
        
    except Exception as e:
        logger.error(f"创建提醒记录失败: {str(e)}")
        return ResponseUtil.error(message=f"创建提醒记录失败: {str(e)}")


@router.get(
    "/records",
    response_model=ApiPagedResponse[ReminderRecordResponse],
    summary="获取提醒记录列表",
    description="获取用户的提醒记录列表，支持按设置、状态、日期筛选和分页"
)
async def get_reminder_records(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    setting_id: Optional[UUID] = Query(None, description="提醒设置ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选: pending, sent, read, cancelled"),
    start_date: Optional[str] = Query(None, description="开始日期筛选 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期筛选 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒记录列表"""
    try:
        # 转换日期参数
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        
        reminder_service = ReminderService(db)
        records, total = reminder_service.get_user_reminder_records(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            setting_id=setting_id,
            status=status,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        return ResponseUtil.paginated(
            items=records,
            total=total,
            page=page,
            page_size=page_size,
            message="获取提醒记录列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取提醒记录列表失败: {str(e)}")
        return ResponseUtil.error(message=f"获取提醒记录列表失败: {str(e)}")


@router.get(
    "/records/{record_id}",
    response_model=ApiResponse[ReminderRecordResponse],
    summary="获取提醒记录详情",
    description="获取指定提醒记录的详细信息"
)
async def get_reminder_record(
    record_id: UUID = Path(..., description="提醒记录ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒记录详情"""
    try:
        reminder_service = ReminderService(db)
        record = reminder_service.get_reminder_record(
            user_id=current_user.id,
            record_id=record_id
        )
        
        return ResponseUtil.success(data=record, message="获取提醒记录详情成功")
        
    except Exception as e:
        logger.error(f"获取提醒记录详情失败: {str(e)}")
        return ResponseUtil.error(message=f"获取提醒记录详情失败: {str(e)}")


@router.post(
    "/records/{record_id}/read",
    response_model=ApiResponse[ReminderRecordResponse],
    summary="标记提醒为已读",
    description="将指定的提醒记录标记为已读状态"
)
async def mark_reminder_as_read(
    record_id: UUID = Path(..., description="提醒记录ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记提醒为已读"""
    try:
        reminder_service = ReminderService(db)
        record = reminder_service.mark_reminder_as_read(
            user_id=current_user.id,
            record_id=record_id
        )
        
        logger.info(f"用户 {current_user.username} 标记提醒为已读: {record_id}")
        return ResponseUtil.success(data=record, message="提醒已标记为已读")
        
    except Exception as e:
        logger.error(f"标记提醒为已读失败: {str(e)}")
        return ResponseUtil.error(message=f"标记提醒为已读失败: {str(e)}")


# ========== 提醒统计和分析 ==========

@router.get(
    "/statistics",
    response_model=ApiResponse[ReminderStatisticsResponse],
    summary="获取提醒统计",
    description="获取用户的提醒统计信息，包括设置数量、提醒数量、阅读率等"
)
async def get_reminder_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒统计"""
    try:
        reminder_service = ReminderService(db)
        statistics = reminder_service.get_reminder_statistics(current_user.id)
        
        return ResponseUtil.success(data=statistics, message="获取提醒统计成功")
        
    except Exception as e:
        logger.error(f"获取提醒统计失败: {str(e)}")
        return ResponseUtil.error(message=f"获取提醒统计失败: {str(e)}")


@router.get(
    "/upcoming",
    response_model=ApiResponse[UpcomingRemindersResponse],
    summary="获取即将到来的提醒",
    description="获取指定天数内即将到来的提醒，按优先级分类"
)
async def get_upcoming_reminders(
    days_ahead: int = Query(7, ge=1, le=30, description="查看未来天数，最大30天"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取即将到来的提醒"""
    try:
        reminder_service = ReminderService(db)
        upcoming = reminder_service.get_upcoming_reminders(
            user_id=current_user.id,
            days_ahead=days_ahead
        )
        
        return ResponseUtil.success(data=upcoming, message="获取即将到来的提醒成功")
        
    except Exception as e:
        logger.error(f"获取即将到来的提醒失败: {str(e)}")
        return ResponseUtil.error(message=f"获取即将到来的提醒失败: {str(e)}")


@router.get(
    "/unread-count",
    response_model=ApiResponse[UnreadRemindersCountResponse],
    summary="获取未读提醒个数",
    description="获取用户的未读提醒个数统计，包括总数、今日未读、高优先级未读等"
)
async def get_unread_reminders_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取未读提醒个数"""
    try:
        reminder_service = ReminderService(db)
        unread_count = reminder_service.get_unread_reminders_count(current_user.id)
        
        return ResponseUtil.success(data=unread_count, message="获取未读提醒个数成功")
        
    except Exception as e:
        logger.error(f"获取未读提醒个数失败: {str(e)}")
        return ResponseUtil.error(message=f"获取未读提醒个数失败: {str(e)}")


@router.post(
    "/mark-all-read",
    response_model=ApiResponse[MarkAllReadResponse],
    summary="标记所有提醒为已读",
    description="将用户的所有未读提醒标记为已读状态"
)
async def mark_all_reminders_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记所有提醒为已读"""
    try:
        reminder_service = ReminderService(db)
        result = reminder_service.mark_all_reminders_as_read(current_user.id)
        
        logger.info(f"用户 {current_user.username} 标记所有提醒为已读")
        return ResponseUtil.success(data=result, message="所有提醒已标记为已读")
        
    except Exception as e:
        logger.error(f"标记所有提醒为已读失败: {str(e)}")
        return ResponseUtil.error(message=f"标记所有提醒为已读失败: {str(e)}")


@router.get(
    "/recent",
    response_model=ApiResponse[List[ReminderRecordResponse]],
    summary="获取最近的提醒",
    description="获取用户最近的提醒记录"
)
async def get_recent_reminders(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制，最大50"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最近的提醒"""
    try:
        reminder_service = ReminderService(db)
        recent_reminders = reminder_service.get_recent_reminders(
            user_id=current_user.id,
            limit=limit
        )
        
        return ResponseUtil.success(data=recent_reminders, message="获取最近提醒成功")
        
    except Exception as e:
        logger.error(f"获取最近提醒失败: {str(e)}")
        return ResponseUtil.error(message=f"获取最近提醒失败: {str(e)}")


# ========== 自动提醒生成 ==========

@router.post(
    "/generate-automatic",
    response_model=ApiResponse[dict],
    summary="生成自动提醒",
    description="为用户的信用卡自动生成提醒记录"
)
async def generate_automatic_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成自动提醒"""
    try:
        reminder_service = ReminderService(db)
        count = reminder_service.create_automatic_reminders(current_user.id)
        
        result = {
            "generated_count": count,
            "message": f"成功生成 {count} 条自动提醒",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"用户 {current_user.username} 生成自动提醒: {count} 条")
        return ResponseUtil.success(data=result, message="自动提醒生成成功")
        
    except Exception as e:
        logger.error(f"生成自动提醒失败: {str(e)}")
        return ResponseUtil.error(message=f"生成自动提醒失败: {str(e)}") 