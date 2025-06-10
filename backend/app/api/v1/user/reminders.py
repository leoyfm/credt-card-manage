"""
用户功能区 - 还款提醒管理接口

本模块提供用户级别的还款提醒管理功能，包括：
- 提醒设置管理 (CRUD操作)
- 提醒记录查询和管理
- 批量操作和管理
- 统计分析和报表
- 特殊功能 (延后、测试、快速设置)
- 模板管理

权限级别：Level 2 (用户认证)
数据范围：仅限当前用户的提醒数据
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.schemas.reminder import (
    # 设置相关
    ReminderSettingCreate, ReminderSettingUpdate, ReminderSettingResponse,
    ReminderSettingQuery, ReminderSettingListResponse,
    
    # 记录相关
    ReminderLogResponse, ReminderLogQuery, ReminderLogListResponse,
    
    # 批量操作
    BatchReminderOperation, BatchOperationResult,
    
    # 统计分析
    ReminderStatistics, ReminderStatisticsResponse,
    ReminderTrendData, ReminderTrendResponse,
    
    # 特殊操作
    SnoozeReminderRequest, TestReminderRequest, QuickReminderSetup,
    
    # 模板相关
    ReminderTemplate, ReminderTemplateListResponse,
    
    # 枚举
    ReminderType, NotificationChannel
)
from app.models.schemas.user import UserProfile
from app.models.schemas.common import BaseResponse
from app.utils.response import ResponseUtil
from app.core.logging import get_logger

# 初始化路由和日志
router = APIRouter(prefix="/reminders", tags=["用户-还款提醒"])
logger = get_logger(__name__)

# ================================
# 提醒设置管理接口
# ================================

@router.get(
    "/settings",
    response_model=ReminderSettingListResponse,
    summary="获取我的提醒设置列表",
    description="获取当前用户的所有提醒设置，支持分页和多条件筛选"
)
async def get_my_reminder_settings(
    query_params: ReminderSettingQuery = Depends(),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的提醒设置列表
    
    支持的筛选条件：
    - keyword: 关键词搜索 (提醒类型、卡片名称等)
    - card_id: 按信用卡筛选
    - reminder_type: 按提醒类型筛选
    - is_enabled: 按启用状态筛选
    
    返回分页结果，包含提醒设置详情和关联的信用卡信息
    """
    try:
        logger.info(f"用户 {current_user.username} 查询提醒设置列表", extra={
            "user_id": str(current_user.id),
            "query_params": query_params.dict()
        })
        
        # TODO: 实现提醒设置查询服务
        # settings, total = reminder_service.get_user_reminder_settings(
        #     user_id=current_user.id,
        #     query_params=query_params
        # )
        
        # 模拟数据
        settings = [
            ReminderSettingResponse(
                id=UUID("123e4567-e89b-12d3-a456-426614174001"),
                user_id=current_user.id,
                card_id=UUID("card-uuid-1"),
                card_name="招商银行信用卡",
                reminder_type=ReminderType.PAYMENT_DUE,
                advance_days=3,
                reminder_time="09:00:00",
                email_enabled=True,
                push_enabled=True,
                sms_enabled=False,
                wechat_enabled=False,
                in_app_enabled=True,
                is_recurring=True,
                frequency="monthly",
                is_enabled=True,
                status="active",
                next_trigger_date=date(2024, 12, 15),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        total = 1
        
        return ResponseUtil.paginated(
            data=settings,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size,
            message="提醒设置查询成功"
        )
        
    except Exception as e:
        logger.error(f"查询提醒设置失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询提醒设置失败")


@router.post(
    "/settings",
    response_model=BaseResponse[ReminderSettingResponse],
    summary="创建提醒设置",
    description="为指定信用卡或全局创建新的提醒设置"
)
async def create_reminder_setting(
    setting_data: ReminderSettingCreate,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的提醒设置
    
    功能特性：
    - 支持单卡提醒和全局提醒设置
    - 自动验证信用卡所有权
    - 防重复设置检查
    - 自动计算下次触发时间
    """
    try:
        logger.info(f"用户 {current_user.username} 创建提醒设置", extra={
            "user_id": str(current_user.id),
            "reminder_type": setting_data.reminder_type,
            "card_id": str(setting_data.card_id) if setting_data.card_id else None
        })
        
        # TODO: 实现提醒设置创建服务
        # if setting_data.card_id:
        #     # 验证信用卡所有权
        #     card = card_service.get_user_card(current_user.id, setting_data.card_id)
        #     if not card:
        #         raise HTTPException(status_code=404, detail="信用卡不存在")
        
        # 检查是否已存在相同类型的提醒设置
        # existing = reminder_service.get_existing_setting(
        #     user_id=current_user.id,
        #     card_id=setting_data.card_id,
        #     reminder_type=setting_data.reminder_type
        # )
        # if existing:
        #     raise HTTPException(status_code=409, detail="该类型的提醒设置已存在")
        
        # setting = reminder_service.create_reminder_setting(
        #     user_id=current_user.id,
        #     setting_data=setting_data
        # )
        
        # 模拟创建
        setting = ReminderSettingResponse(
            id=UUID("123e4567-e89b-12d3-a456-426614174002"),
            user_id=current_user.id,
            card_id=setting_data.card_id,
            card_name="招商银行信用卡" if setting_data.card_id else None,
            reminder_type=setting_data.reminder_type,
            advance_days=setting_data.advance_days,
            reminder_time=setting_data.reminder_time,
            email_enabled=setting_data.email_enabled,
            push_enabled=setting_data.push_enabled,
            sms_enabled=setting_data.sms_enabled,
            wechat_enabled=setting_data.wechat_enabled,
            in_app_enabled=setting_data.in_app_enabled,
            is_recurring=setting_data.is_recurring,
            frequency=setting_data.frequency,
            custom_message=setting_data.custom_message,
            threshold_amount=setting_data.threshold_amount,
            threshold_percentage=setting_data.threshold_percentage,
            is_enabled=setting_data.is_enabled,
            status="active",
            next_trigger_date=date(2024, 12, 15),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return ResponseUtil.success(data=setting, message="提醒设置创建成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建提醒设置失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="创建提醒设置失败")


@router.get(
    "/settings/{setting_id}",
    response_model=BaseResponse[ReminderSettingResponse],
    summary="获取提醒设置详情",
    description="获取指定提醒设置的详细信息"
)
async def get_reminder_setting(
    setting_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒设置详情"""
    try:
        logger.info(f"用户 {current_user.username} 查询提醒设置详情", extra={
            "user_id": str(current_user.id),
            "setting_id": str(setting_id)
        })
        
        # TODO: 实现设置查询服务
        # setting = reminder_service.get_user_reminder_setting(current_user.id, setting_id)
        # if not setting:
        #     raise HTTPException(status_code=404, detail="提醒设置不存在")
        
        # 模拟数据
        setting = ReminderSettingResponse(
            id=setting_id,
            user_id=current_user.id,
            card_id=UUID("card-uuid-1"),
            card_name="招商银行信用卡",
            reminder_type=ReminderType.PAYMENT_DUE,
            advance_days=3,
            reminder_time="09:00:00",
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False,
            wechat_enabled=False,
            in_app_enabled=True,
            is_recurring=True,
            frequency="monthly",
            is_enabled=True,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return ResponseUtil.success(data=setting, message="提醒设置详情获取成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询提醒设置详情失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "setting_id": str(setting_id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询提醒设置详情失败")


@router.put(
    "/settings/{setting_id}",
    response_model=BaseResponse[ReminderSettingResponse],
    summary="更新提醒设置",
    description="更新指定提醒设置的配置信息"
)
async def update_reminder_setting(
    setting_id: UUID,
    update_data: ReminderSettingUpdate,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新提醒设置"""
    try:
        logger.info(f"用户 {current_user.username} 更新提醒设置", extra={
            "user_id": str(current_user.id),
            "setting_id": str(setting_id),
            "update_fields": list(update_data.dict(exclude_unset=True).keys())
        })
        
        # TODO: 实现设置更新服务
        # setting = reminder_service.get_user_reminder_setting(current_user.id, setting_id)
        # if not setting:
        #     raise HTTPException(status_code=404, detail="提醒设置不存在")
        
        # updated_setting = reminder_service.update_reminder_setting(
        #     setting_id=setting_id,
        #     update_data=update_data
        # )
        
        # 模拟更新
        updated_setting = ReminderSettingResponse(
            id=setting_id,
            user_id=current_user.id,
            card_id=UUID("card-uuid-1"),
            card_name="招商银行信用卡",
            reminder_type=ReminderType.PAYMENT_DUE,
            advance_days=update_data.advance_days or 3,
            reminder_time=update_data.reminder_time or "09:00:00",
            email_enabled=update_data.email_enabled or True,
            push_enabled=update_data.push_enabled or True,
            sms_enabled=update_data.sms_enabled or False,
            wechat_enabled=update_data.wechat_enabled or False,
            in_app_enabled=update_data.in_app_enabled or True,
            is_recurring=True,
            frequency=update_data.frequency or "monthly",
            custom_message=update_data.custom_message,
            threshold_amount=update_data.threshold_amount,
            threshold_percentage=update_data.threshold_percentage,
            is_enabled=update_data.is_enabled or True,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return ResponseUtil.success(data=updated_setting, message="提醒设置更新成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新提醒设置失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "setting_id": str(setting_id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="更新提醒设置失败")


@router.delete(
    "/settings/{setting_id}",
    response_model=BaseResponse,
    summary="删除提醒设置",
    description="删除指定的提醒设置"
)
async def delete_reminder_setting(
    setting_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除提醒设置"""
    try:
        logger.info(f"用户 {current_user.username} 删除提醒设置", extra={
            "user_id": str(current_user.id),
            "setting_id": str(setting_id)
        })
        
        # TODO: 实现设置删除服务
        # setting = reminder_service.get_user_reminder_setting(current_user.id, setting_id)
        # if not setting:
        #     raise HTTPException(status_code=404, detail="提醒设置不存在")
        
        # reminder_service.delete_reminder_setting(setting_id)
        
        return ResponseUtil.success(message="提醒设置删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除提醒设置失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "setting_id": str(setting_id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="删除提醒设置失败")


# ================================
# 提醒记录管理接口
# ================================

@router.get(
    "/logs",
    response_model=ReminderLogListResponse,
    summary="获取我的提醒记录",
    description="获取当前用户的提醒记录，支持分页和多条件筛选"
)
async def get_my_reminder_logs(
    query_params: ReminderLogQuery = Depends(),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的提醒记录列表
    
    支持的筛选条件：
    - reminder_type: 按提醒类型筛选
    - overall_status: 按发送状态筛选
    - is_read: 按阅读状态筛选
    - date_range: 按时间范围筛选
    """
    try:
        logger.info(f"用户 {current_user.username} 查询提醒记录", extra={
            "user_id": str(current_user.id),
            "query_params": query_params.dict()
        })
        
        # TODO: 实现提醒记录查询服务
        # logs, total = reminder_service.get_user_reminder_logs(
        #     user_id=current_user.id,
        #     query_params=query_params
        # )
        
        # 模拟数据
        logs = [
            ReminderLogResponse(
                id=UUID("log-uuid-1"),
                setting_id=UUID("setting-uuid-1"),
                user_id=current_user.id,
                card_id=UUID("card-uuid-1"),
                reminder_type=ReminderType.PAYMENT_DUE,
                title="信用卡还款提醒",
                content="您的招商银行信用卡将于3天后到期，请及时还款",
                card_name="招商银行信用卡",
                related_amount=1500.00,
                related_date=date(2024, 12, 15),
                overall_status="sent",
                email_status="delivered",
                push_status="sent",
                sms_status="pending",
                wechat_status="pending",
                in_app_status="read",
                is_read=False,
                scheduled_at=datetime.now(),
                sent_at=datetime.now(),
                created_at=datetime.now(),
                retry_count=0
            )
        ]
        total = 1
        
        return ResponseUtil.paginated(
            data=logs,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size,
            message="提醒记录查询成功"
        )
        
    except Exception as e:
        logger.error(f"查询提醒记录失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询提醒记录失败")


@router.post(
    "/logs/{log_id}/mark-read",
    response_model=BaseResponse,
    summary="标记提醒为已读",
    description="将指定的提醒记录标记为已读状态"
)
async def mark_reminder_as_read(
    log_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记提醒为已读"""
    try:
        logger.info(f"用户 {current_user.username} 标记提醒已读", extra={
            "user_id": str(current_user.id),
            "log_id": str(log_id)
        })
        
        # TODO: 实现标记已读服务
        # log = reminder_service.get_user_reminder_log(current_user.id, log_id)
        # if not log:
        #     raise HTTPException(status_code=404, detail="提醒记录不存在")
        
        # reminder_service.mark_reminder_as_read(log_id)
        
        return ResponseUtil.success(message="提醒已标记为已读")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记提醒已读失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "log_id": str(log_id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="标记提醒已读失败")


@router.post(
    "/logs/{log_id}/snooze",
    response_model=BaseResponse,
    summary="延后提醒",
    description="将提醒延后指定时间后再次发送"
)
async def snooze_reminder(
    log_id: UUID,
    snooze_data: SnoozeReminderRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """延后提醒"""
    try:
        logger.info(f"用户 {current_user.username} 延后提醒", extra={
            "user_id": str(current_user.id),
            "log_id": str(log_id),
            "snooze_minutes": snooze_data.snooze_minutes
        })
        
        # TODO: 实现延后提醒服务
        # log = reminder_service.get_user_reminder_log(current_user.id, log_id)
        # if not log:
        #     raise HTTPException(status_code=404, detail="提醒记录不存在")
        
        # 计算新的发送时间
        # new_schedule_time = datetime.now() + timedelta(minutes=snooze_data.snooze_minutes)
        # 
        # reminder_service.snooze_reminder(
        #     log_id=log_id,
        #     new_schedule_time=new_schedule_time,
        #     reason=snooze_data.reason
        # )
        
        # 添加后台任务重新发送
        # background_tasks.add_task(
        #     reminder_service.schedule_delayed_reminder,
        #     log_id,
        #     new_schedule_time
        # )
        
        return ResponseUtil.success(
            message=f"提醒已延后 {snooze_data.snooze_minutes} 分钟"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"延后提醒失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "log_id": str(log_id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="延后提醒失败")


# ================================
# 批量操作接口
# ================================

@router.post(
    "/batch-operations",
    response_model=BaseResponse[BatchOperationResult],
    summary="批量操作提醒",
    description="对多个提醒设置执行批量操作（启用/禁用/删除）"
)
async def batch_reminder_operations(
    operation_data: BatchReminderOperation,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量操作提醒设置"""
    try:
        logger.info(f"用户 {current_user.username} 执行批量操作", extra={
            "user_id": str(current_user.id),
            "operation": operation_data.operation,
            "count": len(operation_data.reminder_ids)
        })
        
        # TODO: 实现批量操作服务
        # result = reminder_service.batch_operate_reminders(
        #     user_id=current_user.id,
        #     operation_data=operation_data
        # )
        
        # 模拟批量操作
        success_count = len(operation_data.reminder_ids) - 1  # 模拟一个失败
        failed_count = 1
        
        result = BatchOperationResult(
            total_count=len(operation_data.reminder_ids),
            success_count=success_count,
            failed_count=failed_count,
            failed_items=[
                {
                    "id": str(operation_data.reminder_ids[-1]),
                    "error": "提醒设置不存在或已删除"
                }
            ] if failed_count > 0 else []
        )
        
        return ResponseUtil.success(
            data=result,
            message=f"批量{operation_data.operation}操作完成"
        )
        
    except Exception as e:
        logger.error(f"批量操作失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "operation": operation_data.operation,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="批量操作失败")


# ================================
# 统计分析接口
# ================================

@router.get(
    "/statistics",
    response_model=ReminderStatisticsResponse,
    summary="获取提醒统计数据",
    description="获取用户提醒设置和发送的统计分析数据"
)
async def get_reminder_statistics(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒统计数据"""
    try:
        logger.info(f"用户 {current_user.username} 查询提醒统计", extra={
            "user_id": str(current_user.id)
        })
        
        # TODO: 实现统计服务
        # stats = reminder_service.get_user_reminder_statistics(current_user.id)
        
        # 模拟统计数据
        stats = ReminderStatistics(
            total_settings=15,
            active_settings=12,
            type_distribution={
                "payment_due": 8,
                "annual_fee": 4,
                "balance_alert": 3
            },
            channel_usage={
                "email": 12,
                "push": 15,
                "sms": 3,
                "wechat": 2
            },
            total_sent=156,
            delivery_rate=94.5,
            read_rate=67.3,
            recent_reminders=[]
        )
        
        return ResponseUtil.success(data=stats, message="提醒统计查询成功")
        
    except Exception as e:
        logger.error(f"查询提醒统计失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询提醒统计失败")


@router.get(
    "/trends",
    response_model=ReminderTrendResponse,
    summary="获取提醒趋势数据",
    description="获取指定时间范围内的提醒发送趋势数据"
)
async def get_reminder_trends(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒趋势数据"""
    try:
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
        
        logger.info(f"用户 {current_user.username} 查询提醒趋势", extra={
            "user_id": str(current_user.id),
            "date_range": f"{start_date} to {end_date}"
        })
        
        # TODO: 实现趋势数据服务
        # trends = reminder_service.get_user_reminder_trends(
        #     user_id=current_user.id,
        #     start_date=start_date,
        #     end_date=end_date
        # )
        
        # 模拟趋势数据
        trends = [
            ReminderTrendData(
                date=date(2024, 12, 1),
                sent_count=25,
                delivered_count=23,
                read_count=15,
                failed_count=2
            ),
            ReminderTrendData(
                date=date(2024, 12, 2),
                sent_count=18,
                delivered_count=17,
                read_count=12,
                failed_count=1
            )
        ]
        
        return ResponseUtil.success(data=trends, message="趋势数据查询成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询提醒趋势失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询提醒趋势失败")


# ================================
# 特殊功能接口
# ================================

@router.post(
    "/test-reminder",
    response_model=BaseResponse,
    summary="测试提醒发送",
    description="发送测试提醒到指定渠道，用于测试提醒配置"
)
async def test_reminder_delivery(
    test_data: TestReminderRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """测试提醒发送"""
    try:
        logger.info(f"用户 {current_user.username} 测试提醒发送", extra={
            "user_id": str(current_user.id),
            "channels": test_data.channels
        })
        
        # TODO: 实现测试发送服务
        # background_tasks.add_task(
        #     reminder_service.send_test_reminder,
        #     user_id=current_user.id,
        #     channels=test_data.channels,
        #     message=test_data.test_message
        # )
        
        return ResponseUtil.success(
            message=f"测试提醒已发送到 {', '.join(test_data.channels)} 渠道"
        )
        
    except Exception as e:
        logger.error(f"测试提醒发送失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="测试提醒发送失败")


@router.post(
    "/quick-setup",
    response_model=BaseResponse,
    summary="快速设置提醒",
    description="使用预设模板快速为信用卡设置提醒"
)
async def quick_reminder_setup(
    setup_data: QuickReminderSetup,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """快速设置提醒"""
    try:
        logger.info(f"用户 {current_user.username} 快速设置提醒", extra={
            "user_id": str(current_user.id),
            "preset_type": setup_data.preset_type,
            "cards_count": len(setup_data.cards) if setup_data.cards else 0
        })
        
        # TODO: 实现快速设置服务
        # reminder_service.quick_setup_reminders(
        #     user_id=current_user.id,
        #     preset_type=setup_data.preset_type,
        #     card_ids=setup_data.cards
        # )
        
        preset_names = {
            "basic": "基础提醒配置",
            "advanced": "高级提醒配置",
            "custom": "自定义提醒配置"
        }
        
        return ResponseUtil.success(
            message=f"{preset_names[setup_data.preset_type]}设置成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"快速设置提醒失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="快速设置提醒失败")


# ================================
# 模板管理接口
# ================================

@router.get(
    "/templates",
    response_model=ReminderTemplateListResponse,
    summary="获取提醒模板列表",
    description="获取系统和用户自定义的提醒模板列表"
)
async def get_reminder_templates(
    reminder_type: Optional[ReminderType] = Query(None, description="按提醒类型筛选"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取提醒模板列表"""
    try:
        logger.info(f"用户 {current_user.username} 查询提醒模板", extra={
            "user_id": str(current_user.id),
            "reminder_type": reminder_type
        })
        
        # TODO: 实现模板查询服务
        # templates = reminder_service.get_reminder_templates(
        #     user_id=current_user.id,
        #     reminder_type=reminder_type
        # )
        
        # 模拟模板数据
        templates = [
            ReminderTemplate(
                id="payment_due_default",
                name="默认还款提醒",
                reminder_type=ReminderType.PAYMENT_DUE,
                title_template="{card_name}还款提醒",
                content_template="您的{card_name}将于{days}天后到期，请及时还款{amount}元",
                variables=["card_name", "days", "amount", "due_date"],
                is_system=True
            ),
            ReminderTemplate(
                id="annual_fee_default",
                name="默认年费提醒",
                reminder_type=ReminderType.ANNUAL_FEE,
                title_template="{card_name}年费提醒",
                content_template="您的{card_name}年费{amount}元即将到期，到期日：{due_date}",
                variables=["card_name", "amount", "due_date"],
                is_system=True
            )
        ]
        
        # 按类型筛选
        if reminder_type:
            templates = [t for t in templates if t.reminder_type == reminder_type]
        
        return ResponseUtil.success(data=templates, message="模板列表查询成功")
        
    except Exception as e:
        logger.error(f"查询提醒模板失败: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询提醒模板失败")


# ================================
# 健康检查接口
# ================================

@router.get(
    "/health",
    response_model=BaseResponse,
    summary="提醒服务健康检查",
    description="检查提醒服务的运行状态"
)
async def reminder_health_check():
    """提醒服务健康检查"""
    try:
        # TODO: 实现健康检查服务
        # health_status = reminder_service.check_health()
        
        health_status = {
            "service": "healthy",
            "database": "connected",
            "notification_channels": {
                "email": "available",
                "sms": "available", 
                "push": "available"
            },
            "pending_reminders": 0,
            "last_check": datetime.now().isoformat()
        }
        
        return ResponseUtil.success(
            data=health_status,
            message="提醒服务运行正常"
        )
        
    except Exception as e:
        logger.error(f"提醒服务健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="提醒服务健康检查失败")