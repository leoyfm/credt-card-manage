import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from models.response import ApiResponse, ApiPagedResponse
from models.recommendations import Recommendation
from models.users import UserProfile
from services.recommendations_service import RecommendationsService
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["智能推荐"])


def get_current_user_id(current_user: UserProfile = Depends(get_current_user)) -> UUID:
    """从当前用户信息中提取用户ID"""
    return current_user.id


def get_recommendations_service(db: Session = Depends(get_db)) -> RecommendationsService:
    """获取智能推荐服务实例"""
    return RecommendationsService(db)


@router.get(
    "/", 
    response_model=ApiPagedResponse[Recommendation],
    summary="获取信用卡推荐",
    response_description="返回分页的信用卡推荐数据"
)
async def get_recommendations(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="模糊搜索关键词，支持银行名称、卡片类型、推荐标题搜索"),
    user_id: UUID = Depends(get_current_user_id),
    service: RecommendationsService = Depends(get_recommendations_service)
):
    """
    获取信用卡推荐
    
    基于用户消费习惯和偏好，智能推荐最适合的信用卡产品。
    支持分页和模糊搜索功能。
    
    参数:
    - page: 页码，从1开始
    - page_size: 每页数量，默认20，最大100
    - keyword: 搜索关键词，支持银行名称、卡片类型、推荐标题模糊匹配
    
    返回:
    - 推荐列表，按推荐分数和精选状态排序
    """
    logger.info(f"获取信用卡推荐请求 - user_id: {user_id}, page: {page}, page_size: {page_size}, keyword: {keyword}")
    
    try:
        skip = (page - 1) * page_size
        recommendations, total = service.get_recommendations(
            user_id=user_id,
            skip=skip,
            limit=page_size,
            keyword=keyword
        )
        
        logger.info(f"获取信用卡推荐成功 - total: {total}")
        return ResponseUtil.paginated(
            items=recommendations,
            total=total,
            current_page=page,
            page_size=page_size,
            message="获取信用卡推荐成功"
        )
    except Exception as e:
        logger.error(f"获取信用卡推荐失败: {str(e)}")
        return ResponseUtil.server_error(message="获取信用卡推荐失败")


@router.get(
    "/{recommendation_id}",
    response_model=ApiResponse[Recommendation],
    summary="获取推荐详情",
    response_description="返回指定ID的推荐详细信息"
)
async def get_recommendation(
    recommendation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: RecommendationsService = Depends(get_recommendations_service)
):
    """
    根据ID获取推荐详情
    
    获取指定推荐的详细信息，包括推荐理由、卡片特色等。
    同时会更新推荐的查看次数和最后查看时间。
    
    参数:
    - recommendation_id: 推荐ID
    
    返回:
    - 推荐详细信息
    """
    logger.info(f"获取推荐详情请求 - user_id: {user_id}, recommendation_id: {recommendation_id}")
    
    try:
        recommendation = service.get_recommendation(recommendation_id, user_id)
        if not recommendation:
            logger.warning(f"推荐不存在 - recommendation_id: {recommendation_id}")
            return ResponseUtil.not_found(message="推荐不存在")
        
        logger.info("获取推荐详情成功")
        return ResponseUtil.success(
            data=recommendation,
            message="获取推荐详情成功"
        )
    except Exception as e:
        logger.error(f"获取推荐详情失败: {str(e)}")
        return ResponseUtil.server_error(message="获取推荐详情失败")


@router.post(
    "/generate",
    response_model=ApiResponse[List[Recommendation]],
    summary="生成个性化推荐",
    response_description="返回基于用户画像的推荐列表"
)
async def generate_recommendations(
    user_id: UUID = Depends(get_current_user_id),
    service: RecommendationsService = Depends(get_recommendations_service)
):
    """
    生成个性化推荐
    
    基于用户的消费记录、信用卡使用情况、偏好设置等生成个性化的信用卡推荐。
    
    推荐算法考虑因素:
    - 消费习惯和金额
    - 额度使用率
    - 年费承受能力
    - 免息期需求
    - 已有卡片情况
    
    返回:
    - 个性化推荐列表
    """
    logger.info(f"生成个性化推荐请求 - user_id: {user_id}")
    
    try:
        recommendations = service.generate_recommendations(user_id)
        
        logger.info(f"个性化推荐生成成功 - count: {len(recommendations)}")
        return ResponseUtil.success(
            data=recommendations,
            message=f"成功生成{len(recommendations)}条个性化推荐"
        )
    except Exception as e:
        logger.error(f"生成个性化推荐失败: {str(e)}")
        return ResponseUtil.server_error(message="生成个性化推荐失败")


@router.put(
    "/{recommendation_id}/feedback",
    response_model=ApiResponse[None],
    summary="提交推荐反馈",
    response_description="返回反馈提交结果"
)
async def submit_recommendation_feedback(
    recommendation_id: UUID,
    feedback: str = Query(
        ..., 
        description="用户反馈类型，如：interested（感兴趣）、not_interested（不感兴趣）、applied（已申请）、too_expensive（太贵）",
        json_schema_extra={"example": "interested"}
    ),
    user_id: UUID = Depends(get_current_user_id),
    service: RecommendationsService = Depends(get_recommendations_service)
):
    """
    提交推荐反馈
    
    用户对推荐结果进行反馈，用于优化推荐算法。
    根据反馈类型会自动更新推荐状态。
    
    参数:
    - recommendation_id: 推荐ID
    - feedback: 反馈类型
      - interested: 感兴趣
      - not_interested: 不感兴趣
      - applied: 已申请此卡
      - too_expensive: 年费太高
      - already_have: 已持有类似卡片
      - not_eligible: 不符合申请条件
    
    返回:
    - 反馈提交结果
    """
    logger.info(f"提交推荐反馈请求 - user_id: {user_id}, recommendation_id: {recommendation_id}, feedback: {feedback}")
    
    try:
        success = service.submit_feedback(recommendation_id, user_id, feedback)
        if not success:
            logger.warning(f"推荐不存在 - recommendation_id: {recommendation_id}")
            return ResponseUtil.not_found(message="推荐不存在")
        
        logger.info("推荐反馈提交成功")
        return ResponseUtil.success(message="推荐反馈提交成功")
    except Exception as e:
        logger.error(f"提交推荐反馈失败: {str(e)}")
        return ResponseUtil.server_error(message="提交推荐反馈失败")


@router.get(
    "/stats/user-profile",
    response_model=ApiResponse[dict],
    summary="获取用户画像分析",
    response_description="返回用户消费习惯和偏好分析结果"
)
async def get_user_profile_stats(
    user_id: UUID = Depends(get_current_user_id),
    service: RecommendationsService = Depends(get_recommendations_service)
):
    """
    获取用户画像分析
    
    分析用户的消费习惯、信用卡使用情况等，返回画像数据。
    这些数据是推荐算法的基础。
    
    返回:
    - 用户画像统计数据
    """
    logger.info(f"获取用户画像分析请求 - user_id: {user_id}")
    
    try:
        # 调用私有方法分析用户画像
        user_profile = service._analyze_user_profile(user_id)
        
        logger.info("获取用户画像分析成功")
        return ResponseUtil.success(
            data=user_profile,
            message="获取用户画像分析成功"
        )
    except Exception as e:
        logger.error(f"获取用户画像分析失败: {str(e)}")
        return ResponseUtil.server_error(message="获取用户画像分析失败") 