"""
推荐服务

提供智能推荐相关的业务逻辑，包括推荐生成、规则管理、用户反馈等功能
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.database.recommendation import RecommendationRule, RecommendationRecord
from app.models.database.user import User
from app.models.database.card import CreditCard
from app.models.database.transaction import Transaction
from app.models.schemas.recommendation import (
    RecommendationRuleCreate, RecommendationRuleUpdate,
    RecommendationRecordCreate, RecommendationRecordUpdate,
    RecommendationQuery, RecommendationFeedback,
    SmartRecommendationRequest, RecommendationStats
)
from app.utils.pagination import paginate


class RecommendationService:
    """推荐服务类"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 推荐规则管理 ====================

    def create_rule(self, rule_data: RecommendationRuleCreate) -> RecommendationRule:
        """创建推荐规则"""
        rule = RecommendationRule(**rule_data.model_dump())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_rule_by_id(self, rule_id: UUID) -> Optional[RecommendationRule]:
        """根据ID获取推荐规则"""
        return self.db.query(RecommendationRule).filter(
            RecommendationRule.id == rule_id
        ).first()

    def get_rules(
        self,
        rule_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[RecommendationRule], int]:
        """获取推荐规则列表"""
        query = self.db.query(RecommendationRule)

        # 筛选条件
        if rule_type:
            query = query.filter(RecommendationRule.rule_type == rule_type)
        if is_active is not None:
            query = query.filter(RecommendationRule.is_active == is_active)

        # 排序
        query = query.order_by(desc(RecommendationRule.priority), desc(RecommendationRule.created_at))

        return paginate(query, page, page_size)

    def update_rule(self, rule_id: UUID, rule_data: RecommendationRuleUpdate) -> Optional[RecommendationRule]:
        """更新推荐规则"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return None

        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: UUID) -> bool:
        """删除推荐规则"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()
        return True

    # ==================== 推荐记录管理 ====================

    def create_recommendation(
        self,
        user_id: UUID,
        recommendation_data: RecommendationRecordCreate
    ) -> RecommendationRecord:
        """创建推荐记录"""
        record = RecommendationRecord(
            user_id=user_id,
            **recommendation_data.model_dump()
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_recommendation_by_id(
        self,
        recommendation_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[RecommendationRecord]:
        """根据ID获取推荐记录"""
        query = self.db.query(RecommendationRecord).filter(
            RecommendationRecord.id == recommendation_id
        )
        
        if user_id:
            query = query.filter(RecommendationRecord.user_id == user_id)
        
        return query.first()

    def get_user_recommendations(
        self,
        user_id: UUID,
        query_params: RecommendationQuery
    ) -> Tuple[List[RecommendationRecord], int]:
        """获取用户推荐记录列表"""
        query = self.db.query(RecommendationRecord).filter(
            RecommendationRecord.user_id == user_id
        )

        # 筛选条件
        if query_params.recommendation_type:
            query = query.filter(
                RecommendationRecord.recommendation_type == query_params.recommendation_type
            )
        if query_params.status:
            query = query.filter(RecommendationRecord.status == query_params.status)
        if query_params.user_action:
            query = query.filter(RecommendationRecord.user_action == query_params.user_action)
        if query_params.start_date:
            query = query.filter(RecommendationRecord.created_at >= query_params.start_date)
        if query_params.end_date:
            query = query.filter(RecommendationRecord.created_at <= query_params.end_date)

        # 排序
        query = query.order_by(desc(RecommendationRecord.created_at))

        return paginate(query, query_params.page, query_params.page_size)

    def update_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID,
        update_data: RecommendationRecordUpdate
    ) -> Optional[RecommendationRecord]:
        """更新推荐记录"""
        record = self.get_recommendation_by_id(recommendation_id, user_id)
        if not record:
            return None

        update_fields = update_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(record, field, value)

        self.db.commit()
        self.db.refresh(record)
        return record

    def submit_feedback(
        self,
        recommendation_id: UUID,
        user_id: UUID,
        feedback_data: RecommendationFeedback
    ) -> Optional[RecommendationRecord]:
        """提交推荐反馈"""
        record = self.get_recommendation_by_id(recommendation_id, user_id)
        if not record:
            return None

        record.user_action = feedback_data.user_action
        record.feedback = feedback_data.feedback
        record.status = "acted"

        self.db.commit()
        self.db.refresh(record)
        return record

    # ==================== 智能推荐生成 ====================

    def generate_smart_recommendations(
        self,
        user_id: UUID,
        request: SmartRecommendationRequest
    ) -> List[RecommendationRecord]:
        """生成智能推荐"""
        recommendations = []

        # 获取用户信息
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return recommendations

        # 获取用户信用卡信息
        cards = self.db.query(CreditCard).filter(
            CreditCard.user_id == user_id,
            CreditCard.status == "active"
        ).all()

        # 获取用户交易信息（最近3个月）
        three_months_ago = datetime.now() - timedelta(days=90)
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= three_months_ago
        ).all()

        # 生成不同类型的推荐
        if not request.recommendation_types or "card_usage" in request.recommendation_types:
            recommendations.extend(self._generate_card_usage_recommendations(user_id, cards, transactions))

        if not request.recommendation_types or "fee_optimization" in request.recommendation_types:
            recommendations.extend(self._generate_fee_optimization_recommendations(user_id, cards))

        if not request.recommendation_types or "category_analysis" in request.recommendation_types:
            recommendations.extend(self._generate_category_analysis_recommendations(user_id, transactions))

        # 限制推荐数量
        recommendations = recommendations[:request.limit]

        # 保存推荐记录
        saved_recommendations = []
        for rec_data in recommendations:
            record = RecommendationRecord(
                user_id=user_id,
                **rec_data
            )
            self.db.add(record)
            saved_recommendations.append(record)

        self.db.commit()

        # 刷新记录
        for record in saved_recommendations:
            self.db.refresh(record)

        return saved_recommendations

    def _generate_card_usage_recommendations(
        self,
        user_id: UUID,
        cards: List[CreditCard],
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """生成信用卡使用推荐"""
        recommendations = []

        if not cards:
            return recommendations

        # 计算信用卡利用率
        for card in cards:
            if card.credit_limit > 0:
                utilization = card.used_limit / card.credit_limit
                
                # 低利用率推荐
                if utilization < 0.1:
                    recommendations.append({
                        "recommendation_type": "card_usage",
                        "title": f"{card.card_name}利用率较低",
                        "content": f"您的{card.card_name}信用利用率仅为{utilization:.1%}，建议适当增加使用以提升信用记录。",
                        "action_data": {
                            "card_id": str(card.id),
                            "current_utilization": utilization,
                            "recommended_action": "increase_usage"
                        }
                    })
                
                # 高利用率警告
                elif utilization > 0.8:
                    recommendations.append({
                        "recommendation_type": "card_usage",
                        "title": f"{card.card_name}利用率过高",
                        "content": f"您的{card.card_name}信用利用率已达{utilization:.1%}，建议及时还款或申请提额。",
                        "action_data": {
                            "card_id": str(card.id),
                            "current_utilization": utilization,
                            "recommended_action": "reduce_usage"
                        }
                    })

        return recommendations

    def _generate_fee_optimization_recommendations(
        self,
        user_id: UUID,
        cards: List[CreditCard]
    ) -> List[Dict[str, Any]]:
        """生成年费优化推荐"""
        recommendations = []

        for card in cards:
            if card.annual_fee > 0 and card.fee_waivable:
                recommendations.append({
                    "recommendation_type": "fee_optimization",
                    "title": f"{card.card_name}年费减免机会",
                    "content": f"您的{card.card_name}年费为{card.annual_fee}元，可通过达成消费条件减免年费。",
                    "action_data": {
                        "card_id": str(card.id),
                        "annual_fee": float(card.annual_fee),
                        "recommended_action": "check_waiver_rules"
                    }
                })

        return recommendations

    def _generate_category_analysis_recommendations(
        self,
        user_id: UUID,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """生成消费分类分析推荐"""
        recommendations = []

        if not transactions:
            return recommendations

        # 分析消费类别
        category_spending = {}
        total_spending = 0

        for transaction in transactions:
            if transaction.transaction_type == "expense":
                category = transaction.merchant_category or "其他"
                amount = float(transaction.amount)
                category_spending[category] = category_spending.get(category, 0) + amount
                total_spending += amount

        if total_spending > 0:
            # 找出最大消费类别
            top_category = max(category_spending.items(), key=lambda x: x[1])
            category_name, category_amount = top_category
            category_percentage = category_amount / total_spending

            if category_percentage > 0.3:  # 如果某类别占比超过30%
                recommendations.append({
                    "recommendation_type": "category_analysis",
                    "title": f"{category_name}消费占比较高",
                    "content": f"您在{category_name}类别的消费占总消费的{category_percentage:.1%}，建议选择在此类别有优惠的信用卡。",
                    "action_data": {
                        "category": category_name,
                        "amount": category_amount,
                        "percentage": category_percentage,
                        "recommended_action": "optimize_card_for_category"
                    }
                })

        return recommendations

    # ==================== 推荐统计 ====================

    def get_recommendation_stats(self, user_id: UUID) -> RecommendationStats:
        """获取推荐统计信息"""
        # 基础统计
        total_query = self.db.query(RecommendationRecord).filter(
            RecommendationRecord.user_id == user_id
        )
        
        total_recommendations = total_query.count()
        pending_recommendations = total_query.filter(
            RecommendationRecord.status == "pending"
        ).count()
        accepted_recommendations = total_query.filter(
            RecommendationRecord.user_action == "accepted"
        ).count()
        rejected_recommendations = total_query.filter(
            RecommendationRecord.user_action == "rejected"
        ).count()

        # 类型分布
        type_distribution = {}
        type_stats = self.db.query(
            RecommendationRecord.recommendation_type,
            func.count(RecommendationRecord.id).label('count')
        ).filter(
            RecommendationRecord.user_id == user_id
        ).group_by(RecommendationRecord.recommendation_type).all()

        for type_name, count in type_stats:
            type_distribution[type_name] = count

        # 最近推荐
        recent_recommendations = self.db.query(RecommendationRecord).filter(
            RecommendationRecord.user_id == user_id
        ).order_by(desc(RecommendationRecord.created_at)).limit(5).all()

        return RecommendationStats(
            total_recommendations=total_recommendations,
            pending_recommendations=pending_recommendations,
            accepted_recommendations=accepted_recommendations,
            rejected_recommendations=rejected_recommendations,
            type_distribution=type_distribution,
            recent_recommendations=recent_recommendations
        )

    def mark_recommendation_as_read(self, recommendation_id: UUID, user_id: UUID) -> bool:
        """标记推荐为已读"""
        record = self.get_recommendation_by_id(recommendation_id, user_id)
        if not record:
            return False

        if record.status == "pending":
            record.status = "read"
            self.db.commit()

        return True

    def get_active_rules(self) -> List[RecommendationRule]:
        """获取所有激活的推荐规则"""
        return self.db.query(RecommendationRule).filter(
            RecommendationRule.is_active == True
        ).order_by(desc(RecommendationRule.priority)).all()

    def evaluate_rules_for_user(self, user_id: UUID) -> List[RecommendationRecord]:
        """为用户评估所有激活的推荐规则"""
        rules = self.get_active_rules()
        recommendations = []

        for rule in rules:
            if self._evaluate_rule_conditions(user_id, rule):
                record = RecommendationRecord(
                    user_id=user_id,
                    rule_id=rule.id,
                    recommendation_type=rule.rule_type,
                    title=rule.recommendation_title or f"{rule.rule_name}推荐",
                    content=rule.recommendation_content or "系统为您生成的个性化推荐",
                    action_data={"rule_id": str(rule.id), "rule_name": rule.rule_name}
                )
                self.db.add(record)
                recommendations.append(record)

        if recommendations:
            self.db.commit()
            for record in recommendations:
                self.db.refresh(record)

        return recommendations

    def _evaluate_rule_conditions(self, user_id: UUID, rule: RecommendationRule) -> bool:
        """评估规则条件是否满足"""
        # 这里可以根据规则的conditions字段实现复杂的条件评估逻辑
        # 简化实现，实际项目中可以扩展为更复杂的规则引擎
        conditions = rule.conditions
        
        # 示例：检查信用利用率条件
        if "credit_utilization" in conditions:
            cards = self.db.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.status == "active"
            ).all()
            
            for card in cards:
                if card.credit_limit > 0:
                    utilization = card.used_limit / card.credit_limit
                    util_condition = conditions["credit_utilization"]
                    
                    if "max" in util_condition and utilization <= util_condition["max"]:
                        return True
                    if "min" in util_condition and utilization >= util_condition["min"]:
                        return True

        return False 