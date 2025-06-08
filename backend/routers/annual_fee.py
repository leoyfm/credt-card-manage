import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from utils.response import ResponseUtil
from models.response import ApiResponse, ApiPagedResponse
from models.annual_fee import (
    AnnualFeeRecord,
    AnnualFeeRecordCreate,
    AnnualFeeRecordUpdate,
    AnnualFeeRule,
    AnnualFeeRuleCreate,
    AnnualFeeRuleUpdate,
    AnnualFeeStatistics,
    AnnualFeeWaiverCheck,
    FeeType,
    WaiverStatus,
)
from services.annual_fee_service import AnnualFeeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/annual-fees", tags=["年费管理"])


def get_annual_fee_service(db: Session = Depends(get_db)) -> AnnualFeeService:
    """获取年费服务实例"""
    return AnnualFeeService(db)


# ==================== 年费规则相关接口 ====================

@router.post(
    "/rules", 
    response_model=ApiResponse[AnnualFeeRule], 
    summary="创建年费规则",
    response_description="返回创建的年费规则信息"
)
async def create_annual_fee_rule(
    rule_data: AnnualFeeRuleCreate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """
    创建新的年费规则
    
    创建新的年费减免规则，支持多种年费类型：
    - rigid: 刚性年费，不可减免
    - transaction_count: 刷卡次数减免
    - transaction_amount: 刷卡金额减免
    - points_exchange: 积分兑换减免
    
    参数:
    - rule_data: 年费规则创建数据
    """
    logger.info(f"创建年费规则请求 - rule_name: {rule_data.rule_name}, fee_type: {rule_data.fee_type}")
    
    try:
        rule = service.create_annual_fee_rule(rule_data)
        logger.info(f"年费规则创建成功 - rule_id: {rule.id}")
        return ResponseUtil.created(data=rule, message="年费规则创建成功")
    except Exception as e:
        logger.error(f"创建年费规则失败: {str(e)}")
        return ResponseUtil.error(message=f"创建年费规则失败: {str(e)}")


@router.get(
    "/rules", 
    response_model=ApiPagedResponse[AnnualFeeRule], 
    summary="获取年费规则列表",
    response_description="返回分页的年费规则列表"
)
async def get_annual_fee_rules(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="模糊搜索关键词，支持规则名称、描述搜索"),
    fee_type: Optional[FeeType] = Query(None, description="按年费类型筛选"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """
    获取年费规则列表
    
    获取系统中所有的年费规则，支持分页、模糊搜索和类型过滤。
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量，默认20，最大100
    - keyword: 搜索关键词，支持规则名称、描述模糊匹配
    - fee_type: 年费类型过滤，可选值：rigid、transaction_count、transaction_amount、points_exchange
    """
    skip = ResponseUtil.calculate_skip(page, page_size)
    rules, total = service.get_annual_fee_rules(
        skip=skip, 
        limit=page_size, 
        fee_type=fee_type,
        keyword=keyword
    )
    return ResponseUtil.paginated(
        items=rules, 
        total=total, 
        page=page, 
        page_size=page_size, 
        message="获取年费规则列表成功"
    )


@router.get(
    "/rules/{rule_id}", 
    response_model=ApiResponse[AnnualFeeRule], 
    summary="获取年费规则详情",
    response_description="返回指定ID的年费规则详细信息"
)
async def get_annual_fee_rule(
    rule_id: UUID,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """
    根据ID获取年费规则详情
    
    获取指定年费规则的详细信息，包括规则名称、年费类型、
    减免条件、考核周期等完整信息。
    
    参数:
    - rule_id: 年费规则的UUID
    """
    rule = service.get_annual_fee_rule(rule_id)
    if not rule:
        return ResponseUtil.not_found(message="年费规则不存在")
    return ResponseUtil.success(data=rule, message="获取年费规则详情成功")


@router.put("/rules/{rule_id}", response_model=ApiResponse[AnnualFeeRule], summary="更新年费规则")
async def update_annual_fee_rule(
    rule_id: UUID,
    rule_data: AnnualFeeRuleUpdate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """更新年费规则"""
    rule = service.update_annual_fee_rule(rule_id, rule_data)
    if not rule:
        return ResponseUtil.not_found(message="年费规则不存在")
    return ResponseUtil.success(data=rule, message="年费规则更新成功")


@router.delete("/rules/{rule_id}", response_model=ApiResponse[None], summary="删除年费规则")
async def delete_annual_fee_rule(
    rule_id: UUID,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """删除年费规则"""
    success = service.delete_annual_fee_rule(rule_id)
    if not success:
        return ResponseUtil.not_found(message="年费规则不存在")
    return ResponseUtil.deleted(message="年费规则删除成功")


# ==================== 年费记录相关接口 ====================

@router.post("/records", response_model=ApiResponse[AnnualFeeRecord], summary="创建年费记录")
async def create_annual_fee_record(
    record_data: AnnualFeeRecordCreate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """创建年费记录"""
    try:
        record = service.create_annual_fee_record(record_data)
        return ResponseUtil.created(data=record, message="年费记录创建成功")
    except Exception as e:
        return ResponseUtil.error(message=f"创建年费记录失败: {str(e)}")


@router.post("/records/auto", response_model=ApiResponse[dict], summary="自动创建年费记录")
async def create_annual_fee_record_auto(
    card_id: UUID,
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """使用数据库函数自动创建年费记录"""
    try:
        record_id = service.create_annual_fee_record_auto(card_id, fee_year)
        return ResponseUtil.created(
            data={"record_id": record_id}, 
            message="年费记录自动创建成功"
        )
    except Exception as e:
        return ResponseUtil.error(message=f"自动创建年费记录失败: {str(e)}")


@router.get(
    "/records", 
    response_model=ApiPagedResponse[AnnualFeeRecord], 
    summary="获取年费记录列表",
    response_description="返回分页的年费记录列表"
)
async def get_annual_fee_records(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="模糊搜索关键词，支持卡片名称、银行名称搜索"),
    card_id: Optional[UUID] = Query(None, description="信用卡ID过滤"),
    fee_year: Optional[int] = Query(None, description="年费年份过滤"),
    waiver_status: Optional[WaiverStatus] = Query(None, description="减免状态过滤"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """
    获取年费记录列表
    
    获取年费记录信息，支持多种筛选条件和模糊搜索。
    可以按照信用卡、年份、减免状态等进行过滤。
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量，默认20，最大100
    - keyword: 搜索关键词，支持卡片名称、银行名称模糊匹配
    - card_id: 信用卡ID，筛选指定卡片的年费记录
    - fee_year: 年费年份，筛选指定年份的记录
    - waiver_status: 减免状态，可选值：pending、waived、paid、overdue
    """
    skip = ResponseUtil.calculate_skip(page, page_size)
    records, total = service.get_annual_fee_records(
        card_id=card_id,
        fee_year=fee_year,
        waiver_status=waiver_status,
        keyword=keyword,
        skip=skip,
        limit=page_size
    )
    return ResponseUtil.paginated(
        items=records, 
        total=total, 
        page=page, 
        page_size=page_size, 
        message="获取年费记录列表成功"
    )


@router.get("/records/{record_id}", response_model=ApiResponse[AnnualFeeRecord], summary="获取年费记录详情")
async def get_annual_fee_record(
    record_id: UUID,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """根据ID获取年费记录详情"""
    record = service.get_annual_fee_record(record_id)
    if not record:
        return ResponseUtil.not_found(message="年费记录不存在")
    return ResponseUtil.success(data=record, message="获取年费记录详情成功")


@router.put("/records/{record_id}", response_model=ApiResponse[AnnualFeeRecord], summary="更新年费记录")
async def update_annual_fee_record(
    record_id: UUID,
    record_data: AnnualFeeRecordUpdate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """更新年费记录"""
    record = service.update_annual_fee_record(record_id, record_data)
    if not record:
        return ResponseUtil.not_found(message="年费记录不存在")
    return ResponseUtil.success(data=record, message="年费记录更新成功")


# ==================== 年费减免检查接口 ====================

@router.get("/waiver-check/{card_id}/{fee_year}", response_model=ApiResponse[AnnualFeeWaiverCheck], summary="检查年费减免条件")
async def check_annual_fee_waiver(
    card_id: UUID,
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """检查指定信用卡的年费减免条件"""
    try:
        result = service.check_annual_fee_waiver(card_id, fee_year)
        return ResponseUtil.success(data=result, message="年费减免条件检查完成")
    except ValueError as e:
        return ResponseUtil.not_found(message=str(e))
    except Exception as e:
        return ResponseUtil.server_error(message=f"检查年费减免条件失败: {str(e)}")


@router.get("/waiver-check/user/{user_id}", response_model=ApiResponse[List[AnnualFeeWaiverCheck]], summary="检查用户所有卡的年费减免条件")
async def check_all_annual_fee_waivers(
    user_id: UUID,
    year: Optional[int] = Query(None, description="年份，默认为当前年份"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """检查用户所有信用卡的年费减免条件"""
    try:
        results = service.check_all_annual_fee_waivers(user_id, year)
        return ResponseUtil.success(data=results, message="用户所有卡片年费减免条件检查完成")
    except Exception as e:
        return ResponseUtil.server_error(message=f"检查用户年费减免条件失败: {str(e)}")


# ==================== 年费统计接口 ====================

@router.get("/statistics/{user_id}", response_model=ApiResponse[AnnualFeeStatistics], summary="获取年费统计信息")
async def get_annual_fee_statistics(
    user_id: UUID,
    year: Optional[int] = Query(None, description="年份，默认为当前年份"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """获取用户的年费统计信息"""
    try:
        statistics = service.get_annual_fee_statistics(user_id, year)
        return ResponseUtil.success(data=statistics, message="获取年费统计信息成功")
    except Exception as e:
        return ResponseUtil.server_error(message=f"获取年费统计信息失败: {str(e)}")


# ==================== 批量操作接口 ====================

@router.post("/batch/create-records", response_model=ApiResponse[dict], summary="批量创建年费记录")
async def batch_create_annual_fee_records(
    card_ids: List[UUID],
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """为多张信用卡批量创建年费记录"""
    try:
        results = []
        errors = []
        
        for card_id in card_ids:
            try:
                record_id = service.create_annual_fee_record_auto(card_id, fee_year)
                results.append({"card_id": card_id, "record_id": record_id})
            except Exception as e:
                errors.append({"card_id": card_id, "error": str(e)})
        
        batch_result = {
            "success_count": len(results),
            "error_count": len(errors),
            "results": results,
            "errors": errors
        }
        
        message = f"批量创建完成：成功{len(results)}个，失败{len(errors)}个"
        
        if len(errors) == 0:
            return ResponseUtil.success(data=batch_result, message=message)
        elif len(results) == 0:
            return ResponseUtil.error(message=message, data=batch_result)
        else:
            return ResponseUtil.success(data=batch_result, message=message)
    except Exception as e:
        return ResponseUtil.server_error(message=f"批量创建年费记录失败: {str(e)}")


@router.post("/batch/check-waivers", response_model=ApiResponse[List[AnnualFeeWaiverCheck]], summary="批量检查年费减免")
async def batch_check_annual_fee_waivers(
    card_ids: List[UUID],
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """批量检查多张信用卡的年费减免条件"""
    try:
        results = []
        error_count = 0
        
        for card_id in card_ids:
            try:
                waiver_check = service.check_annual_fee_waiver(card_id, fee_year)
                results.append(waiver_check)
            except Exception:
                # 跳过有错误的卡片
                error_count += 1
                continue
        
        message = f"批量检查完成：成功{len(results)}个"
        if error_count > 0:
            message += f"，跳过{error_count}个异常卡片"
            
        return ResponseUtil.success(data=results, message=message)
    except Exception as e:
        return ResponseUtil.server_error(message=f"批量检查年费减免失败: {str(e)}") 