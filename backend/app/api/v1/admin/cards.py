"""
管理员信用卡管理 API
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, date

from app.api.dependencies.auth import get_current_admin_user
from app.api.dependencies.services import get_admin_card_service
from app.models.database.user import User
from app.models.schemas.admin import (
    AdminCardStatisticsResponse,
    AdminBankDistributionResponse,
    AdminCardHealthResponse,
    AdminCardTrendsResponse
)
from app.utils.response import ApiResponse
from app.services.admin_card_service import AdminCardService
from app.utils.response import ResponseUtil

router = APIRouter(prefix="/cards", tags=["管理员-信用卡管理"])


@router.get(
    "/statistics",
    response_model=ApiResponse,
    summary="获取信用卡系统统计",
    description="管理员获取系统级信用卡统计数据（脱敏）"
)
async def get_card_statistics(
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取信用卡系统统计（管理员权限）"""
    statistics = admin_service.get_card_statistics()
    
    return ResponseUtil.success(
        data=statistics,
        message="信用卡系统统计查询成功"
    )


@router.get(
    "/bank-distribution",
    response_model=ApiResponse,
    summary="获取银行分布统计",
    description="管理员获取各银行信用卡分布情况"
)
async def get_bank_distribution(
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取银行分布统计（管理员权限）"""
    distribution = admin_service.get_bank_distribution()
    
    return ResponseUtil.success(
        data=distribution,
        message="银行分布统计查询成功"
    )


@router.get(
    "/card-types",
    response_model=ApiResponse,
    summary="获取卡片类型分布",
    description="管理员获取信用卡类型、等级分布统计"
)
async def get_card_types_distribution(
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取卡片类型分布（管理员权限）"""
    types_distribution = admin_service.get_card_types_distribution()
    
    return ResponseUtil.success(
        data=types_distribution,
        message="卡片类型分布查询成功"
    )


@router.get(
    "/health-status",
    response_model=ApiResponse,
    summary="获取信用卡健康状况",
    description="管理员获取系统信用卡健康状况分析"
)
async def get_card_health_status(
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取信用卡健康状况（管理员权限）"""
    health_status = admin_service.get_card_health_status()
    
    return ResponseUtil.success(
        data=health_status,
        message="信用卡健康状况查询成功"
    )


@router.get(
    "/trends",
    response_model=ApiResponse,
    summary="获取信用卡趋势分析",
    description="管理员获取信用卡增长趋势和使用情况分析"
)
async def get_card_trends(
    months: int = Query(6, ge=1, le=24, description="分析月数，1-24个月"),
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取信用卡趋势分析（管理员权限）"""
    trends = admin_service.get_card_trends(months=months)
    
    return ResponseUtil.success(
        data=trends,
        message="信用卡趋势分析查询成功"
    )


@router.get(
    "/utilization-analysis",
    response_model=ApiResponse,
    summary="获取信用额度利用率分析",
    description="管理员获取系统信用额度利用率分布和风险分析"
)
async def get_utilization_analysis(
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取信用额度利用率分析（管理员权限）"""
    utilization_analysis = admin_service.get_utilization_analysis()
    
    return ResponseUtil.success(
        data=utilization_analysis,
        message="信用额度利用率分析查询成功"
    )


@router.get(
    "/expiry-alerts",
    response_model=ApiResponse,
    summary="获取即将到期卡片统计",
    description="管理员获取即将到期信用卡的统计信息"
)
async def get_expiry_alerts(
    months_ahead: int = Query(3, ge=1, le=12, description="提前月数，1-12个月"),
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取即将到期卡片统计（管理员权限）"""
    expiry_alerts = admin_service.get_expiry_alerts(months_ahead=months_ahead)
    
    return ResponseUtil.success(
        data=expiry_alerts,
        message="即将到期卡片统计查询成功"
    )


@router.get(
    "/annual-fee-summary",
    response_model=ApiResponse,
    summary="获取年费管理概览",
    description="管理员获取系统年费管理统计概览"
)
async def get_annual_fee_summary(
    year: Optional[int] = Query(None, description="指定年份，默认当前年份"),
    current_admin: User = Depends(get_current_admin_user),
    admin_service: AdminCardService = Depends(get_admin_card_service)
):
    """获取年费管理概览（管理员权限）"""
    if year is None:
        year = datetime.now().year
        
    fee_summary = admin_service.get_annual_fee_summary(year=year)
    
    return ResponseUtil.success(
        data=fee_summary,
        message=f"{year}年年费管理概览查询成功"
    ) 