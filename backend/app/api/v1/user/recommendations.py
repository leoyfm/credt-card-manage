"""
用户推荐API路由

提供用户推荐相关的API接口，包括智能推荐、推荐历史、反馈等功能
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.database import get_db
from app.models.database.user import User
from app.core.exceptions import (
    ResourceNotFoundError, DatabaseError, BusinessRuleError
)
from app.models.schemas.recommendation import (
    RecommendationRecordResponse, RecommendationRecordListResponse,
    RecommendationQuery, RecommendationFeedback, SmartRecommendationRequest,
    RecommendationStats, RecommendationRecordUpdate
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse, PaginationInfo
from app.services.recommendation_service import RecommendationService
from app.utils.response import ResponseUtil

router = APIRouter(prefix="/recommendations", tags=["用户推荐"])


@router.get(
    "/smart",
    response_model=ApiResponse[List[RecommendationRecordResponse]],
    summary="获取智能推荐",
    description="基于用户数据生成个性化推荐"
)
async def get_smart_recommendations(
    recommendation_types: Optional[List[str]] = Query(None, description="推荐类型列表"),
    limit: int = Query(5, ge=1, le=20, description="推荐数量限制"),
    include_history: bool = Query(False, description="是否包含历史推荐"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取智能推荐
    
    根据用户的信用卡使用情况、交易记录等数据，生成个性化推荐：
    - card_usage: 信用卡使用优化建议
    - fee_optimization: 年费减免建议
    - category_analysis: 消费分类分析建议
    """
    try:
        service = RecommendationService(db)
        
        request = SmartRecommendationRequest(
            recommendation_types=recommendation_types,
            limit=limit,
            include_history=include_history
        )
        
        recommendations = service.generate_smart_recommendations(current_user.id, request)
        
        return ResponseUtil.success(
            data=recommendations,
            message=f"成功生成{len(recommendations)}条推荐"
        )
        
    except Exception as e:
        raise DatabaseError(
            message="生成推荐失败",
            error_detail=str(e)
        )


@router.get(
    "/history",
    response_model=ApiPagedResponse[RecommendationRecordResponse],
    summary="获取推荐历史",
    description="获取用户的推荐历史记录，支持筛选和分页"
)
async def get_recommendation_history(
    recommendation_type: Optional[str] = Query(None, description="推荐类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    user_action: Optional[str] = Query(None, description="用户行动筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取推荐历史
    
    支持的筛选条件：
    - recommendation_type: card_usage, fee_optimization, category_analysis
    - status: pending, read, acted
    - user_action: viewed, accepted, rejected, ignored
    """
    try:
        service = RecommendationService(db)
        
        query_params = RecommendationQuery(
            recommendation_type=recommendation_type,
            status=status,
            user_action=user_action,
            page=page,
            page_size=page_size
        )
        
        recommendations, total = service.get_user_recommendations(current_user.id, query_params)
        
        return ResponseUtil.paginated(
            items=recommendations,
            total=total,
            page=page,
            page_size=page_size,
            message=f"查询到{len(recommendations)}条推荐记录"
        )
        
    except Exception as e:
        raise DatabaseError(
            message="查询推荐历史失败",
            error_detail=str(e)
        )


@router.get(
    "/{recommendation_id}",
    response_model=ApiResponse[RecommendationRecordResponse],
    summary="获取推荐详情",
    description="获取指定推荐的详细信息"
)
async def get_recommendation_detail(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取推荐详情"""
    try:
        service = RecommendationService(db)
        
        recommendation = service.get_recommendation_by_id(recommendation_id, current_user.id)
        if not recommendation:
            raise ResourceNotFoundError(
                message="推荐记录不存在",
                error_detail=f"推荐ID: {recommendation_id}"
            )
        
        # 标记为已读
        service.mark_recommendation_as_read(recommendation_id, current_user.id)
        
        return ResponseUtil.success(
            data=recommendation,
            message="获取推荐详情成功"
        )
        
    except (ResourceNotFoundError, BusinessRuleError):
        raise
    except Exception as e:
        raise DatabaseError(
            message="获取推荐详情失败",
            error_detail=str(e)
        )


@router.post(
    "/{recommendation_id}/feedback",
    response_model=ApiResponse[RecommendationRecordResponse],
    summary="提交推荐反馈",
    description="对推荐提交用户反馈和行动"
)
async def submit_recommendation_feedback(
    recommendation_id: UUID,
    feedback: RecommendationFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交推荐反馈
    
    用户行动类型：
    - viewed: 已查看
    - accepted: 已接受
    - rejected: 已拒绝
    - ignored: 已忽略
    """
    try:
        service = RecommendationService(db)
        
        recommendation = service.submit_feedback(recommendation_id, current_user.id, feedback)
        if not recommendation:
            raise ResourceNotFoundError(
                message="推荐记录不存在",
                error_detail=f"推荐ID: {recommendation_id}"
            )
        
        return ResponseUtil.success(
            data=recommendation,
            message="反馈提交成功"
        )
        
    except (ResourceNotFoundError, BusinessRuleError):
        raise
    except Exception as e:
        raise DatabaseError(
            message="提交反馈失败",
            error_detail=str(e)
        )


@router.put(
    "/{recommendation_id}",
    response_model=ApiResponse[RecommendationRecordResponse],
    summary="更新推荐记录",
    description="更新推荐记录的状态或用户行动"
)
async def update_recommendation(
    recommendation_id: UUID,
    update_data: RecommendationRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新推荐记录"""
    try:
        service = RecommendationService(db)
        
        recommendation = service.update_recommendation(
            recommendation_id, current_user.id, update_data
        )
        if not recommendation:
            raise ResourceNotFoundError(
                message="推荐记录不存在",
                error_detail=f"推荐ID: {recommendation_id}"
            )
        
        return ResponseUtil.success(
            data=recommendation,
            message="推荐记录更新成功"
        )
        
    except (ResourceNotFoundError, BusinessRuleError):
        raise
    except Exception as e:
        raise DatabaseError(
            message="更新推荐记录失败",
            error_detail=str(e)
        )


@router.get(
    "/stats/overview",
    response_model=ApiResponse[RecommendationStats],
    summary="获取推荐统计",
    description="获取用户推荐的统计信息"
)
async def get_recommendation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取推荐统计
    
    包括：
    - 总推荐数
    - 各类型推荐数量
    - 用户行动统计
    - 接受率等指标
    """
    try:
        service = RecommendationService(db)
        
        stats = service.get_recommendation_stats(current_user.id)
        
        return ResponseUtil.success(
            data=stats,
            message="获取推荐统计成功"
        )
        
    except Exception as e:
        raise DatabaseError(
            message="获取推荐统计失败",
            error_detail=str(e)
        )


@router.post(
    "/evaluate-rules",
    response_model=ApiResponse[List[RecommendationRecordResponse]],
    summary="评估推荐规则",
    description="基于系统规则为用户生成推荐"
)
async def evaluate_recommendation_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    评估推荐规则
    
    基于系统配置的推荐规则，为当前用户生成推荐记录
    """
    try:
        service = RecommendationService(db)
        
        recommendations = service.evaluate_rules_for_user(current_user.id)
        
        return ResponseUtil.success(
            data=recommendations,
            message=f"基于规则生成{len(recommendations)}条推荐"
        )
        
    except Exception as e:
        raise DatabaseError(
            message="评估推荐规则失败",
            error_detail=str(e)
        )


@router.get(
    "/types/available",
    response_model=ApiResponse[List[str]],
    summary="获取可用推荐类型",
    description="获取系统支持的推荐类型列表"
)
async def get_available_recommendation_types():
    """
    获取可用推荐类型
    
    返回系统支持的所有推荐类型
    """
    available_types = [
        "card_usage",
        "fee_optimization", 
        "category_analysis",
        "limit_management",
        "payment_reminder",
        "points_optimization"
    ]
    
    return ResponseUtil.success(
        data=available_types,
        message="获取推荐类型成功"
    )


@router.get(
    "/actions/available",
    response_model=ApiResponse[List[str]],
    summary="获取可用用户行动",
    description="获取用户可以对推荐执行的行动类型"
)
async def get_available_user_actions():
    """
    获取可用用户行动
    
    返回用户可以对推荐执行的所有行动类型
    """
    available_actions = [
        "viewed",
        "accepted", 
        "rejected",
        "ignored"
    ]
    
    return ResponseUtil.success(
        data=available_actions,
        message="获取用户行动类型成功"
    ) 