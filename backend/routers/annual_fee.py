from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
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

router = APIRouter(prefix="/annual-fees", tags=["年费管理"])


def get_annual_fee_service(db: Session = Depends(get_db)) -> AnnualFeeService:
    """获取年费服务实例"""
    return AnnualFeeService(db)


# ==================== 年费规则相关接口 ====================

@router.post("/rules", response_model=AnnualFeeRule, summary="创建年费规则")
async def create_annual_fee_rule(
    rule_data: AnnualFeeRuleCreate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """创建新的年费规则"""
    try:
        return service.create_annual_fee_rule(rule_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rules", response_model=List[AnnualFeeRule], summary="获取年费规则列表")
async def get_annual_fee_rules(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    fee_type: Optional[FeeType] = Query(None, description="按年费类型筛选"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """获取年费规则列表"""
    return service.get_annual_fee_rules(skip=skip, limit=limit, fee_type=fee_type)


@router.get("/rules/{rule_id}", response_model=AnnualFeeRule, summary="获取年费规则详情")
async def get_annual_fee_rule(
    rule_id: UUID,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """根据ID获取年费规则详情"""
    rule = service.get_annual_fee_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="年费规则不存在")
    return rule


@router.put("/rules/{rule_id}", response_model=AnnualFeeRule, summary="更新年费规则")
async def update_annual_fee_rule(
    rule_id: UUID,
    rule_data: AnnualFeeRuleUpdate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """更新年费规则"""
    rule = service.update_annual_fee_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="年费规则不存在")
    return rule


@router.delete("/rules/{rule_id}", summary="删除年费规则")
async def delete_annual_fee_rule(
    rule_id: UUID,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """删除年费规则"""
    success = service.delete_annual_fee_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="年费规则不存在")
    return {"message": "年费规则删除成功"}


# ==================== 年费记录相关接口 ====================

@router.post("/records", response_model=AnnualFeeRecord, summary="创建年费记录")
async def create_annual_fee_record(
    record_data: AnnualFeeRecordCreate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """创建年费记录"""
    try:
        return service.create_annual_fee_record(record_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/auto", summary="自动创建年费记录")
async def create_annual_fee_record_auto(
    card_id: UUID,
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """使用数据库函数自动创建年费记录"""
    try:
        record_id = service.create_annual_fee_record_auto(card_id, fee_year)
        return {"record_id": record_id, "message": "年费记录创建成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/records", response_model=List[AnnualFeeRecord], summary="获取年费记录列表")
async def get_annual_fee_records(
    card_id: Optional[UUID] = Query(None, description="信用卡ID"),
    fee_year: Optional[int] = Query(None, description="年费年份"),
    waiver_status: Optional[WaiverStatus] = Query(None, description="减免状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """获取年费记录列表"""
    return service.get_annual_fee_records(
        card_id=card_id,
        fee_year=fee_year,
        waiver_status=waiver_status,
        skip=skip,
        limit=limit
    )


@router.get("/records/{record_id}", response_model=AnnualFeeRecord, summary="获取年费记录详情")
async def get_annual_fee_record(
    record_id: UUID,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """根据ID获取年费记录详情"""
    record = service.get_annual_fee_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="年费记录不存在")
    return record


@router.put("/records/{record_id}", response_model=AnnualFeeRecord, summary="更新年费记录")
async def update_annual_fee_record(
    record_id: UUID,
    record_data: AnnualFeeRecordUpdate,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """更新年费记录"""
    record = service.update_annual_fee_record(record_id, record_data)
    if not record:
        raise HTTPException(status_code=404, detail="年费记录不存在")
    return record


# ==================== 年费减免检查接口 ====================

@router.get("/waiver-check/{card_id}/{fee_year}", response_model=AnnualFeeWaiverCheck, summary="检查年费减免条件")
async def check_annual_fee_waiver(
    card_id: UUID,
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """检查指定信用卡的年费减免条件"""
    try:
        return service.check_annual_fee_waiver(card_id, fee_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/waiver-check/user/{user_id}", response_model=List[AnnualFeeWaiverCheck], summary="检查用户所有卡的年费减免条件")
async def check_all_annual_fee_waivers(
    user_id: UUID,
    year: Optional[int] = Query(None, description="年份，默认为当前年份"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """检查用户所有信用卡的年费减免条件"""
    try:
        return service.check_all_annual_fee_waivers(user_id, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 年费统计接口 ====================

@router.get("/statistics/{user_id}", response_model=AnnualFeeStatistics, summary="获取年费统计信息")
async def get_annual_fee_statistics(
    user_id: UUID,
    year: Optional[int] = Query(None, description="年份，默认为当前年份"),
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """获取用户的年费统计信息"""
    try:
        return service.get_annual_fee_statistics(user_id, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 批量操作接口 ====================

@router.post("/batch/create-records", summary="批量创建年费记录")
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
        
        return {
            "success_count": len(results),
            "error_count": len(errors),
            "results": results,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/check-waivers", response_model=List[AnnualFeeWaiverCheck], summary="批量检查年费减免")
async def batch_check_annual_fee_waivers(
    card_ids: List[UUID],
    fee_year: int,
    service: AnnualFeeService = Depends(get_annual_fee_service)
):
    """批量检查多张信用卡的年费减免条件"""
    try:
        results = []
        
        for card_id in card_ids:
            try:
                waiver_check = service.check_annual_fee_waiver(card_id, fee_year)
                results.append(waiver_check)
            except Exception:
                # 跳过有错误的卡片
                continue
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 