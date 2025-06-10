"""
智能推荐管理 Pydantic 模型

本模块定义了智能推荐系统的所有数据模型，包括：
- 推荐规则模型 (RecommendationRule)
- 推荐结果模型 (RecommendationResult)
- 用户反馈模型 (UserFeedback)
- 学习模型配置 (MLModelConfig)
- 请求响应模型
- 查询过滤模型
- 统计分析模型
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator
from .common import BaseResponse, BasePaginatedResponse, BaseQueryParams


# ================================
# 枚举定义
# ================================

class RecommendationType(str, Enum):
    """推荐类型"""
    CARD_SELECTION = "card_selection"         # 信用卡选择推荐
    SPENDING_OPTIMIZATION = "spending_optimization"  # 支出优化推荐
    CASHBACK_MAXIMIZATION = "cashback_maximization"  # 返现最大化
    POINTS_EARNING = "points_earning"         # 积分获取推荐
    ANNUAL_FEE_OPTIMIZATION = "annual_fee_optimization"  # 年费优化
    PAYMENT_STRATEGY = "payment_strategy"     # 还款策略推荐
    BUDGET_ADJUSTMENT = "budget_adjustment"   # 预算调整建议
    PROMOTIONAL_OFFERS = "promotional_offers" # 优惠活动推荐
    RISK_MANAGEMENT = "risk_management"       # 风险管理建议


class RecommendationPriority(str, Enum):
    """推荐优先级"""
    CRITICAL = "critical"     # 紧急重要
    HIGH = "high"            # 高优先级
    MEDIUM = "medium"        # 中等优先级
    LOW = "low"              # 低优先级
    INFO = "info"            # 信息提示


class RecommendationStatus(str, Enum):
    """推荐状态"""
    ACTIVE = "active"        # 激活
    ACCEPTED = "accepted"    # 已接受
    REJECTED = "rejected"    # 已拒绝
    IGNORED = "ignored"      # 已忽略
    EXPIRED = "expired"      # 已过期
    ARCHIVED = "archived"    # 已归档


class FeedbackType(str, Enum):
    """反馈类型"""
    LIKE = "like"           # 喜欢
    DISLIKE = "dislike"     # 不喜欢
    USEFUL = "useful"       # 有用
    NOT_USEFUL = "not_useful"  # 无用
    IRRELEVANT = "irrelevant"  # 不相关
    INCORRECT = "incorrect"  # 错误信息


class MLModelType(str, Enum):
    """机器学习模型类型"""
    COLLABORATIVE_FILTERING = "collaborative_filtering"  # 协同过滤
    CONTENT_BASED = "content_based"                      # 基于内容
    MATRIX_FACTORIZATION = "matrix_factorization"       # 矩阵分解
    DEEP_LEARNING = "deep_learning"                      # 深度学习
    ENSEMBLE = "ensemble"                                # 集成学习
    RULE_BASED = "rule_based"                           # 基于规则


class ContextType(str, Enum):
    """上下文类型"""
    SPENDING_PATTERN = "spending_pattern"    # 支出模式
    SEASONAL = "seasonal"                    # 季节性
    LOCATION_BASED = "location_based"        # 基于位置
    TIME_BASED = "time_based"               # 基于时间
    BEHAVIORAL = "behavioral"               # 行为模式
    DEMOGRAPHIC = "demographic"             # 人口统计


# ================================
# 基础数据模型
# ================================

class RecommendationContext(BaseModel):
    """推荐上下文模型"""
    context_type: ContextType = Field(..., description="上下文类型")
    context_data: Dict[str, Any] = Field({}, description="上下文数据")
    weight: float = Field(1.0, ge=0, le=1, description="权重，0-1之间")
    
    class Config:
        schema_extra = {
            "example": {
                "context_type": "spending_pattern",
                "context_data": {
                    "category": "dining",
                    "frequency": "high",
                    "average_amount": 150.0
                },
                "weight": 0.8
            }
        }


class RecommendationAction(BaseModel):
    """推荐操作模型"""
    action_type: str = Field(..., description="操作类型")
    action_params: Dict[str, Any] = Field({}, description="操作参数")
    expected_benefit: Optional[str] = Field(None, description="预期收益")
    difficulty_level: str = Field("medium", description="执行难度：easy/medium/hard")
    
    class Config:
        schema_extra = {
            "example": {
                "action_type": "switch_card",
                "action_params": {
                    "from_card": "card_id_1",
                    "to_card": "card_id_2",
                    "category": "dining"
                },
                "expected_benefit": "每月可多获得50元返现",
                "difficulty_level": "easy"
            }
        }


# ================================
# 推荐规则相关模型
# ================================

class RecommendationRuleBase(BaseModel):
    """推荐规则基础模型"""
    rule_name: str = Field(..., max_length=200, description="规则名称")
    rule_description: str = Field(..., max_length=1000, description="规则描述")
    recommendation_type: RecommendationType = Field(..., description="推荐类型")
    
    # 触发条件
    trigger_conditions: Dict[str, Any] = Field({}, description="触发条件")
    min_confidence: float = Field(0.7, ge=0, le=1, description="最小置信度")
    
    # 规则配置
    is_ml_based: bool = Field(False, description="是否基于机器学习")
    ml_model_type: Optional[MLModelType] = Field(None, description="机器学习模型类型")
    priority: RecommendationPriority = Field(RecommendationPriority.MEDIUM, description="优先级")
    
    # 有效性设置
    is_active: bool = Field(True, description="是否激活")
    valid_from: Optional[datetime] = Field(None, description="有效期开始")
    valid_to: Optional[datetime] = Field(None, description="有效期结束")
    
    # 频率限制
    max_daily_recommendations: int = Field(3, ge=1, le=10, description="每日最大推荐数")
    cooldown_hours: int = Field(24, ge=1, description="冷却时间（小时）")
    
    @validator('valid_to')
    def validate_validity_period(cls, v, values):
        """验证有效期"""
        valid_from = values.get('valid_from')
        if valid_from and v and v <= valid_from:
            raise ValueError("有效期结束时间必须晚于开始时间")
        return v
    
    @root_validator
    def validate_ml_config(cls, values):
        """验证机器学习配置"""
        is_ml_based = values.get('is_ml_based', False)
        ml_model_type = values.get('ml_model_type')
        
        if is_ml_based and not ml_model_type:
            raise ValueError("基于机器学习的规则必须指定模型类型")
        if not is_ml_based and ml_model_type:
            raise ValueError("非机器学习规则不应指定模型类型")
            
        return values


class RecommendationRuleCreate(RecommendationRuleBase):
    """创建推荐规则请求模型"""
    target_user_segments: Optional[List[str]] = Field(None, description="目标用户群体")
    test_mode: bool = Field(False, description="测试模式")
    
    class Config:
        schema_extra = {
            "example": {
                "rule_name": "餐饮消费优化推荐",
                "rule_description": "基于用户餐饮消费模式推荐最优信用卡",
                "recommendation_type": "card_selection",
                "trigger_conditions": {
                    "min_monthly_dining_spend": 1000,
                    "dining_frequency": ">=5"
                },
                "min_confidence": 0.8,
                "is_ml_based": True,
                "ml_model_type": "collaborative_filtering",
                "priority": "high",
                "max_daily_recommendations": 2,
                "cooldown_hours": 48,
                "is_active": True
            }
        }


class RecommendationRuleUpdate(BaseModel):
    """更新推荐规则请求模型"""
    rule_name: Optional[str] = Field(None, max_length=200, description="规则名称")
    rule_description: Optional[str] = Field(None, max_length=1000, description="规则描述")
    trigger_conditions: Optional[Dict[str, Any]] = Field(None, description="触发条件")
    min_confidence: Optional[float] = Field(None, ge=0, le=1, description="最小置信度")
    
    priority: Optional[RecommendationPriority] = Field(None, description="优先级")
    is_active: Optional[bool] = Field(None, description="是否激活")
    max_daily_recommendations: Optional[int] = Field(None, ge=1, le=10, description="每日最大推荐数")
    cooldown_hours: Optional[int] = Field(None, ge=1, description="冷却时间")
    
    class Config:
        schema_extra = {
            "example": {
                "min_confidence": 0.85,
                "priority": "high",
                "max_daily_recommendations": 3,
                "is_active": True
            }
        }


class RecommendationRuleResponse(RecommendationRuleBase):
    """推荐规则响应模型"""
    id: UUID = Field(..., description="规则ID")
    user_id: UUID = Field(..., description="创建用户ID")
    
    # 统计信息
    total_triggered: int = Field(0, description="总触发次数")
    total_accepted: int = Field(0, description="总接受次数")
    acceptance_rate: float = Field(0.0, description="接受率")
    avg_feedback_score: Optional[float] = Field(None, description="平均反馈评分")
    
    # 模型性能
    model_accuracy: Optional[float] = Field(None, description="模型准确率")
    last_trained_at: Optional[datetime] = Field(None, description="最后训练时间")
    
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "rule-uuid-here",
                "user_id": "user-uuid-here",
                "rule_name": "餐饮消费优化推荐",
                "recommendation_type": "card_selection",
                "priority": "high",
                "total_triggered": 150,
                "total_accepted": 95,
                "acceptance_rate": 63.3,
                "avg_feedback_score": 4.2,
                "model_accuracy": 0.85,
                "is_active": True,
                "created_at": "2024-12-01T10:00:00Z",
                "updated_at": "2024-12-01T10:00:00Z"
            }
        }


# ================================
# 推荐结果相关模型
# ================================

class RecommendationResultBase(BaseModel):
    """推荐结果基础模型"""
    title: str = Field(..., max_length=200, description="推荐标题")
    description: str = Field(..., max_length=2000, description="推荐描述")
    recommendation_type: RecommendationType = Field(..., description="推荐类型")
    
    # 推荐内容
    recommended_actions: List[RecommendationAction] = Field([], description="推荐操作列表")
    context_data: List[RecommendationContext] = Field([], description="上下文数据")
    
    # 置信度和优先级
    confidence_score: float = Field(..., ge=0, le=1, description="置信度分数")
    priority: RecommendationPriority = Field(..., description="优先级")
    
    # 预期收益
    estimated_savings: Optional[Decimal] = Field(None, ge=0, description="预计节省金额")
    estimated_earnings: Optional[Decimal] = Field(None, ge=0, description="预计收益金额")
    roi_percentage: Optional[float] = Field(None, ge=0, description="投资回报率")
    
    # 有效期和展示
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    display_until: Optional[datetime] = Field(None, description="展示截止时间")
    is_personalized: bool = Field(True, description="是否个性化推荐")
    
    # 关联数据
    related_card_ids: List[UUID] = Field([], description="相关信用卡ID列表")
    related_category_ids: List[str] = Field([], description="相关分类ID列表")
    
    @validator('display_until')
    def validate_display_time(cls, v, values):
        """验证展示时间"""
        expires_at = values.get('expires_at')
        if expires_at and v and v > expires_at:
            raise ValueError("展示截止时间不能晚于过期时间")
        return v


class RecommendationResultResponse(RecommendationResultBase):
    """推荐结果响应模型"""
    id: UUID = Field(..., description="推荐结果ID")
    rule_id: UUID = Field(..., description="规则ID")
    user_id: UUID = Field(..., description="用户ID")
    
    # 状态和反馈
    status: RecommendationStatus = Field(RecommendationStatus.ACTIVE, description="推荐状态")
    user_feedback: Optional[str] = Field(None, description="用户反馈")
    feedback_score: Optional[int] = Field(None, ge=1, le=5, description="反馈评分")
    
    # 交互数据
    view_count: int = Field(0, description="查看次数")
    click_count: int = Field(0, description="点击次数")
    last_viewed_at: Optional[datetime] = Field(None, description="最后查看时间")
    
    # 执行结果
    is_executed: bool = Field(False, description="是否已执行")
    executed_at: Optional[datetime] = Field(None, description="执行时间")
    actual_result: Optional[Dict[str, Any]] = Field(None, description="实际执行结果")
    
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "recommendation-uuid-here",
                "rule_id": "rule-uuid-here",
                "user_id": "user-uuid-here",
                "title": "使用A卡进行餐饮消费获得更多返现",
                "description": "根据您的消费模式，使用A银行信用卡进行餐饮消费可获得5%返现，比当前使用的B卡多2%",
                "recommendation_type": "spending_optimization",
                "confidence_score": 0.85,
                "priority": "high",
                "estimated_savings": 200.00,
                "status": "active",
                "view_count": 3,
                "click_count": 1,
                "is_executed": False,
                "created_at": "2024-12-01T10:00:00Z"
            }
        }


# ================================
# 用户反馈相关模型
# ================================

class UserFeedbackBase(BaseModel):
    """用户反馈基础模型"""
    feedback_type: FeedbackType = Field(..., description="反馈类型")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分，1-5星")
    comment: Optional[str] = Field(None, max_length=500, description="反馈评论")
    
    # 详细反馈
    is_helpful: Optional[bool] = Field(None, description="是否有帮助")
    is_accurate: Optional[bool] = Field(None, description="是否准确")
    is_timely: Optional[bool] = Field(None, description="是否及时")
    
    # 改进建议
    improvement_suggestions: Optional[List[str]] = Field(None, description="改进建议列表")
    
    @validator('improvement_suggestions')
    def validate_suggestions(cls, v):
        """验证改进建议"""
        if v and len(v) > 10:
            raise ValueError("改进建议不能超过10条")
        return v


class UserFeedbackCreate(UserFeedbackBase):
    """创建用户反馈请求模型"""
    recommendation_id: UUID = Field(..., description="推荐结果ID")
    
    class Config:
        schema_extra = {
            "example": {
                "recommendation_id": "recommendation-uuid-here",
                "feedback_type": "useful",
                "rating": 4,
                "comment": "推荐很准确，已经按建议执行了",
                "is_helpful": True,
                "is_accurate": True,
                "is_timely": True,
                "improvement_suggestions": ["希望提供更多执行步骤"]
            }
        }


class UserFeedbackResponse(UserFeedbackBase):
    """用户反馈响应模型"""
    id: UUID = Field(..., description="反馈ID")
    recommendation_id: UUID = Field(..., description="推荐结果ID")
    user_id: UUID = Field(..., description="用户ID")
    
    # 处理状态
    is_processed: bool = Field(False, description="是否已处理")
    processed_at: Optional[datetime] = Field(None, description="处理时间")
    admin_response: Optional[str] = Field(None, description="管理员回复")
    
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


# ================================
# 查询和过滤模型
# ================================

class RecommendationRuleQuery(BaseQueryParams):
    """推荐规则查询参数"""
    recommendation_type: Optional[RecommendationType] = Field(None, description="推荐类型筛选")
    priority: Optional[RecommendationPriority] = Field(None, description="优先级筛选")
    is_active: Optional[bool] = Field(None, description="激活状态筛选")
    is_ml_based: Optional[bool] = Field(None, description="是否基于机器学习筛选")
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "keyword": "餐饮",
                "recommendation_type": "card_selection",
                "priority": "high",
                "is_active": True
            }
        }


class RecommendationResultQuery(BaseQueryParams):
    """推荐结果查询参数"""
    recommendation_type: Optional[RecommendationType] = Field(None, description="推荐类型筛选")
    priority: Optional[RecommendationPriority] = Field(None, description="优先级筛选")
    status: Optional[RecommendationStatus] = Field(None, description="状态筛选")
    min_confidence: Optional[float] = Field(None, ge=0, le=1, description="最小置信度")
    
    # 时间筛选
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    
    # 关联筛选
    card_id: Optional[UUID] = Field(None, description="关联信用卡筛选")
    category: Optional[str] = Field(None, description="关联分类筛选")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError("结束日期不能早于开始日期")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "recommendation_type": "spending_optimization",
                "priority": "high",
                "status": "active",
                "min_confidence": 0.7,
                "start_date": "2024-12-01",
                "end_date": "2024-12-31"
            }
        }


# ================================
# 批量操作模型
# ================================

class BatchRecommendationOperation(BaseModel):
    """批量推荐操作模型"""
    recommendation_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="推荐ID列表")
    operation: str = Field(..., description="操作类型：accept/reject/ignore/archive")
    feedback_type: Optional[FeedbackType] = Field(None, description="批量反馈类型")
    batch_comment: Optional[str] = Field(None, max_length=200, description="批量操作备注")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['accept', 'reject', 'ignore', 'archive', 'mark_viewed']
        if v not in allowed_operations:
            raise ValueError(f"操作类型必须是：{', '.join(allowed_operations)}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "recommendation_ids": ["uuid1", "uuid2", "uuid3"],
                "operation": "accept",
                "feedback_type": "useful",
                "batch_comment": "批量接受相关推荐"
            }
        }


# ================================
# 统计分析模型
# ================================

class RecommendationStatistics(BaseModel):
    """推荐统计模型"""
    total_recommendations: int = Field(0, description="总推荐数")
    active_recommendations: int = Field(0, description="活跃推荐数")
    
    # 状态分布
    status_distribution: Dict[str, int] = Field({}, description="状态分布")
    type_distribution: Dict[str, int] = Field({}, description="类型分布")
    priority_distribution: Dict[str, int] = Field({}, description="优先级分布")
    
    # 性能指标
    avg_confidence_score: float = Field(0.0, description="平均置信度")
    overall_acceptance_rate: float = Field(0.0, description="总体接受率")
    avg_user_rating: float = Field(0.0, description="平均用户评分")
    
    # 收益统计
    total_estimated_savings: Decimal = Field(0, description="总预计节省")
    total_actual_savings: Decimal = Field(0, description="总实际节省")
    roi_achieved: float = Field(0.0, description="实现的投资回报率")
    
    # 近期趋势
    daily_generation_rate: float = Field(0.0, description="日均生成率")
    weekly_acceptance_trend: List[float] = Field([], description="周接受率趋势")
    
    class Config:
        schema_extra = {
            "example": {
                "total_recommendations": 450,
                "active_recommendations": 85,
                "status_distribution": {
                    "active": 85,
                    "accepted": 200,
                    "rejected": 120,
                    "expired": 45
                },
                "type_distribution": {
                    "card_selection": 150,
                    "spending_optimization": 180,
                    "cashback_maximization": 120
                },
                "avg_confidence_score": 0.78,
                "overall_acceptance_rate": 44.4,
                "avg_user_rating": 3.8,
                "total_estimated_savings": 15000.00,
                "total_actual_savings": 8500.00,
                "roi_achieved": 56.7
            }
        }


class RecommendationPerformanceMetrics(BaseModel):
    """推荐性能指标模型"""
    rule_id: UUID = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    
    # 生成指标
    total_generated: int = Field(0, description="总生成数")
    avg_confidence: float = Field(0.0, description="平均置信度")
    
    # 用户交互指标
    total_views: int = Field(0, description="总查看数")
    total_clicks: int = Field(0, description="总点击数")
    click_through_rate: float = Field(0.0, description="点击率")
    
    # 转化指标
    total_accepted: int = Field(0, description="总接受数")
    total_rejected: int = Field(0, description="总拒绝数")
    acceptance_rate: float = Field(0.0, description="接受率")
    
    # 执行效果
    total_executed: int = Field(0, description="总执行数")
    execution_success_rate: float = Field(0.0, description="执行成功率")
    
    # 用户满意度
    avg_rating: float = Field(0.0, description="平均评分")
    feedback_count: int = Field(0, description="反馈数量")
    
    class Config:
        schema_extra = {
            "example": {
                "rule_id": "rule-uuid-here",
                "rule_name": "餐饮消费优化推荐",
                "total_generated": 125,
                "avg_confidence": 0.82,
                "total_views": 98,
                "total_clicks": 45,
                "click_through_rate": 45.9,
                "total_accepted": 35,
                "acceptance_rate": 35.7,
                "total_executed": 28,
                "execution_success_rate": 80.0,
                "avg_rating": 4.1,
                "feedback_count": 22
            }
        }


# ================================
# 机器学习模型配置
# ================================

class MLModelConfig(BaseModel):
    """机器学习模型配置模型"""
    model_id: str = Field(..., description="模型ID")
    model_name: str = Field(..., description="模型名称")
    model_type: MLModelType = Field(..., description="模型类型")
    
    # 模型参数
    hyperparameters: Dict[str, Any] = Field({}, description="超参数配置")
    feature_config: Dict[str, Any] = Field({}, description="特征配置")
    
    # 训练配置
    training_data_size: int = Field(0, description="训练数据大小")
    validation_split: float = Field(0.2, ge=0.1, le=0.5, description="验证集比例")
    
    # 性能指标
    accuracy: Optional[float] = Field(None, description="准确率")
    precision: Optional[float] = Field(None, description="精确率")
    recall: Optional[float] = Field(None, description="召回率")
    f1_score: Optional[float] = Field(None, description="F1分数")
    
    # 状态信息
    is_trained: bool = Field(False, description="是否已训练")
    is_active: bool = Field(True, description="是否激活")
    last_trained_at: Optional[datetime] = Field(None, description="最后训练时间")
    next_retrain_at: Optional[datetime] = Field(None, description="下次重训练时间")
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "cf_dining_v1",
                "model_name": "餐饮消费协同过滤模型",
                "model_type": "collaborative_filtering",
                "hyperparameters": {
                    "n_factors": 50,
                    "learning_rate": 0.01,
                    "regularization": 0.1
                },
                "training_data_size": 10000,
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.78,
                "f1_score": 0.80,
                "is_trained": True,
                "is_active": True
            }
        }


# ================================
# 特殊操作模型
# ================================

class RecommendationPreferences(BaseModel):
    """推荐偏好设置模型"""
    preferred_types: List[RecommendationType] = Field([], description="偏好的推荐类型")
    excluded_types: List[RecommendationType] = Field([], description="排除的推荐类型")
    max_daily_recommendations: int = Field(5, ge=1, le=20, description="每日最大推荐数")
    min_confidence_threshold: float = Field(0.6, ge=0.3, le=1.0, description="最小置信度阈值")
    
    # 通知设置
    enable_notifications: bool = Field(True, description="启用通知")
    notification_channels: List[str] = Field(["in_app"], description="通知渠道")
    quiet_hours_start: Optional[str] = Field(None, description="免打扰开始时间")
    quiet_hours_end: Optional[str] = Field(None, description="免打扰结束时间")
    
    # 个性化设置
    learning_enabled: bool = Field(True, description="启用学习功能")
    share_anonymous_data: bool = Field(True, description="共享匿名数据用于改进")
    
    class Config:
        schema_extra = {
            "example": {
                "preferred_types": ["card_selection", "spending_optimization"],
                "excluded_types": ["promotional_offers"],
                "max_daily_recommendations": 3,
                "min_confidence_threshold": 0.75,
                "enable_notifications": True,
                "notification_channels": ["in_app", "email"],
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00",
                "learning_enabled": True
            }
        }


class RecommendationExplanation(BaseModel):
    """推荐解释模型"""
    explanation_text: str = Field(..., description="解释文本")
    key_factors: List[Dict[str, Any]] = Field([], description="关键因素")
    confidence_breakdown: Dict[str, float] = Field({}, description="置信度分解")
    similar_users_data: Optional[Dict[str, Any]] = Field(None, description="相似用户数据")
    historical_performance: Optional[Dict[str, Any]] = Field(None, description="历史性能")
    
    class Config:
        schema_extra = {
            "example": {
                "explanation_text": "基于您过去3个月的餐饮消费模式（平均每月1500元），推荐使用A银行信用卡",
                "key_factors": [
                    {
                        "factor": "monthly_dining_spend",
                        "value": 1500,
                        "weight": 0.4,
                        "description": "月均餐饮支出"
                    }
                ],
                "confidence_breakdown": {
                    "spending_pattern": 0.4,
                    "card_features": 0.3,
                    "similar_users": 0.2,
                    "historical_success": 0.1
                }
            }
        }


# ================================
# 响应模型
# ================================

class RecommendationRuleListResponse(BasePaginatedResponse):
    """推荐规则列表响应"""
    data: List[RecommendationRuleResponse] = Field([], description="推荐规则列表")


class RecommendationResultListResponse(BasePaginatedResponse):
    """推荐结果列表响应"""
    data: List[RecommendationResultResponse] = Field([], description="推荐结果列表")


class UserFeedbackListResponse(BasePaginatedResponse):
    """用户反馈列表响应"""
    data: List[UserFeedbackResponse] = Field([], description="用户反馈列表")


class RecommendationStatisticsResponse(BaseResponse):
    """推荐统计响应"""
    data: RecommendationStatistics = Field(..., description="统计数据")


class RecommendationPerformanceResponse(BaseResponse):
    """推荐性能响应"""
    data: List[RecommendationPerformanceMetrics] = Field([], description="性能指标列表")


class MLModelConfigListResponse(BaseResponse):
    """机器学习模型配置列表响应"""
    data: List[MLModelConfig] = Field([], description="模型配置列表")


class RecommendationExplanationResponse(BaseResponse):
    """推荐解释响应"""
    data: RecommendationExplanation = Field(..., description="推荐解释")


class BatchOperationResult(BaseModel):
    """批量操作结果模型"""
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    failed_items: List[Dict[str, Any]] = Field([], description="失败项详情")
    
    class Config:
        schema_extra = {
            "example": {
                "total_count": 5,
                "success_count": 4,
                "failed_count": 1,
                "failed_items": [
                    {
                        "id": "uuid5",
                        "error": "推荐已过期"
                    }
                ]
            }
        } 