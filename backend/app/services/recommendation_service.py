"""
智能推荐服务层

包含推荐规则引擎、推荐结果生成、用户反馈处理等功能。
新架构下的智能推荐服务。
"""

import logging
from datetime import datetime, date, timedelta, UTC
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.models.schemas.recommendation import (
    RecommendationResult,
    RecommendationResultCreate,
    RecommendationRule,
    RecommendationRuleCreate,
    UserFeedback,
    UserFeedbackCreate,
    RecommendationQueryFilter,
    RecommendationBatchOperation,
    RecommendationStats,
    RecommendationExplanation,
    MLModelConfig,
    RecommendationType,
    RecommendationPriority,
    RecommendationStatus,
    FeedbackType
)
from app.models.database.recommendation import (
    RecommendationResult as DBRecommendationResult,
    RecommendationRule as DBRecommendationRule,
    UserFeedback as DBUserFeedback
)
from app.models.database.card import CreditCard as DBCard
from app.models.database.transaction import Transaction as DBTransaction
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class RecommendationService:
    """智能推荐服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 推荐结果管理 ====================

    def get_recommendations(
        self,
        user_id: UUID,
        filter_params: RecommendationQueryFilter,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[RecommendationResult], int]:
        """获取推荐结果列表"""
        try:
            query = self.db.query(DBRecommendationResult).filter(
                DBRecommendationResult.user_id == user_id
            )
            
            # 应用过滤条件
            if filter_params.recommendation_type:
                query = query.filter(
                    DBRecommendationResult.recommendation_type == filter_params.recommendation_type
                )
            
            if filter_params.priority:
                query = query.filter(DBRecommendationResult.priority == filter_params.priority)
            
            if filter_params.status:
                query = query.filter(DBRecommendationResult.status == filter_params.status)
            
            if filter_params.start_date:
                query = query.filter(DBRecommendationResult.created_at >= filter_params.start_date)
            
            if filter_params.end_date:
                query = query.filter(DBRecommendationResult.created_at <= filter_params.end_date)
            
            if filter_params.keyword:
                keyword_filter = f"%{filter_params.keyword}%"
                query = query.filter(
                    or_(
                        DBRecommendationResult.title.ilike(keyword_filter),
                        DBRecommendationResult.description.ilike(keyword_filter)
                    )
                )
            
            total = query.count()
            recommendations = query.order_by(
                desc(DBRecommendationResult.priority),
                desc(DBRecommendationResult.created_at)
            ).offset(skip).limit(limit).all()
            
            return [RecommendationResult.model_validate(rec) for rec in recommendations], total
            
        except Exception as e:
            logger.error(f"获取推荐结果失败: {str(e)}")
            raise

    def get_recommendation_by_id(
        self, 
        recommendation_id: UUID, 
        user_id: UUID
    ) -> Optional[RecommendationResult]:
        """获取单个推荐结果"""
        try:
            recommendation = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.id == recommendation_id,
                    DBRecommendationResult.user_id == user_id
                )
            ).first()
            
            if not recommendation:
                return None
                
            return RecommendationResult.model_validate(recommendation)
            
        except Exception as e:
            logger.error(f"获取推荐结果失败: {str(e)}")
            raise

    def create_recommendation(
        self,
        user_id: UUID,
        recommendation_data: RecommendationResultCreate
    ) -> RecommendationResult:
        """创建推荐结果"""
        try:
            logger.info(f"创建推荐结果", extra={
                "user_id": str(user_id),
                "recommendation_type": recommendation_data.recommendation_type.value
            })
            
            # 创建推荐记录
            rec_dict = recommendation_data.model_dump(exclude_unset=True)
            rec_dict['user_id'] = user_id
            
            db_recommendation = DBRecommendationResult(**rec_dict)
            self.db.add(db_recommendation)
            self.db.commit()
            self.db.refresh(db_recommendation)
            
            logger.info(f"推荐结果创建成功", extra={
                "recommendation_id": str(db_recommendation.id),
                "user_id": str(user_id)
            })
            
            return RecommendationResult.model_validate(db_recommendation)
            
        except Exception as e:
            logger.error(f"创建推荐结果失败: {str(e)}")
            self.db.rollback()
            raise

    def update_recommendation_status(
        self,
        recommendation_id: UUID,
        user_id: UUID,
        status: RecommendationStatus
    ) -> bool:
        """更新推荐状态"""
        try:
            recommendation = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.id == recommendation_id,
                    DBRecommendationResult.user_id == user_id
                )
            ).first()
            
            if not recommendation:
                return False
            
            recommendation.status = status
            recommendation.updated_at = datetime.now(UTC)
            
            if status == RecommendationStatus.ACCEPTED:
                recommendation.accepted_at = datetime.now(UTC)
            elif status == RecommendationStatus.DISMISSED:
                recommendation.dismissed_at = datetime.now(UTC)
            
            self.db.commit()
            
            logger.info(f"推荐状态更新成功", extra={
                "recommendation_id": str(recommendation_id),
                "status": status.value,
                "user_id": str(user_id)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"更新推荐状态失败: {str(e)}")
            self.db.rollback()
            raise

    # ==================== 用户反馈管理 ====================

    def submit_feedback(
        self,
        user_id: UUID,
        feedback_data: UserFeedbackCreate
    ) -> UserFeedback:
        """提交用户反馈"""
        try:
            # 验证推荐是否属于该用户
            recommendation = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.id == feedback_data.recommendation_id,
                    DBRecommendationResult.user_id == user_id
                )
            ).first()
            
            if not recommendation:
                raise ValueError("推荐不存在或不属于该用户")
            
            # 创建反馈记录
            feedback_dict = feedback_data.model_dump(exclude_unset=True)
            feedback_dict['user_id'] = user_id
            
            db_feedback = DBUserFeedback(**feedback_dict)
            self.db.add(db_feedback)
            self.db.commit()
            self.db.refresh(db_feedback)
            
            logger.info(f"用户反馈提交成功", extra={
                "feedback_id": str(db_feedback.id),
                "recommendation_id": str(feedback_data.recommendation_id),
                "feedback_type": feedback_data.feedback_type.value,
                "user_id": str(user_id)
            })
            
            return UserFeedback.model_validate(db_feedback)
            
        except Exception as e:
            logger.error(f"提交用户反馈失败: {str(e)}")
            self.db.rollback()
            raise

    def get_user_feedbacks(
        self,
        user_id: UUID,
        recommendation_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[UserFeedback], int]:
        """获取用户反馈列表"""
        try:
            query = self.db.query(DBUserFeedback).filter(
                DBUserFeedback.user_id == user_id
            )
            
            if recommendation_id:
                query = query.filter(DBUserFeedback.recommendation_id == recommendation_id)
            
            total = query.count()
            feedbacks = query.order_by(
                desc(DBUserFeedback.created_at)
            ).offset(skip).limit(limit).all()
            
            return [UserFeedback.model_validate(feedback) for feedback in feedbacks], total
            
        except Exception as e:
            logger.error(f"获取用户反馈失败: {str(e)}")
            raise

    # ==================== 智能推荐引擎 ====================

    def generate_recommendations(self, user_id: UUID) -> List[RecommendationResult]:
        """生成智能推荐"""
        try:
            logger.info(f"开始生成智能推荐", extra={"user_id": str(user_id)})
            
            recommendations = []
            
            # 生成不同类型的推荐
            recommendations.extend(self._generate_card_recommendations(user_id))
            recommendations.extend(self._generate_optimization_recommendations(user_id))
            recommendations.extend(self._generate_promotion_recommendations(user_id))
            recommendations.extend(self._generate_risk_recommendations(user_id))
            
            # 保存推荐结果
            saved_recommendations = []
            for rec_data in recommendations:
                rec = self.create_recommendation(user_id, rec_data)
                saved_recommendations.append(rec)
            
            logger.info(f"智能推荐生成完成", extra={
                "user_id": str(user_id),
                "recommendations_count": len(saved_recommendations)
            })
            
            return saved_recommendations
            
        except Exception as e:
            logger.error(f"生成智能推荐失败: {str(e)}")
            raise

    def _generate_card_recommendations(self, user_id: UUID) -> List[RecommendationResultCreate]:
        """生成信用卡推荐"""
        recommendations = []
        
        try:
            # 获取用户的消费数据
            spending_stats = self._get_user_spending_stats(user_id)
            
            # 如果没有信用卡，推荐办卡
            card_count = self.db.query(DBCard).filter(DBCard.user_id == user_id).count()
            
            if card_count == 0:
                recommendations.append(RecommendationResultCreate(
                    recommendation_type=RecommendationType.CARD_APPLICATION,
                    priority=RecommendationPriority.HIGH,
                    title="推荐申请第一张信用卡",
                    description="根据您的情况，建议申请一张适合日常消费的信用卡",
                    action_suggestion="选择年费较低、权益丰富的入门级信用卡",
                    expected_benefit="享受信用卡便利，建立个人信用记录",
                    confidence_score=0.85
                ))
            
            # 基于消费分析推荐新卡
            elif spending_stats.get('monthly_spending', 0) > 5000:
                recommendations.append(RecommendationResultCreate(
                    recommendation_type=RecommendationType.CARD_APPLICATION,
                    priority=RecommendationPriority.MEDIUM,
                    title="推荐申请高端信用卡",
                    description=f"您的月均消费达到{spending_stats['monthly_spending']:.0f}元，适合申请高端卡",
                    action_suggestion="考虑申请白金卡或钻石卡，享受更多权益",
                    expected_benefit="获得更高积分回报率和专属服务",
                    confidence_score=0.75
                ))
                
        except Exception as e:
            logger.error(f"生成信用卡推荐失败: {str(e)}")
        
        return recommendations

    def _generate_optimization_recommendations(self, user_id: UUID) -> List[RecommendationResultCreate]:
        """生成优化建议推荐"""
        recommendations = []
        
        try:
            # 检查信用卡利用率
            cards = self.db.query(DBCard).filter(DBCard.user_id == user_id).all()
            
            for card in cards:
                utilization_rate = self._calculate_utilization_rate(card.id)
                
                if utilization_rate > 0.8:  # 利用率过高
                    recommendations.append(RecommendationResultCreate(
                        recommendation_type=RecommendationType.USAGE_OPTIMIZATION,
                        priority=RecommendationPriority.HIGH,
                        title=f"{card.card_name} 利用率过高",
                        description=f"该卡当前利用率为{utilization_rate:.1%}，建议及时还款",
                        action_suggestion="尽快还款降低利用率，或申请临时额度",
                        expected_benefit="维护良好的信用记录，避免影响信用评分",
                        confidence_score=0.9,
                        related_card_id=card.id
                    ))
                
                elif utilization_rate < 0.1:  # 利用率过低
                    recommendations.append(RecommendationResultCreate(
                        recommendation_type=RecommendationType.USAGE_OPTIMIZATION,
                        priority=RecommendationPriority.LOW,
                        title=f"{card.card_name} 使用率较低",
                        description=f"该卡利用率仅为{utilization_rate:.1%}，可以考虑优化使用",
                        action_suggestion="增加该卡的日常使用频率，或考虑注销",
                        expected_benefit="提高积分获取效率或减少年费负担",
                        confidence_score=0.6,
                        related_card_id=card.id
                    ))
                    
        except Exception as e:
            logger.error(f"生成优化建议失败: {str(e)}")
        
        return recommendations

    def _generate_promotion_recommendations(self, user_id: UUID) -> List[RecommendationResultCreate]:
        """生成优惠活动推荐"""
        recommendations = []
        
        try:
            # 基于消费习惯推荐优惠活动
            categories = self._get_top_spending_categories(user_id)
            
            for category, amount in categories[:3]:  # 取前三个分类
                recommendations.append(RecommendationResultCreate(
                    recommendation_type=RecommendationType.PROMOTION,
                    priority=RecommendationPriority.MEDIUM,
                    title=f"{category}消费优惠活动",
                    description=f"您在{category}类别月均消费{amount:.0f}元，有相关优惠活动",
                    action_suggestion=f"关注{category}相关的信用卡优惠活动",
                    expected_benefit="享受额外折扣或积分奖励",
                    confidence_score=0.7
                ))
                
        except Exception as e:
            logger.error(f"生成优惠活动推荐失败: {str(e)}")
        
        return recommendations

    def _generate_risk_recommendations(self, user_id: UUID) -> List[RecommendationResultCreate]:
        """生成风险提醒推荐"""
        recommendations = []
        
        try:
            # 检查逾期风险
            overdue_risk = self._check_overdue_risk(user_id)
            
            if overdue_risk['risk_level'] == 'high':
                recommendations.append(RecommendationResultCreate(
                    recommendation_type=RecommendationType.RISK_WARNING,
                    priority=RecommendationPriority.URGENT,
                    title="逾期风险警告",
                    description=overdue_risk['description'],
                    action_suggestion="立即检查还款情况，设置自动还款",
                    expected_benefit="避免逾期记录，保护个人征信",
                    confidence_score=0.95
                ))
            
            # 检查年费风险
            annual_fee_risk = self._check_annual_fee_risk(user_id)
            
            if annual_fee_risk['risk_level'] == 'medium':
                recommendations.append(RecommendationResultCreate(
                    recommendation_type=RecommendationType.COST_OPTIMIZATION,
                    priority=RecommendationPriority.MEDIUM,
                    title="年费优化建议",
                    description=annual_fee_risk['description'],
                    action_suggestion="评估年费减免条件或考虑降级卡片",
                    expected_benefit="减少不必要的年费支出",
                    confidence_score=0.8
                ))
                
        except Exception as e:
            logger.error(f"生成风险提醒失败: {str(e)}")
        
        return recommendations

    # ==================== 数据分析辅助方法 ====================

    def _get_user_spending_stats(self, user_id: UUID) -> Dict[str, Any]:
        """获取用户消费统计"""
        try:
            # 计算最近6个月的消费数据
            six_months_ago = datetime.now(UTC) - timedelta(days=180)
            
            spending_data = self.db.query(
                func.avg(DBTransaction.amount).label('avg_amount'),
                func.sum(DBTransaction.amount).label('total_amount'),
                func.count(DBTransaction.id).label('transaction_count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_type == "expense",
                    DBTransaction.transaction_date >= six_months_ago
                )
            ).first()
            
            if not spending_data.total_amount:
                return {'monthly_spending': 0, 'avg_transaction': 0, 'transaction_count': 0}
            
            monthly_spending = float(spending_data.total_amount) / 6
            avg_transaction = float(spending_data.avg_amount) if spending_data.avg_amount else 0
            
            return {
                'monthly_spending': monthly_spending,
                'avg_transaction': avg_transaction,
                'transaction_count': spending_data.transaction_count
            }
            
        except Exception as e:
            logger.error(f"获取用户消费统计失败: {str(e)}")
            return {'monthly_spending': 0, 'avg_transaction': 0, 'transaction_count': 0}

    def _calculate_utilization_rate(self, card_id: UUID) -> float:
        """计算信用卡利用率"""
        try:
            card = self.db.query(DBCard).filter(DBCard.id == card_id).first()
            if not card or not card.credit_limit:
                return 0.0
            
            # 计算最近一个月的平均余额（简化计算）
            recent_transactions = self.db.query(
                func.sum(DBTransaction.amount)
            ).filter(
                and_(
                    DBTransaction.card_id == card_id,
                    DBTransaction.transaction_date >= datetime.now(UTC) - timedelta(days=30),
                    DBTransaction.transaction_type == "expense"
                )
            ).scalar()
            
            if not recent_transactions:
                return 0.0
            
            # 假设当前余额等于近30天消费的70%（简化）
            estimated_balance = float(recent_transactions) * 0.7
            utilization_rate = estimated_balance / float(card.credit_limit)
            
            return min(max(utilization_rate, 0.0), 1.0)  # 限制在0-1之间
            
        except Exception as e:
            logger.error(f"计算利用率失败: {str(e)}")
            return 0.0

    def _get_top_spending_categories(self, user_id: UUID) -> List[Tuple[str, float]]:
        """获取主要消费分类"""
        try:
            three_months_ago = datetime.now(UTC) - timedelta(days=90)
            
            category_stats = self.db.query(
                DBTransaction.category,
                func.sum(DBTransaction.amount).label('total_amount')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_type == "expense",
                    DBTransaction.transaction_date >= three_months_ago
                )
            ).group_by(DBTransaction.category).order_by(
                desc('total_amount')
            ).limit(5).all()
            
            return [(cat.category, float(cat.total_amount)) for cat in category_stats]
            
        except Exception as e:
            logger.error(f"获取消费分类失败: {str(e)}")
            return []

    def _check_overdue_risk(self, user_id: UUID) -> Dict[str, Any]:
        """检查逾期风险"""
        try:
            # 检查即将到来的还款日
            upcoming_due_dates = self.db.query(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBCard.due_date <= date.today() + timedelta(days=3),
                    DBCard.due_date >= date.today()
                )
            ).count()
            
            if upcoming_due_dates > 0:
                return {
                    'risk_level': 'high',
                    'description': f"您有{upcoming_due_dates}张信用卡即将到达还款日"
                }
            
            return {'risk_level': 'low', 'description': '当前无逾期风险'}
            
        except Exception as e:
            logger.error(f"检查逾期风险失败: {str(e)}")
            return {'risk_level': 'unknown', 'description': '无法评估逾期风险'}

    def _check_annual_fee_risk(self, user_id: UUID) -> Dict[str, Any]:
        """检查年费风险"""
        try:
            # 查找年费较高但使用率低的卡片
            high_fee_cards = self.db.query(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBCard.annual_fee > 500  # 年费超过500元
                )
            ).all()
            
            low_usage_count = 0
            for card in high_fee_cards:
                utilization = self._calculate_utilization_rate(card.id)
                if utilization < 0.1:  # 利用率低于10%
                    low_usage_count += 1
            
            if low_usage_count > 0:
                return {
                    'risk_level': 'medium',
                    'description': f"您有{low_usage_count}张高年费卡使用率较低"
                }
            
            return {'risk_level': 'low', 'description': '年费支出合理'}
            
        except Exception as e:
            logger.error(f"检查年费风险失败: {str(e)}")
            return {'risk_level': 'unknown', 'description': '无法评估年费风险'}

    def get_recommendation_stats(
        self,
        user_id: UUID,
        days: int = 30
    ) -> RecommendationStats:
        """获取推荐统计"""
        try:
            start_date = datetime.now(UTC) - timedelta(days=days)
            
            # 获取基础统计
            total_count = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.user_id == user_id,
                    DBRecommendationResult.created_at >= start_date
                )
            ).count()
            
            accepted_count = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.user_id == user_id,
                    DBRecommendationResult.status == RecommendationStatus.ACCEPTED,
                    DBRecommendationResult.created_at >= start_date
                )
            ).count()
            
            dismissed_count = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.user_id == user_id,
                    DBRecommendationResult.status == RecommendationStatus.DISMISSED,
                    DBRecommendationResult.created_at >= start_date
                )
            ).count()
            
            pending_count = self.db.query(DBRecommendationResult).filter(
                and_(
                    DBRecommendationResult.user_id == user_id,
                    DBRecommendationResult.status == RecommendationStatus.PENDING,
                    DBRecommendationResult.created_at >= start_date
                )
            ).count()
            
            return RecommendationStats(
                total_recommendations=total_count,
                accepted_recommendations=accepted_count,
                dismissed_recommendations=dismissed_count,
                pending_recommendations=pending_count,
                acceptance_rate=float(accepted_count / total_count * 100) if total_count > 0 else 0,
                period_days=days
            )
            
        except Exception as e:
            logger.error(f"获取推荐统计失败: {str(e)}")
            raise

    def batch_operations(
        self,
        user_id: UUID,
        operation: RecommendationBatchOperation
    ) -> Dict[str, Any]:
        """批量操作"""
        try:
            if operation.action == "dismiss":
                updated_count = 0
                for rec_id in operation.recommendation_ids:
                    if self.update_recommendation_status(rec_id, user_id, RecommendationStatus.DISMISSED):
                        updated_count += 1
                
                return {"updated_count": updated_count, "total_requested": len(operation.recommendation_ids)}
            
            elif operation.action == "accept":
                updated_count = 0
                for rec_id in operation.recommendation_ids:
                    if self.update_recommendation_status(rec_id, user_id, RecommendationStatus.ACCEPTED):
                        updated_count += 1
                
                return {"updated_count": updated_count, "total_requested": len(operation.recommendation_ids)}
            
            else:
                raise ValueError(f"不支持的批量操作: {operation.action}")
                
        except Exception as e:
            logger.error(f"批量操作失败: {str(e)}")
            self.db.rollback()
            raise