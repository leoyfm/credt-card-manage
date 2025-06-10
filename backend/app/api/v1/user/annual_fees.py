"""
用户功能区 - 年费管理接口

本模块提供用户个人年费管理的所有接口：
- 年费规则管理
- 年费记录查询
- 减免进度跟踪
- 年费统计分析

权限等级: Level 2 (用户认证)
数据范围: 仅自有年费数据

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
from app.models.schemas.annual_fee import (
    AnnualFeeRuleCreateRequest, AnnualFeeRuleUpdateRequest, AnnualFeeRuleResponse,
    AnnualFeeRecordCreateRequest, AnnualFeeRecordUpdateRequest, 
    AnnualFeeRecordResponse, AnnualFeeRecordDetailResponse,
    AnnualFeeListQuery, AnnualFeeStatistics, AnnualFeeAnalysisReport,
    WaiverProgress, AnnualFeeReminderSettings, AnnualFeeReminder,
    AnnualFeeBatchRequest, AnnualFeeBatchResponse, AnnualFeeOptimization
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse, SuccessMessage
from app.services.annual_fees_service import AnnualFeesService
from app.utils.response import ResponseUtil

# 配置日志和路由
logger = get_logger(__name__)
router = APIRouter(
    prefix="/annual-fees",
    tags=["v1-用户-年费管理"]
)

@router.get(
    "/rules/list",
    response_model=ApiPagedResponse[AnnualFeeRuleResponse],
    summary="获取我的年费规则列表",
    response_description="返回当前用户的年费规则列表"
)
async def get_my_annual_fee_rules(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="搜索关键词，支持卡片名称、银行名称模糊搜索"),
    fee_type: Optional[str] = Query(None, description="年费类型筛选：rigid, waiver_by_transactions, waiver_by_amount, waiver_by_points"),
    card_id: Optional[UUID] = Query(None, description="信用卡筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用筛选"),
    sort_by: str = Query("created_at", description="排序字段：created_at, effective_date, base_fee"),
    sort_order: str = Query("desc", description="排序方向：asc, desc"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的年费规则列表
    
    显示用户设置的所有年费规则：
    - 支持按卡片、类型筛选
    - 显示规则状态和生效期
    - 包含减免条件配置
    - 支持多种排序方式
    
    帮助用户管理和监控年费规则
    """
    try:
        logger.info("用户查询年费规则列表", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   page=page, 
                   page_size=page_size,
                   keyword=keyword)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 构建查询参数
        query_params = AnnualFeeListQuery(
            keyword=keyword,
            fee_type=fee_type,
            card_id=card_id,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # 获取用户年费规则列表
        rules, total = annual_fees_service.get_user_annual_fee_rules(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            query_params=query_params,
            is_active=is_active
        )
        
        return ResponseUtil.paginated(
            items=rules,
            total=total,
            page=page,
            page_size=page_size,
            message="获取年费规则列表成功"
        )
        
    except Exception as e:
        logger.error("获取年费规则列表异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费规则列表失败，请稍后重试")


@router.post(
    "/rules/create",
    response_model=ApiResponse[AnnualFeeRuleResponse],
    summary="创建年费规则",
    response_description="返回新创建的年费规则信息"
)
async def create_annual_fee_rule(
    rule_data: AnnualFeeRuleCreateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的年费规则
    
    用户可以为信用卡设置年费规则：
    - 支持多种年费类型（刚性、条件减免）
    - 灵活配置减免条件
    - 设置提醒和自动续费
    - 自动生成年费记录
    
    帮助用户管理年费支出和减免
    """
    try:
        logger.info("用户创建年费规则", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_id=rule_data.card_id,
                   fee_type=rule_data.fee_type,
                   base_fee=rule_data.base_fee)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 验证信用卡归属
        card_belongs = annual_fees_service.verify_card_ownership(
            user_id=current_user.id,
            card_id=rule_data.card_id
        )
        if not card_belongs:
            return ResponseUtil.validation_error("信用卡不存在或无权访问")
        
        # 检查是否已存在活跃规则
        existing_rule = annual_fees_service.check_existing_active_rule(
            user_id=current_user.id,
            card_id=rule_data.card_id
        )
        if existing_rule:
            return ResponseUtil.validation_error("该信用卡已存在活跃的年费规则")
        
        # 创建年费规则
        new_rule = annual_fees_service.create_user_annual_fee_rule(
            user_id=current_user.id,
            rule_data=rule_data
        )
        
        if not new_rule:
            return ResponseUtil.error("创建年费规则失败")
        
        logger.info("用户创建年费规则成功", 
                   user_id=current_user.id, 
                   rule_id=new_rule.id,
                   fee_type=new_rule.fee_type)
        
        return ResponseUtil.created(
            data=new_rule,
            message="年费规则创建成功"
        )
        
    except ValueError as e:
        logger.warning("创建年费规则参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("创建年费规则异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("创建年费规则失败，请稍后重试")


@router.get(
    "/records/list",
    response_model=ApiPagedResponse[AnnualFeeRecordResponse],
    summary="获取我的年费记录列表",
    response_description="返回当前用户的年费记录列表"
)
async def get_my_annual_fee_records(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="搜索关键词，支持卡片名称、银行名称模糊搜索"),
    fee_type: Optional[str] = Query(None, description="年费类型筛选"),
    status: Optional[str] = Query(None, description="年费状态筛选：pending, paid, waived, overdue"),
    card_id: Optional[UUID] = Query(None, description="信用卡筛选"),
    fee_year: Optional[int] = Query(None, description="年费年度筛选"),
    waiver_status: Optional[str] = Query(None, description="减免状态筛选：not_applicable, in_progress, completed, failed"),
    is_overdue: Optional[bool] = Query(None, description="是否逾期筛选"),
    due_soon: Optional[bool] = Query(None, description="是否即将到期筛选（30天内）"),
    sort_by: str = Query("due_date", description="排序字段：due_date, fee_year, created_at, actual_fee"),
    sort_order: str = Query("asc", description="排序方向：asc, desc"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的年费记录列表
    
    显示用户的所有年费记录：
    - 按状态、年度、卡片筛选
    - 显示到期提醒和逾期状态
    - 跟踪减免进度
    - 支持多维度排序
    
    帮助用户掌控年费缴费情况
    """
    try:
        logger.info("用户查询年费记录列表", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   page=page, 
                   page_size=page_size,
                   keyword=keyword)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 构建查询参数
        query_params = AnnualFeeListQuery(
            keyword=keyword,
            fee_type=fee_type,
            status=status,
            card_id=card_id,
            fee_year=fee_year,
            waiver_status=waiver_status,
            is_overdue=is_overdue,
            due_soon=due_soon,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # 获取用户年费记录列表
        records, total = annual_fees_service.get_user_annual_fee_records(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            query_params=query_params
        )
        
        return ResponseUtil.paginated(
            items=records,
            total=total,
            page=page,
            page_size=page_size,
            message="获取年费记录列表成功"
        )
        
    except Exception as e:
        logger.error("获取年费记录列表异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费记录列表失败，请稍后重试")


@router.get(
    "/records/{record_id}/details",
    response_model=ApiResponse[AnnualFeeRecordDetailResponse],
    summary="获取年费记录详情",
    response_description="返回指定年费记录的详细信息"
)
async def get_annual_fee_record_details(
    record_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定年费记录的详细信息
    
    包含完整的年费记录详情：
    - 年费规则和减免条件
    - 缴费历史和减免进度
    - 相关交易和积分记录
    - 下次缴费预测
    
    只能查看自己的年费记录详情
    """
    try:
        logger.info("用户查看年费记录详情", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   record_id=record_id)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 获取年费记录详情
        record_detail = annual_fees_service.get_user_annual_fee_record_detail(
            user_id=current_user.id,
            record_id=record_id
        )
        
        if not record_detail:
            return ResponseUtil.not_found("年费记录不存在或无权访问")
        
        return ResponseUtil.success(
            data=record_detail,
            message="获取年费记录详情成功"
        )
        
    except Exception as e:
        logger.error("获取年费记录详情异常", error=str(e), user_id=current_user.id, record_id=record_id)
        return ResponseUtil.error("获取年费记录详情失败，请稍后重试")


@router.put(
    "/records/{record_id}/status",
    response_model=ApiResponse[SuccessMessage],
    summary="更新年费记录状态",
    response_description="返回状态更新结果"
)
async def update_annual_fee_record_status(
    record_id: UUID,
    record_data: AnnualFeeRecordUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新年费记录状态
    
    用户可以更新年费状态：
    - 标记为已缴费
    - 申请减免
    - 添加缴费备注
    - 更新实际缴费金额
    
    状态变更会自动更新相关统计
    """
    try:
        logger.info("用户更新年费记录状态", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   record_id=record_id,
                   new_status=record_data.status)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 更新年费记录状态
        updated_record = annual_fees_service.update_user_annual_fee_record(
            user_id=current_user.id,
            record_id=record_id,
            record_data=record_data
        )
        
        if not updated_record:
            return ResponseUtil.not_found("年费记录不存在或无权访问")
        
        status_text = {
            "pending": "待缴费",
            "paid": "已缴费",
            "waived": "已减免",
            "overdue": "逾期未缴"
        }.get(record_data.status or updated_record.status, "未知")
        
        logger.info("用户更新年费记录状态成功", 
                   user_id=current_user.id, 
                   record_id=record_id,
                   status=updated_record.status)
        
        return ResponseUtil.success(
            data={"message": f"年费状态已更新为{status_text}", "timestamp": None},
            message=f"年费状态更新成功，已标记为{status_text}"
        )
        
    except ValueError as e:
        logger.warning("更新年费记录状态参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新年费记录状态异常", error=str(e), user_id=current_user.id, record_id=record_id)
        return ResponseUtil.error("更新年费记录状态失败，请稍后重试")


@router.get(
    "/waiver/{record_id}/progress",
    response_model=ApiResponse[WaiverProgress],
    summary="获取年费减免进度",
    response_description="返回年费减免进度信息"
)
async def get_waiver_progress(
    record_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取年费减免进度
    
    显示减免条件完成情况：
    - 当前进度和目标要求
    - 完成百分比和预计时间
    - 具体的完成建议
    - 相关交易和积分统计
    
    帮助用户了解减免进度和优化策略
    """
    try:
        logger.info("用户查看年费减免进度", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   record_id=record_id)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 获取减免进度
        waiver_progress = annual_fees_service.get_user_waiver_progress(
            user_id=current_user.id,
            record_id=record_id
        )
        
        if not waiver_progress:
            return ResponseUtil.not_found("年费记录不存在或无减免条件")
        
        return ResponseUtil.success(
            data=waiver_progress,
            message="获取年费减免进度成功"
        )
        
    except Exception as e:
        logger.error("获取年费减免进度异常", error=str(e), user_id=current_user.id, record_id=record_id)
        return ResponseUtil.error("获取年费减免进度失败，请稍后重试")


@router.get(
    "/statistics",
    response_model=ApiResponse[AnnualFeeStatistics],
    summary="获取我的年费统计",
    response_description="返回当前用户的年费统计数据"
)
async def get_my_annual_fee_statistics(
    year: Optional[int] = Query(None, description="统计年度，默认当前年度"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的年费统计数据
    
    提供全面的年费分析：
    - 年费规则和记录统计
    - 缴费、减免、逾期分布
    - 按银行、类型分组统计
    - 减免成功率分析
    - 即将到期提醒
    
    支持按年度筛选统计
    """
    try:
        logger.info("用户查看年费统计", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   year=year)
        
        annual_fees_service = AnnualFeesService(db)
        statistics = annual_fees_service.get_user_annual_fee_statistics(
            user_id=current_user.id,
            year=year
        )
        
        return ResponseUtil.success(
            data=statistics,
            message="获取年费统计成功"
        )
        
    except Exception as e:
        logger.error("获取年费统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费统计失败，请稍后重试")


@router.get(
    "/analysis",
    response_model=ApiResponse[AnnualFeeAnalysisReport],
    summary="获取年费分析报告",
    response_description="返回详细的年费分析报告"
)
async def get_annual_fee_analysis(
    year: Optional[int] = Query(None, description="分析年度，默认当前年度"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取详细的年费分析报告
    
    提供深度年费分析：
    - 成本效益分析
    - 减免策略效果
    - 年费趋势预测
    - 优化建议
    - 下年度规划
    
    帮助用户制定年费管理策略
    """
    try:
        logger.info("用户查看年费分析报告", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   year=year)
        
        annual_fees_service = AnnualFeesService(db)
        analysis_report = annual_fees_service.get_user_annual_fee_analysis(
            user_id=current_user.id,
            year=year
        )
        
        return ResponseUtil.success(
            data=analysis_report,
            message="获取年费分析报告成功"
        )
        
    except Exception as e:
        logger.error("获取年费分析异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费分析失败，请稍后重试")


@router.get(
    "/reminders",
    response_model=ApiResponse[List[AnnualFeeReminder]],
    summary="获取年费提醒",
    response_description="返回当前用户的年费提醒信息"
)
async def get_annual_fee_reminders(
    priority: Optional[str] = Query(None, description="优先级筛选：low, medium, high, urgent"),
    reminder_type: Optional[str] = Query(None, description="提醒类型筛选：due_soon, overdue, waiver_opportunity"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取年费提醒信息
    
    显示重要的年费提醒：
    - 即将到期提醒
    - 逾期缴费提醒
    - 减免机会提醒
    - 按优先级排序
    
    帮助用户及时处理年费事务
    """
    try:
        logger.info("用户查看年费提醒", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   priority=priority,
                   reminder_type=reminder_type)
        
        annual_fees_service = AnnualFeesService(db)
        reminders = annual_fees_service.get_user_annual_fee_reminders(
            user_id=current_user.id,
            priority=priority,
            reminder_type=reminder_type
        )
        
        return ResponseUtil.success(
            data=reminders,
            message="获取年费提醒成功"
        )
        
    except Exception as e:
        logger.error("获取年费提醒异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费提醒失败，请稍后重试")


@router.get(
    "/optimization",
    response_model=ApiResponse[AnnualFeeOptimization],
    summary="获取年费优化建议",
    response_description="返回个性化的年费优化建议"
)
async def get_annual_fee_optimization(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取个性化的年费优化建议
    
    提供智能优化建议：
    - 成本节约机会分析
    - 减免策略优化
    - 卡片组合建议
    - 实施步骤指导
    - 风险评估
    
    帮助用户最大化年费效益
    """
    try:
        logger.info("用户查看年费优化建议", 
                   user_id=current_user.id, 
                   username=current_user.username)
        
        annual_fees_service = AnnualFeesService(db)
        optimization = annual_fees_service.get_user_annual_fee_optimization(
            user_id=current_user.id
        )
        
        return ResponseUtil.success(
            data=optimization,
            message="获取年费优化建议成功"
        )
        
    except Exception as e:
        logger.error("获取年费优化建议异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取年费优化建议失败，请稍后重试")


@router.put(
    "/rules/{rule_id}/settings",
    response_model=ApiResponse[SuccessMessage],
    summary="更新年费提醒设置",
    response_description="返回提醒设置更新结果"
)
async def update_reminder_settings(
    rule_id: UUID,
    settings: AnnualFeeReminderSettings,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新年费提醒设置
    
    用户可以自定义提醒设置：
    - 设置提醒天数和方式
    - 自定义提醒消息
    - 启用/禁用特定提醒类型
    - 配置多渠道通知
    
    帮助用户个性化年费提醒
    """
    try:
        logger.info("用户更新年费提醒设置", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   rule_id=rule_id)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 更新提醒设置
        success = annual_fees_service.update_user_reminder_settings(
            user_id=current_user.id,
            rule_id=rule_id,
            settings=settings
        )
        
        if not success:
            return ResponseUtil.not_found("年费规则不存在或无权访问")
        
        logger.info("用户更新年费提醒设置成功", 
                   user_id=current_user.id, 
                   rule_id=rule_id)
        
        return ResponseUtil.success(
            data={"message": "年费提醒设置已更新", "timestamp": None},
            message="年费提醒设置更新成功"
        )
        
    except ValueError as e:
        logger.warning("更新年费提醒设置参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新年费提醒设置异常", error=str(e), user_id=current_user.id, rule_id=rule_id)
        return ResponseUtil.error("更新年费提醒设置失败，请稍后重试")


@router.post(
    "/batch",
    response_model=ApiResponse[AnnualFeeBatchResponse],
    summary="批量处理年费",
    response_description="返回批量处理结果"
)
async def batch_process_annual_fees(
    batch_data: AnnualFeeBatchRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量处理年费记录
    
    支持批量操作：
    - 批量标记缴费
    - 批量申请减免
    - 批量延期到期日
    - 批量更新状态
    
    一次最多处理50条记录
    """
    try:
        logger.info("用户批量处理年费", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   record_count=len(batch_data.record_ids),
                   operation=batch_data.operation)
        
        annual_fees_service = AnnualFeesService(db)
        
        # 执行批量处理
        batch_result = annual_fees_service.batch_process_user_annual_fees(
            user_id=current_user.id,
            batch_data=batch_data
        )
        
        logger.info("用户批量处理年费完成", 
                   user_id=current_user.id,
                   success_count=batch_result.success_count,
                   failed_count=batch_result.failed_count)
        
        return ResponseUtil.success(
            data=batch_result,
            message=f"批量处理完成，成功{batch_result.success_count}个，失败{batch_result.failed_count}个"
        )
        
    except ValueError as e:
        logger.warning("批量处理年费参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("批量处理年费异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("批量处理年费失败，请稍后重试") 