from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class RecommendationType(str, Enum):
    """
    推荐类型枚举
    
    定义不同的推荐类型：
    - CASHBACK: 现金回馈类信用卡推荐
    - POINTS: 积分奖励类信用卡推荐
    - TRAVEL: 旅行消费类信用卡推荐
    - DINING: 餐饮消费类信用卡推荐
    - SHOPPING: 购物消费类信用卡推荐
    - FUEL: 加油消费类信用卡推荐
    """
    CASHBACK = "cashback"    # 现金回馈
    POINTS = "points"        # 积分奖励
    TRAVEL = "travel"        # 旅行消费
    DINING = "dining"        # 餐饮消费
    SHOPPING = "shopping"    # 购物消费
    FUEL = "fuel"           # 加油消费


class RecommendationStatus(str, Enum):
    """
    推荐状态枚举
    
    定义推荐的状态：
    - ACTIVE: 活跃推荐，当前有效的推荐
    - EXPIRED: 已过期，推荐已失效
    - APPLIED: 已申请，用户已申请此卡
    - REJECTED: 已拒绝，用户拒绝此推荐
    """
    ACTIVE = "active"        # 活跃推荐
    EXPIRED = "expired"      # 已过期
    APPLIED = "applied"      # 已申请
    REJECTED = "rejected"    # 已拒绝


class RecommendationBase(BaseModel):
    """
    智能推荐基础模型
    
    定义智能推荐的基础字段，包括推荐类型、内容、评分等。
    """
    bank_name: str = Field(
        ..., 
        min_length=2, 
        max_length=50,
        description="银行名称",
        json_schema_extra={"example": "招商银行"}
    )
    
    card_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="信用卡名称",
        json_schema_extra={"example": "招商银行经典白金卡"}
    )
    
    recommendation_type: RecommendationType = Field(
        ...,
        description="推荐类型",
        json_schema_extra={"example": RecommendationType.CASHBACK}
    )
    
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="推荐标题",
        json_schema_extra={"example": "高现金回馈信用卡推荐"}
    )
    
    description: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="推荐描述",
        json_schema_extra={"example": "基于您的消费习惯，这张卡在餐饮和超市消费有高额回馈"}
    )
    
    features: List[str] = Field(
        [],
        description="卡片特色功能列表",
        json_schema_extra={"example": ["餐饮5%回馈", "超市3%回馈", "免年费政策"]}
    )
    
    annual_fee: Decimal = Field(
        0, 
        ge=0, 
        le=99999.99,
        description="年费金额，单位：元",
        json_schema_extra={"example": 200.00}
    )
    
    credit_limit_range: str = Field(
        ...,
        max_length=50,
        description="额度范围",
        json_schema_extra={"example": "5万-50万"}
    )
    
    approval_difficulty: int = Field(
        ..., 
        ge=1, 
        le=5,
        description="申请难度等级，1-5分",
        json_schema_extra={"example": 3}
    )
    
    recommendation_score: Decimal = Field(
        ..., 
        ge=0, 
        le=100,
        description="推荐分数，0-100分",
        json_schema_extra={"example": 85.5}
    )
    
    match_reasons: List[str] = Field(
        [],
        description="匹配原因列表",
        json_schema_extra={"example": ["消费类型匹配", "收入水平适合", "优惠活动丰富"]}
    )
    
    pros: List[str] = Field(
        [],
        description="优点列表",
        json_schema_extra={"example": ["回馈率高", "优惠活动多", "服务质量好"]}
    )
    
    cons: List[str] = Field(
        [],
        description="缺点列表",
        json_schema_extra={"example": ["年费较高", "申请门槛高"]}
    )
    
    apply_url: Optional[str] = Field(
        None,
        max_length=500,
        description="申请链接",
        json_schema_extra={"example": "https://bank.example.com/apply/card123"}
    )
    
    status: RecommendationStatus = Field(
        RecommendationStatus.ACTIVE,
        description="推荐状态",
        json_schema_extra={"example": RecommendationStatus.ACTIVE}
    )
    
    expires_at: Optional[datetime] = Field(
        None,
        description="推荐过期时间",
        json_schema_extra={"example": "2024-12-31T23:59:59"}
    )
    
    is_featured: bool = Field(
        False,
        description="是否为精选推荐",
        json_schema_extra={"example": False}
    )


class RecommendationCreate(RecommendationBase):
    """
    创建推荐请求模型
    
    用于接收创建新推荐的请求数据。
    """
    user_id: UUID = Field(
        ..., 
        description="用户ID，推荐的目标用户",
        json_schema_extra={"example": "12345678-1234-1234-1234-123456789012"}
    )


class RecommendationUpdate(BaseModel):
    """
    更新推荐请求模型
    
    用于接收更新推荐的请求数据，所有字段均为可选。
    """
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="推荐标题",
        json_schema_extra={"example": "超值积分奖励信用卡推荐"}
    )
    description: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=1000, 
        description="推荐描述",
        json_schema_extra={"example": "基于您的积分偏好，这张卡在多个类别有丰厚积分奖励"}
    )
    features: Optional[List[str]] = Field(
        None, 
        description="卡片特色功能列表",
        json_schema_extra={"example": ["超市10倍积分", "加油5倍积分", "生日月双倍积分"]}
    )
    annual_fee: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=99999.99, 
        description="年费金额",
        json_schema_extra={"example": 300.00}
    )
    credit_limit_range: Optional[str] = Field(
        None, 
        max_length=50, 
        description="额度范围",
        json_schema_extra={"example": "3万-30万"}
    )
    approval_difficulty: Optional[int] = Field(
        None, 
        ge=1, 
        le=5, 
        description="申请难度等级",
        json_schema_extra={"example": 2}
    )
    recommendation_score: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=100, 
        description="推荐分数",
        json_schema_extra={"example": 92.0}
    )
    match_reasons: Optional[List[str]] = Field(
        None, 
        description="匹配原因列表",
        json_schema_extra={"example": ["积分需求匹配", "消费类型符合", "优惠活动丰富"]}
    )
    pros: Optional[List[str]] = Field(
        None, 
        description="优点列表",
        json_schema_extra={"example": ["积分奖励丰厚", "兑换选择多样", "有效期较长"]}
    )
    cons: Optional[List[str]] = Field(
        None, 
        description="缺点列表",
        json_schema_extra={"example": ["年费稍高", "积分有效期限制"]}
    )
    apply_url: Optional[str] = Field(
        None, 
        max_length=500, 
        description="申请链接",
        json_schema_extra={"example": "https://bank.example.com/apply/points-card"}
    )
    status: Optional[RecommendationStatus] = Field(
        None, 
        description="推荐状态",
        json_schema_extra={"example": RecommendationStatus.ACTIVE}
    )
    expires_at: Optional[datetime] = Field(
        None, 
        description="推荐过期时间",
        json_schema_extra={"example": "2024-06-30T23:59:59"}
    )
    is_featured: Optional[bool] = Field(
        None, 
        description="是否为精选推荐",
        json_schema_extra={"example": True}
    )


class Recommendation(RecommendationBase):
    """
    推荐响应模型
    
    用于返回推荐数据，包含完整的推荐信息和系统生成的字段。
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="推荐ID，系统自动生成的唯一标识")
    user_id: UUID = Field(..., description="用户ID，推荐的目标用户")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    view_count: int = Field(0, description="查看次数")
    last_viewed_at: Optional[datetime] = Field(None, description="最后查看时间")

    @field_serializer('created_at', 'updated_at', 'last_viewed_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return value.isoformat() if value is not None else None

    @field_serializer('annual_fee', 'recommendation_score')
    def serialize_decimal(self, value: Decimal) -> float:
        """序列化Decimal为float"""
        return float(value)


class RecommendationFeedback(BaseModel):
    """
    推荐反馈模型
    
    用于收集用户对推荐的反馈信息。
    """
    model_config = ConfigDict(from_attributes=True)
    
    recommendation_id: UUID = Field(
        ..., 
        description="推荐ID",
        json_schema_extra={"example": "87654321-4321-4321-4321-210987654321"}
    )
    feedback_type: str = Field(
        ...,
        description="反馈类型，如：interested、not_interested、applied、too_expensive",
        json_schema_extra={"example": "interested"}
    )
    rating: Optional[int] = Field(
        None, 
        ge=1, 
        le=5,
        description="用户评分，1-5分",
        json_schema_extra={"example": 4}
    )
    comment: Optional[str] = Field(
        None,
        max_length=500,
        description="用户评论",
        json_schema_extra={"example": "这张卡的回馈率确实不错，考虑申请"}
    ) 