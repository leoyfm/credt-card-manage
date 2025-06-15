"""
推荐模块API模型

包含推荐相关的请求和响应模型定义
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .common import PaginationInfo, PaginationParams


# ==================== 推荐规则相关模型 ====================

class RecommendationRuleBase(BaseModel):
    """推荐规则基础模型"""
    rule_name: str = Field(..., description="规则名称", max_length=100)
    rule_type: str = Field(..., description="规则类型", max_length=30)
    conditions: Dict[str, Any] = Field(..., description="规则条件")
    recommendation_title: Optional[str] = Field(None, description="推荐标题", max_length=200)
    recommendation_content: Optional[str] = Field(None, description="推荐内容")
    action_type: Optional[str] = Field(None, description="行动类型", max_length=30)
    priority: int = Field(1, description="优先级", ge=1, le=10)
    is_active: bool = Field(True, description="是否激活")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_name": "高额度低利用率推荐",
                "rule_type": "card_usage",
                "conditions": {
                    "credit_utilization": {"max": 0.3},
                    "credit_limit": {"min": 50000}
                },
                "recommendation_title": "您的信用卡利用率较低",
                "recommendation_content": "建议适当增加消费或申请更高额度的信用卡",
                "action_type": "card_switch",
                "priority": 5,
                "is_active": True
            }
        }
    )


class RecommendationRuleCreate(RecommendationRuleBase):
    """创建推荐规则请求模型"""
    pass


class RecommendationRuleUpdate(BaseModel):
    """更新推荐规则请求模型"""
    rule_name: Optional[str] = Field(None, description="规则名称", max_length=100)
    rule_type: Optional[str] = Field(None, description="规则类型", max_length=30)
    conditions: Optional[Dict[str, Any]] = Field(None, description="规则条件")
    recommendation_title: Optional[str] = Field(None, description="推荐标题", max_length=200)
    recommendation_content: Optional[str] = Field(None, description="推荐内容")
    action_type: Optional[str] = Field(None, description="行动类型", max_length=30)
    priority: Optional[int] = Field(None, description="优先级", ge=1, le=10)
    is_active: Optional[bool] = Field(None, description="是否激活")


class RecommendationRuleResponse(RecommendationRuleBase):
    """推荐规则响应模型"""
    id: UUID = Field(..., description="规则ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 推荐记录相关模型 ====================

class RecommendationRecordBase(BaseModel):
    """推荐记录基础模型"""
    recommendation_type: str = Field(..., description="推荐类型", max_length=30)
    title: str = Field(..., description="标题", max_length=200)
    content: str = Field(..., description="内容")
    action_data: Optional[Dict[str, Any]] = Field(None, description="行动数据")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommendation_type": "card_usage",
                "title": "信用卡使用优化建议",
                "content": "根据您的消费习惯，建议您使用招商银行信用卡进行日常消费",
                "action_data": {
                    "recommended_card_id": "uuid-string",
                    "reason": "该卡在您常用的消费类别有更高的积分倍率"
                }
            }
        }
    )


class RecommendationRecordCreate(RecommendationRecordBase):
    """创建推荐记录请求模型"""
    rule_id: Optional[UUID] = Field(None, description="规则ID")


class RecommendationRecordUpdate(BaseModel):
    """更新推荐记录请求模型"""
    user_action: Optional[str] = Field(None, description="用户行动", max_length=20)
    feedback: Optional[str] = Field(None, description="用户反馈")
    status: Optional[str] = Field(None, description="状态", max_length=20)


class RecommendationRecordResponse(RecommendationRecordBase):
    """推荐记录响应模型"""
    id: UUID = Field(..., description="记录ID")
    user_id: UUID = Field(..., description="用户ID")
    rule_id: Optional[UUID] = Field(None, description="规则ID")
    user_action: Optional[str] = Field(None, description="用户行动")
    feedback: Optional[str] = Field(None, description="用户反馈")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 推荐查询模型 ====================

class RecommendationQuery(PaginationParams):
    """推荐查询参数模型"""
    recommendation_type: Optional[str] = Field(None, description="推荐类型筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    user_action: Optional[str] = Field(None, description="用户行动筛选")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommendation_type": "card_usage",
                "status": "pending",
                "page": 1,
                "page_size": 20
            }
        }
    )


# ==================== 推荐反馈模型 ====================

class RecommendationFeedback(BaseModel):
    """推荐反馈模型"""
    user_action: str = Field(..., description="用户行动", max_length=20)
    feedback: Optional[str] = Field(None, description="用户反馈")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_action": "accepted",
                "feedback": "这个推荐很有用，我已经按照建议调整了信用卡使用策略"
            }
        }
    )


# ==================== 智能推荐请求模型 ====================

class SmartRecommendationRequest(BaseModel):
    """智能推荐请求模型"""
    recommendation_types: Optional[List[str]] = Field(None, description="推荐类型列表")
    limit: int = Field(5, description="推荐数量限制", ge=1, le=20)
    include_history: bool = Field(False, description="是否包含历史推荐")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommendation_types": ["card_usage", "fee_optimization"],
                "limit": 5,
                "include_history": False
            }
        }
    )


# ==================== 推荐统计模型 ====================

class RecommendationStats(BaseModel):
    """推荐统计模型"""
    total_recommendations: int = Field(..., description="总推荐数")
    pending_recommendations: int = Field(..., description="待处理推荐数")
    accepted_recommendations: int = Field(..., description="已接受推荐数")
    rejected_recommendations: int = Field(..., description="已拒绝推荐数")
    type_distribution: Dict[str, int] = Field(..., description="类型分布")
    recent_recommendations: List[RecommendationRecordResponse] = Field(..., description="最近推荐")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_recommendations": 25,
                "pending_recommendations": 3,
                "accepted_recommendations": 18,
                "rejected_recommendations": 4,
                "type_distribution": {
                    "card_usage": 10,
                    "fee_optimization": 8,
                    "category_analysis": 7
                },
                "recent_recommendations": []
            }
        }
    )


# ==================== 分页响应模型 ====================

class RecommendationRecordListResponse(BaseModel):
    """推荐记录列表响应模型"""
    items: List[RecommendationRecordResponse] = Field(..., description="推荐记录列表")
    pagination: PaginationInfo = Field(..., description="分页信息")

    model_config = ConfigDict(from_attributes=True)


class RecommendationRuleListResponse(BaseModel):
    """推荐规则列表响应模型"""
    items: List[RecommendationRuleResponse] = Field(..., description="推荐规则列表")
    pagination: PaginationInfo = Field(..., description="分页信息")

    model_config = ConfigDict(from_attributes=True) 