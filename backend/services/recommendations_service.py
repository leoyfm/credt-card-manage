"""
智能推荐服务

实现基于用户消费情况、免息时长等因素的智能推荐算法。
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from database import get_db
from db_models.cards import CreditCard
from db_models.transactions import Transaction
from db_models.annual_fee import AnnualFeeRule
from db_models.recommendations import Recommendation as DBRecommendation
from models.recommendations import (
    Recommendation, RecommendationCreate, RecommendationUpdate, 
    RecommendationType, RecommendationStatus
)
from models.transactions import TransactionCategory

logger = logging.getLogger(__name__)


class RecommendationsService:
    """智能推荐服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        keyword: str = ""
    ) -> Tuple[List[Recommendation], int]:
        """
        获取用户推荐列表
        
        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            keyword: 搜索关键词
            
        Returns:
            推荐列表和总数
        """
        try:
            logger.info(f"获取推荐列表: user_id={user_id}, keyword='{keyword}'")
            
            query = self.db.query(DBRecommendation).filter(
                DBRecommendation.user_id == user_id,
                DBRecommendation.is_deleted == False
            )
            
            # 模糊搜索
            if keyword.strip():
                search_filter = or_(
                    DBRecommendation.card_name.ilike(f"%{keyword}%"),
                    DBRecommendation.bank_name.ilike(f"%{keyword}%"),
                    DBRecommendation.title.ilike(f"%{keyword}%"),
                    DBRecommendation.description.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            total = query.count()
            recommendations = query.order_by(
                DBRecommendation.recommendation_score.desc(),
                DBRecommendation.is_featured.desc(),
                DBRecommendation.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            return [Recommendation.model_validate(rec) for rec in recommendations], total
            
        except Exception as e:
            logger.error(f"获取推荐列表失败: {str(e)}")
            raise Exception(f"获取推荐列表失败: {str(e)}")

    def get_recommendation(self, rec_id: UUID, user_id: UUID) -> Optional[Recommendation]:
        """
        获取单个推荐详情
        
        Args:
            rec_id: 推荐ID
            user_id: 用户ID
            
        Returns:
            推荐详情或None
        """
        try:
            recommendation = self.db.query(DBRecommendation).filter(
                DBRecommendation.id == rec_id,
                DBRecommendation.user_id == user_id,
                DBRecommendation.is_deleted == False
            ).first()
            
            if not recommendation:
                return None
            
            # 更新查看统计
            recommendation.view_count += 1
            recommendation.last_viewed_at = datetime.utcnow()
            self.db.commit()
                
            return Recommendation.model_validate(recommendation)
            
        except Exception as e:
            logger.error(f"获取推荐失败: {str(e)}")
            raise Exception(f"获取推荐失败: {str(e)}")

    def generate_recommendations(self, user_id: UUID) -> List[Recommendation]:
        """
        生成个性化推荐
        
        基于用户的信用卡使用情况、消费习惯、免息期偏好等生成推荐
        
        Args:
            user_id: 用户ID
            
        Returns:
            推荐列表
        """
        try:
            logger.info(f"开始生成个性化推荐: user_id={user_id}")
            
            # 1. 分析用户消费情况
            user_profile = self._analyze_user_profile(user_id)
            
            # 2. 清理过期推荐
            self._cleanup_expired_recommendations(user_id)
            
            # 3. 生成不同类型的推荐
            recommendations = []
            
            # 现金回馈推荐
            cashback_recs = self._generate_cashback_recommendations(user_id, user_profile)
            recommendations.extend(cashback_recs)
            
            # 积分奖励推荐
            points_recs = self._generate_points_recommendations(user_id, user_profile)
            recommendations.extend(points_recs)
            
            # 免息期推荐
            grace_period_recs = self._generate_grace_period_recommendations(user_id, user_profile)
            recommendations.extend(grace_period_recs)
            
            # 额度优化推荐
            limit_recs = self._generate_limit_optimization_recommendations(user_id, user_profile)
            recommendations.extend(limit_recs)
            
            # 年费优化推荐
            fee_recs = self._generate_fee_optimization_recommendations(user_id, user_profile)
            recommendations.extend(fee_recs)
            
            # 4. 保存推荐到数据库
            saved_recs = []
            for rec in recommendations:
                try:
                    saved_rec = self._save_recommendation(rec, user_id)
                    if saved_rec:
                        saved_recs.append(saved_rec)
                except Exception as e:
                    logger.warning(f"保存推荐失败: {str(e)}")
                    continue
            
            logger.info(f"成功生成 {len(saved_recs)} 条推荐")
            return saved_recs
            
        except Exception as e:
            logger.error(f"生成个性化推荐失败: {str(e)}")
            raise Exception(f"生成个性化推荐失败: {str(e)}")

    def submit_feedback(self, rec_id: UUID, user_id: UUID, feedback: str) -> bool:
        """
        提交推荐反馈
        
        Args:
            rec_id: 推荐ID
            user_id: 用户ID
            feedback: 反馈内容
            
        Returns:
            是否成功
        """
        try:
            recommendation = self.db.query(DBRecommendation).filter(
                DBRecommendation.id == rec_id,
                DBRecommendation.user_id == user_id,
                DBRecommendation.is_deleted == False
            ).first()
            
            if not recommendation:
                return False
            
            # 根据反馈更新推荐状态
            if feedback.lower() in ['applied', 'applied_card']:
                recommendation.status = RecommendationStatus.APPLIED
            elif feedback.lower() in ['rejected', 'not_interested']:
                recommendation.status = RecommendationStatus.REJECTED
            
            self.db.commit()
            logger.info(f"推荐反馈提交成功: rec_id={rec_id}, feedback={feedback}")
            return True
            
        except Exception as e:
            logger.error(f"提交推荐反馈失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"提交推荐反馈失败: {str(e)}")

    def _analyze_user_profile(self, user_id: UUID) -> Dict[str, Any]:
        """
        分析用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像数据
        """
        profile = {
            'total_cards': 0,
            'total_limit': Decimal('0'),
            'used_limit': Decimal('0'),
            'utilization_rate': Decimal('0'),
            'monthly_spending': Decimal('0'),
            'top_categories': [],
            'avg_transaction_amount': Decimal('0'),
            'has_high_fee_cards': False,
            'prefers_cashback': False,
            'prefers_points': False,
            'needs_higher_limit': False,
            'needs_longer_grace_period': False
        }
        
        try:
            # 统计信用卡情况
            cards = self.db.query(CreditCard).filter(
                CreditCard.user_id == user_id,
                CreditCard.is_deleted == False
            ).all()
            
            profile['total_cards'] = len(cards)
            profile['total_limit'] = sum(card.credit_limit or Decimal('0') for card in cards)
            profile['used_limit'] = sum(card.used_amount or Decimal('0') for card in cards)
            
            if profile['total_limit'] > 0:
                profile['utilization_rate'] = profile['used_limit'] / profile['total_limit'] * 100
            
            # 分析消费情况 (最近3个月)
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            transactions = self.db.query(Transaction).join(CreditCard).filter(
                CreditCard.user_id == user_id,
                Transaction.transaction_date >= three_months_ago,
                Transaction.is_deleted == False
            ).all()
            
            if transactions:
                total_spending = sum(t.amount for t in transactions if t.amount > 0)
                profile['monthly_spending'] = total_spending / 3
                profile['avg_transaction_amount'] = total_spending / len(transactions)
                
                # 分析消费类别
                category_spending = {}
                for t in transactions:
                    if t.amount > 0:  # 只统计支出
                        cat = t.category or TransactionCategory.OTHER
                        category_spending[cat] = category_spending.get(cat, Decimal('0')) + t.amount
                
                # 获取前3个消费类别
                profile['top_categories'] = sorted(
                    category_spending.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
            
            # 分析年费情况
            high_fee_cards = [card for card in cards if self._get_card_annual_fee(card.id) > 500]
            profile['has_high_fee_cards'] = len(high_fee_cards) > 0
            
            # 推断用户偏好
            profile['prefers_cashback'] = profile['monthly_spending'] > 5000
            profile['prefers_points'] = len(profile['top_categories']) >= 2
            profile['needs_higher_limit'] = profile['utilization_rate'] > 70
            profile['needs_longer_grace_period'] = profile['monthly_spending'] > 10000
            
            return profile
            
        except Exception as e:
            logger.error(f"分析用户画像失败: {str(e)}")
            return profile

    def _get_card_annual_fee(self, card_id: UUID) -> Decimal:
        """获取信用卡年费"""
        try:
            annual_fee_rule = self.db.query(AnnualFeeRule).filter(
                AnnualFeeRule.card_id == card_id,
                AnnualFeeRule.is_enabled == True,
                AnnualFeeRule.is_deleted == False
            ).first()
            
            return annual_fee_rule.base_fee if annual_fee_rule else Decimal('0')
        except:
            return Decimal('0')

    def _cleanup_expired_recommendations(self, user_id: UUID):
        """清理过期推荐"""
        try:
            self.db.query(DBRecommendation).filter(
                DBRecommendation.user_id == user_id,
                DBRecommendation.expires_at < datetime.utcnow(),
                DBRecommendation.status == RecommendationStatus.ACTIVE
            ).update({
                'status': RecommendationStatus.EXPIRED
            })
            self.db.commit()
        except Exception as e:
            logger.warning(f"清理过期推荐失败: {str(e)}")

    def _generate_cashback_recommendations(self, user_id: UUID, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成现金回馈推荐"""
        recommendations = []
        
        if profile['prefers_cashback'] and profile['monthly_spending'] > 3000:
            rec = {
                'bank_name': '招商银行',
                'card_name': '招商银行现金回馈信用卡',
                'recommendation_type': RecommendationType.CASHBACK,
                'title': '高现金回馈推荐',
                'description': f'基于您月均消费{profile["monthly_spending"]:.0f}元，推荐此高现金回馈信用卡',
                'features': ['餐饮消费5%回馈', '超市购物3%回馈', '加油2%回馈', '其他消费1%回馈'],
                'annual_fee': Decimal('200'),
                'credit_limit_range': '1万-50万',
                'approval_difficulty': 3,
                'recommendation_score': min(95, 80 + int(profile['monthly_spending'] / 1000)),
                'match_reasons': [
                    f'月均消费{profile["monthly_spending"]:.0f}元，适合现金回馈卡',
                    '消费类别多样，现金回馈更灵活',
                    '高消费频次用户'
                ],
                'pros': ['回馈率高', '使用灵活', '无类别限制'],
                'cons': ['年费200元', '需达到消费门槛'],
                'apply_url': 'https://creditcard.cmbchina.com/apply',
                'is_featured': profile['monthly_spending'] > 8000
            }
            recommendations.append(rec)
        
        return recommendations

    def _generate_points_recommendations(self, user_id: UUID, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成积分奖励推荐"""
        recommendations = []
        
        if profile['prefers_points'] and len(profile['top_categories']) >= 2:
            top_category = profile['top_categories'][0][0] if profile['top_categories'] else TransactionCategory.OTHER
            
            rec = {
                'bank_name': '中信银行',
                'card_name': '中信银行积分达人卡',
                'recommendation_type': RecommendationType.POINTS,
                'title': '积分奖励优化推荐',
                'description': f'根据您的{top_category.value}等消费习惯，推荐此积分奖励卡',
                'features': ['餐饮10倍积分', '超市5倍积分', '网购3倍积分', '其他消费1倍积分'],
                'annual_fee': Decimal('300'),
                'credit_limit_range': '2万-30万',
                'approval_difficulty': 2,
                'recommendation_score': 88,
                'match_reasons': [
                    f'主要消费类别：{top_category.value}',
                    '多类别消费，积分回报丰厚',
                    '积分兑换选择多样'
                ],
                'pros': ['积分倍率高', '兑换渠道多', '积分有效期长'],
                'cons': ['兑换门槛高', '部分商户不参与'],
                'apply_url': 'https://creditcard.citicbank.com/apply',
                'is_featured': False
            }
            recommendations.append(rec)
        
        return recommendations

    def _generate_grace_period_recommendations(self, user_id: UUID, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成免息期推荐"""
        recommendations = []
        
        if profile['needs_longer_grace_period']:
            rec = {
                'bank_name': '光大银行',
                'card_name': '光大银行长免息期信用卡',
                'recommendation_type': RecommendationType.CASHBACK,  # 免息期属于现金价值
                'title': '超长免息期推荐',
                'description': f'您的高消费水平({profile["monthly_spending"]:.0f}元/月)需要更长的资金周转期',
                'features': ['最长56天免息期', '账单日可调整', '支持分期付款', '紧急取现服务'],
                'annual_fee': Decimal('0'),
                'credit_limit_range': '5万-100万',
                'approval_difficulty': 3,
                'recommendation_score': 85,
                'match_reasons': [
                    f'月消费{profile["monthly_spending"]:.0f}元，需要长免息期',
                    '高额度使用率，资金周转需求大',
                    '免年费政策降低持卡成本'
                ],
                'pros': ['免息期最长', '免年费', '额度高', '还款灵活'],
                'cons': ['申请门槛较高', '部分功能有限制'],
                'apply_url': 'https://creditcard.cebbank.com/apply',
                'is_featured': profile['monthly_spending'] > 15000
            }
            recommendations.append(rec)
        
        return recommendations

    def _generate_limit_optimization_recommendations(self, user_id: UUID, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成额度优化推荐"""
        recommendations = []
        
        if profile['needs_higher_limit']:
            rec = {
                'bank_name': '建设银行',
                'card_name': '建设银行高额度白金卡',
                'recommendation_type': RecommendationType.CASHBACK,
                'title': '额度提升推荐',
                'description': f'您的额度使用率{profile["utilization_rate"]:.1f}%较高，建议增加可用额度',
                'features': ['起始额度高', '快速提额', '临时额度便利', '全球通用'],
                'annual_fee': Decimal('480'),
                'credit_limit_range': '10万-500万',
                'approval_difficulty': 4,
                'recommendation_score': 82,
                'match_reasons': [
                    f'当前额度使用率{profile["utilization_rate"]:.1f}%',
                    '需要更多可用额度',
                    '信用记录良好，适合高额度卡'
                ],
                'pros': ['额度起点高', '提额速度快', '服务优质'],
                'cons': ['年费较高', '申请要求严格'],
                'apply_url': 'https://creditcard.ccb.com/apply',
                'is_featured': profile['utilization_rate'] > 85
            }
            recommendations.append(rec)
        
        return recommendations

    def _generate_fee_optimization_recommendations(self, user_id: UUID, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成年费优化推荐"""
        recommendations = []
        
        if profile['has_high_fee_cards'] and profile['monthly_spending'] < 5000:
            rec = {
                'bank_name': '平安银行',
                'card_name': '平安银行免年费标准卡',
                'recommendation_type': RecommendationType.CASHBACK,
                'title': '年费优化推荐',
                'description': f'您的月消费{profile["monthly_spending"]:.0f}元，建议选择免年费卡片降低成本',
                'features': ['终身免年费', '基础权益齐全', '积分不过期', '还款方式多样'],
                'annual_fee': Decimal('0'),
                'credit_limit_range': '5千-20万',
                'approval_difficulty': 1,
                'recommendation_score': 75,
                'match_reasons': [
                    f'当前持有高年费卡片但消费较少',
                    '免年费可节省成本',
                    '基础功能满足日常需求'
                ],
                'pros': ['完全免费', '申请简单', '功能实用'],
                'cons': ['额度相对较低', '权益较基础'],
                'apply_url': 'https://creditcard.pingan.com/apply',
                'is_featured': False
            }
            recommendations.append(rec)
        
        return recommendations

    def _save_recommendation(self, rec_data: Dict[str, Any], user_id: UUID) -> Optional[Recommendation]:
        """保存推荐到数据库"""
        try:
            # 检查是否已存在相同推荐
            existing = self.db.query(DBRecommendation).filter(
                DBRecommendation.user_id == user_id,
                DBRecommendation.card_name == rec_data['card_name'],
                DBRecommendation.status == RecommendationStatus.ACTIVE,
                DBRecommendation.is_deleted == False
            ).first()
            
            if existing:
                logger.info(f"推荐已存在，跳过: {rec_data['card_name']}")
                return None
            
            # 创建新推荐
            db_rec = DBRecommendation(
                user_id=user_id,
                bank_name=rec_data['bank_name'],
                card_name=rec_data['card_name'],
                recommendation_type=rec_data['recommendation_type'],
                title=rec_data['title'],
                description=rec_data['description'],
                features=rec_data['features'],
                annual_fee=rec_data['annual_fee'],
                credit_limit_range=rec_data['credit_limit_range'],
                approval_difficulty=rec_data['approval_difficulty'],
                recommendation_score=rec_data['recommendation_score'],
                match_reasons=rec_data['match_reasons'],
                pros=rec_data['pros'],
                cons=rec_data['cons'],
                apply_url=rec_data.get('apply_url'),
                is_featured=rec_data.get('is_featured', False),
                expires_at=datetime.utcnow() + timedelta(days=30),  # 30天后过期
                status=RecommendationStatus.ACTIVE
            )
            
            self.db.add(db_rec)
            self.db.commit()
            self.db.refresh(db_rec)
            
            return Recommendation.model_validate(db_rec)
            
        except Exception as e:
            logger.error(f"保存推荐失败: {str(e)}")
            self.db.rollback()
            return None