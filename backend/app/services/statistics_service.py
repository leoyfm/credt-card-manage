"""
统计分析服务层

包含仪表板数据、趋势分析、财务报告等功能。
新架构下的统计分析服务。
"""

import logging
from datetime import datetime, date, timedelta, UTC
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, extract, desc, case
from sqlalchemy.orm import Session

from app.models.schemas.statistics import (
    DashboardData,
    OverviewStats,
    TrendAnalysis,
    ComparisonData,
    FinancialReport,
    HealthAssessment,
    PeriodType,
    MetricType
)
from app.models.database.card import CreditCard as DBCard
from app.models.database.transaction import Transaction as DBTransaction
from app.models.database.annual_fee import AnnualFeeRecord as DBFeeRecord
from app.models.database.reminder import ReminderRecord as DBReminderRecord
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class StatisticsService:
    """统计分析服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 仪表板数据 ====================

    def get_dashboard_data(self, user_id: UUID) -> DashboardData:
        """获取仪表板数据"""
        try:
            logger.info(f"获取用户仪表板数据", extra={"user_id": str(user_id)})
            
            # 获取基础统计
            overview_stats = self.get_overview_stats(user_id)
            
            # 获取最近趋势
            recent_trend = self.get_trend_analysis(user_id, PeriodType.LAST_30_DAYS)
            
            # 获取健康评估
            health_assessment = self.get_financial_health(user_id)
            
            # 获取待处理事项
            pending_items = self._get_pending_items(user_id)
            
            # 获取最近交易
            recent_transactions = self._get_recent_transactions(user_id, limit=10)
            
            # 获取卡片概览
            cards_overview = self._get_cards_overview(user_id)
            
            return DashboardData(
                overview_stats=overview_stats,
                recent_trend=recent_trend,
                health_assessment=health_assessment,
                pending_items=pending_items,
                recent_transactions=recent_transactions,
                cards_overview=cards_overview,
                last_updated=datetime.now(UTC)
            )
            
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {str(e)}")
            raise

    def get_overview_stats(self, user_id: UUID) -> OverviewStats:
        """获取概览统计"""
        try:
            # 获取信用卡统计
            cards_stats = self.db.query(
                func.count(DBCard.id).label('total_cards'),
                func.sum(DBCard.credit_limit).label('total_limit'),
                func.sum(DBCard.annual_fee).label('total_annual_fee')
            ).filter(DBCard.user_id == user_id).first()
            
            # 获取本月交易统计
            current_month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_stats = self.db.query(
                func.count(DBTransaction.id).label('transaction_count'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'expense', DBTransaction.amount),
                    else_=0
                )).label('total_spending'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'income', DBTransaction.amount),
                    else_=0
                )).label('total_income')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= current_month_start
                )
            ).first()
            
            # 获取年费统计
            current_year = datetime.now().year
            annual_fee_stats = self.db.query(
                func.sum(DBFeeRecord.actual_fee).label('paid_annual_fees'),
                func.sum(DBFeeRecord.waiver_amount).label('waived_amount')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBFeeRecord.fee_year == current_year
                )
            ).first()
            
            # 计算利用率
            avg_utilization = self._calculate_average_utilization(user_id)
            
            return OverviewStats(
                total_cards=cards_stats.total_cards or 0,
                total_credit_limit=cards_stats.total_limit or Decimal("0"),
                monthly_spending=monthly_stats.total_spending or Decimal("0"),
                monthly_income=monthly_stats.total_income or Decimal("0"),
                monthly_transactions=monthly_stats.transaction_count or 0,
                annual_fees_paid=annual_fee_stats.paid_annual_fees or Decimal("0"),
                annual_fees_waived=annual_fee_stats.waived_amount or Decimal("0"),
                average_utilization=avg_utilization,
                net_monthly_flow=(monthly_stats.total_income or Decimal("0")) - (monthly_stats.total_spending or Decimal("0"))
            )
            
        except Exception as e:
            logger.error(f"获取概览统计失败: {str(e)}")
            raise

    def get_trend_analysis(
        self, 
        user_id: UUID, 
        period: PeriodType,
        metric_type: Optional[MetricType] = None
    ) -> TrendAnalysis:
        """获取趋势分析"""
        try:
            logger.info(f"获取趋势分析", extra={
                "user_id": str(user_id),
                "period": period.value
            })
            
            # 计算时间范围
            end_date = datetime.now(UTC)
            
            if period == PeriodType.LAST_7_DAYS:
                start_date = end_date - timedelta(days=7)
                group_by_format = 'day'
            elif period == PeriodType.LAST_30_DAYS:
                start_date = end_date - timedelta(days=30)
                group_by_format = 'day'
            elif period == PeriodType.LAST_3_MONTHS:
                start_date = end_date - timedelta(days=90)
                group_by_format = 'week'
            elif period == PeriodType.LAST_6_MONTHS:
                start_date = end_date - timedelta(days=180)
                group_by_format = 'month'
            else:  # LAST_12_MONTHS
                start_date = end_date - timedelta(days=365)
                group_by_format = 'month'
            
            # 获取趋势数据
            if group_by_format == 'day':
                trend_data = self._get_daily_trend(user_id, start_date, end_date)
            elif group_by_format == 'week':
                trend_data = self._get_weekly_trend(user_id, start_date, end_date)
            else:  # month
                trend_data = self._get_monthly_trend(user_id, start_date, end_date)
            
            # 计算增长率
            if len(trend_data) >= 2:
                latest_value = trend_data[-1].get('spending', 0)
                previous_value = trend_data[-2].get('spending', 0)
                
                if previous_value > 0:
                    growth_rate = ((latest_value - previous_value) / previous_value) * 100
                else:
                    growth_rate = 0.0
            else:
                growth_rate = 0.0
            
            return TrendAnalysis(
                period=period,
                trend_data=trend_data,
                growth_rate=growth_rate,
                average_value=sum(item.get('spending', 0) for item in trend_data) / len(trend_data) if trend_data else 0,
                peak_value=max(item.get('spending', 0) for item in trend_data) if trend_data else 0,
                low_value=min(item.get('spending', 0) for item in trend_data) if trend_data else 0
            )
            
        except Exception as e:
            logger.error(f"获取趋势分析失败: {str(e)}")
            raise

    def get_comparison_data(
        self,
        user_id: UUID,
        comparison_type: str,
        period1: Dict[str, Any],
        period2: Dict[str, Any]
    ) -> ComparisonData:
        """获取对比数据"""
        try:
            logger.info(f"获取对比数据", extra={
                "user_id": str(user_id),
                "comparison_type": comparison_type
            })
            
            # 获取两个时期的数据
            period1_data = self._get_period_stats(user_id, period1['start'], period1['end'])
            period2_data = self._get_period_stats(user_id, period2['start'], period2['end'])
            
            # 计算变化
            changes = {}
            for key in period1_data:
                if key in period2_data:
                    if period2_data[key] != 0:
                        change_percent = ((period1_data[key] - period2_data[key]) / period2_data[key]) * 100
                    else:
                        change_percent = 0.0
                    
                    changes[key] = {
                        'absolute_change': period1_data[key] - period2_data[key],
                        'percent_change': change_percent,
                        'is_improvement': self._is_improvement(key, change_percent)
                    }
            
            return ComparisonData(
                comparison_type=comparison_type,
                period1_data=period1_data,
                period2_data=period2_data,
                changes=changes,
                summary=self._generate_comparison_summary(changes)
            )
            
        except Exception as e:
            logger.error(f"获取对比数据失败: {str(e)}")
            raise

    def get_financial_report(
        self,
        user_id: UUID,
        report_type: str,
        start_date: date,
        end_date: date
    ) -> FinancialReport:
        """获取财务报告"""
        try:
            logger.info(f"生成财务报告", extra={
                "user_id": str(user_id),
                "report_type": report_type,
                "period": f"{start_date} to {end_date}"
            })
            
            # 获取收支数据
            income_expenses = self._get_income_expenses_breakdown(user_id, start_date, end_date)
            
            # 获取分类统计
            category_breakdown = self._get_category_breakdown(user_id, start_date, end_date)
            
            # 获取卡片使用统计
            card_usage = self._get_card_usage_breakdown(user_id, start_date, end_date)
            
            # 获取年费统计
            annual_fee_summary = self._get_annual_fee_summary(user_id, start_date, end_date)
            
            # 计算关键指标
            key_metrics = self._calculate_key_metrics(user_id, start_date, end_date)
            
            return FinancialReport(
                report_type=report_type,
                period_start=start_date,
                period_end=end_date,
                income_expenses=income_expenses,
                category_breakdown=category_breakdown,
                card_usage=card_usage,
                annual_fee_summary=annual_fee_summary,
                key_metrics=key_metrics,
                generated_at=datetime.now(UTC)
            )
            
        except Exception as e:
            logger.error(f"生成财务报告失败: {str(e)}")
            raise

    def get_financial_health(self, user_id: UUID) -> HealthAssessment:
        """获取财务健康评估"""
        try:
            logger.info(f"评估财务健康状况", extra={"user_id": str(user_id)})
            
            # 计算各项健康指标
            utilization_score = self._calculate_utilization_health(user_id)
            payment_score = self._calculate_payment_health(user_id)
            diversity_score = self._calculate_portfolio_diversity(user_id)
            cost_efficiency_score = self._calculate_cost_efficiency(user_id)
            
            # 计算综合评分
            overall_score = (utilization_score + payment_score + diversity_score + cost_efficiency_score) / 4
            
            # 生成建议
            recommendations = self._generate_health_recommendations(
                utilization_score, payment_score, diversity_score, cost_efficiency_score
            )
            
            # 确定健康等级
            if overall_score >= 80:
                health_level = "excellent"
            elif overall_score >= 60:
                health_level = "good"
            elif overall_score >= 40:
                health_level = "fair"
            else:
                health_level = "poor"
            
            return HealthAssessment(
                overall_score=overall_score,
                health_level=health_level,
                utilization_health=utilization_score,
                payment_health=payment_score,
                portfolio_diversity=diversity_score,
                cost_efficiency=cost_efficiency_score,
                recommendations=recommendations,
                risk_factors=self._identify_risk_factors(user_id),
                assessed_at=datetime.now(UTC)
            )
            
        except Exception as e:
            logger.error(f"财务健康评估失败: {str(e)}")
            raise

    # ==================== 辅助方法 ====================

    def _get_pending_items(self, user_id: UUID) -> List[Dict[str, Any]]:
        """获取待处理事项"""
        try:
            pending_items = []
            
            # 检查即将到期的还款
            upcoming_payments = self.db.query(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBCard.due_date <= date.today() + timedelta(days=7),
                    DBCard.due_date >= date.today()
                )
            ).all()
            
            for card in upcoming_payments:
                pending_items.append({
                    'type': 'payment_due',
                    'title': f'{card.card_name} 即将到期',
                    'description': f'还款日: {card.due_date}',
                    'priority': 'high',
                    'due_date': card.due_date
                })
            
            # 检查待处理的提醒
            pending_reminders = self.db.query(DBReminderRecord).join(
                DBReminderRecord.setting
            ).filter(
                and_(
                    DBReminderRecord.setting.has(user_id=user_id),
                    DBReminderRecord.status == 'pending',
                    DBReminderRecord.reminder_date <= datetime.now(UTC) + timedelta(days=1)
                )
            ).limit(5).all()
            
            for reminder in pending_reminders:
                pending_items.append({
                    'type': 'reminder',
                    'title': '待处理提醒',
                    'description': reminder.message,
                    'priority': 'medium',
                    'due_date': reminder.reminder_date.date()
                })
            
            return sorted(pending_items, key=lambda x: x['due_date'])
            
        except Exception as e:
            logger.error(f"获取待处理事项失败: {str(e)}")
            return []

    def _get_recent_transactions(self, user_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近交易"""
        try:
            transactions = self.db.query(DBTransaction).join(DBCard).filter(
                DBCard.user_id == user_id
            ).order_by(desc(DBTransaction.transaction_date)).limit(limit).all()
            
            return [
                {
                    'id': str(transaction.id),
                    'amount': float(transaction.amount),
                    'description': transaction.description,
                    'category': transaction.category,
                    'transaction_date': transaction.transaction_date,
                    'transaction_type': transaction.transaction_type,
                    'card_name': transaction.card.card_name if transaction.card else None
                }
                for transaction in transactions
            ]
            
        except Exception as e:
            logger.error(f"获取最近交易失败: {str(e)}")
            return []

    def _get_cards_overview(self, user_id: UUID) -> List[Dict[str, Any]]:
        """获取卡片概览"""
        try:
            cards = self.db.query(DBCard).filter(DBCard.user_id == user_id).all()
            
            cards_overview = []
            for card in cards:
                # 计算本月消费
                current_month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                monthly_spending = self.db.query(
                    func.sum(DBTransaction.amount)
                ).filter(
                    and_(
                        DBTransaction.card_id == card.id,
                        DBTransaction.transaction_type == 'expense',
                        DBTransaction.transaction_date >= current_month_start
                    )
                ).scalar() or Decimal("0")
                
                # 计算利用率
                utilization = 0.0
                if card.credit_limit and card.credit_limit > 0:
                    utilization = float(monthly_spending) / float(card.credit_limit) * 100
                
                cards_overview.append({
                    'id': str(card.id),
                    'card_name': card.card_name,
                    'bank_name': card.bank_name,
                    'credit_limit': float(card.credit_limit) if card.credit_limit else 0,
                    'monthly_spending': float(monthly_spending),
                    'utilization_rate': utilization,
                    'due_date': card.due_date,
                    'status': card.status
                })
            
            return cards_overview
            
        except Exception as e:
            logger.error(f"获取卡片概览失败: {str(e)}")
            return []

    def _calculate_average_utilization(self, user_id: UUID) -> float:
        """计算平均利用率"""
        try:
            cards = self.db.query(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBCard.credit_limit > 0
                )
            ).all()
            
            if not cards:
                return 0.0
            
            total_utilization = 0.0
            valid_cards = 0
            
            for card in cards:
                # 计算最近30天的平均消费
                thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
                monthly_spending = self.db.query(
                    func.sum(DBTransaction.amount)
                ).filter(
                    and_(
                        DBTransaction.card_id == card.id,
                        DBTransaction.transaction_type == 'expense',
                        DBTransaction.transaction_date >= thirty_days_ago
                    )
                ).scalar() or Decimal("0")
                
                if card.credit_limit > 0:
                    utilization = float(monthly_spending) / float(card.credit_limit)
                    total_utilization += utilization
                    valid_cards += 1
            
            return (total_utilization / valid_cards * 100) if valid_cards > 0 else 0.0
            
        except Exception as e:
            logger.error(f"计算平均利用率失败: {str(e)}")
            return 0.0

    def _get_daily_trend(self, user_id: UUID, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取每日趋势"""
        try:
            daily_stats = self.db.query(
                func.date(DBTransaction.transaction_date).label('date'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'expense', DBTransaction.amount),
                    else_=0
                )).label('spending'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'income', DBTransaction.amount),
                    else_=0
                )).label('income'),
                func.count(DBTransaction.id).label('transaction_count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= start_date,
                    DBTransaction.transaction_date <= end_date
                )
            ).group_by(func.date(DBTransaction.transaction_date)).order_by('date').all()
            
            return [
                {
                    'date': stat.date.isoformat(),
                    'spending': float(stat.spending) if stat.spending else 0.0,
                    'income': float(stat.income) if stat.income else 0.0,
                    'transaction_count': stat.transaction_count
                }
                for stat in daily_stats
            ]
            
        except Exception as e:
            logger.error(f"获取每日趋势失败: {str(e)}")
            return []

    def _get_weekly_trend(self, user_id: UUID, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取每周趋势"""
        try:
            weekly_stats = self.db.query(
                func.date_trunc('week', DBTransaction.transaction_date).label('week'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'expense', DBTransaction.amount),
                    else_=0
                )).label('spending'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'income', DBTransaction.amount),
                    else_=0
                )).label('income'),
                func.count(DBTransaction.id).label('transaction_count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= start_date,
                    DBTransaction.transaction_date <= end_date
                )
            ).group_by(func.date_trunc('week', DBTransaction.transaction_date)).order_by('week').all()
            
            return [
                {
                    'date': stat.week.isoformat(),
                    'spending': float(stat.spending) if stat.spending else 0.0,
                    'income': float(stat.income) if stat.income else 0.0,
                    'transaction_count': stat.transaction_count
                }
                for stat in weekly_stats
            ]
            
        except Exception as e:
            logger.error(f"获取每周趋势失败: {str(e)}")
            return []

    def _get_monthly_trend(self, user_id: UUID, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """获取每月趋势"""
        try:
            monthly_stats = self.db.query(
                func.date_trunc('month', DBTransaction.transaction_date).label('month'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'expense', DBTransaction.amount),
                    else_=0
                )).label('spending'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'income', DBTransaction.amount),
                    else_=0
                )).label('income'),
                func.count(DBTransaction.id).label('transaction_count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= start_date,
                    DBTransaction.transaction_date <= end_date
                )
            ).group_by(func.date_trunc('month', DBTransaction.transaction_date)).order_by('month').all()
            
            return [
                {
                    'date': stat.month.isoformat(),
                    'spending': float(stat.spending) if stat.spending else 0.0,
                    'income': float(stat.income) if stat.income else 0.0,
                    'transaction_count': stat.transaction_count
                }
                for stat in monthly_stats
            ]
            
        except Exception as e:
            logger.error(f"获取每月趋势失败: {str(e)}")
            return []

    def _calculate_utilization_health(self, user_id: UUID) -> float:
        """计算利用率健康评分"""
        try:
            avg_utilization = self._calculate_average_utilization(user_id)
            
            # 理想利用率在10-30%之间
            if 10 <= avg_utilization <= 30:
                return 100.0
            elif avg_utilization < 10:
                return max(50.0, avg_utilization * 5)  # 使用率过低
            elif avg_utilization <= 50:
                return 100 - (avg_utilization - 30) * 2  # 适度下降
            else:
                return max(0.0, 60 - (avg_utilization - 50))  # 利用率过高
                
        except Exception as e:
            logger.error(f"计算利用率健康评分失败: {str(e)}")
            return 50.0

    def _calculate_payment_health(self, user_id: UUID) -> float:
        """计算还款健康评分"""
        try:
            # 检查最近6个月的还款记录
            six_months_ago = datetime.now(UTC) - timedelta(days=180)
            
            # 简化评分：假设用户按时还款
            # 实际实现中需要查询还款记录
            return 85.0
            
        except Exception as e:
            logger.error(f"计算还款健康评分失败: {str(e)}")
            return 50.0

    def _calculate_portfolio_diversity(self, user_id: UUID) -> float:
        """计算投资组合多样性评分"""
        try:
            cards = self.db.query(DBCard).filter(DBCard.user_id == user_id).all()
            
            if not cards:
                return 0.0
            
            # 评估卡片多样性
            card_count = len(cards)
            bank_count = len(set(card.bank_name for card in cards))
            
            # 基础评分
            base_score = min(card_count * 20, 60)  # 最多3张卡60分
            
            # 银行多样性加分
            diversity_bonus = min(bank_count * 10, 40)  # 最多4家银行40分
            
            return min(base_score + diversity_bonus, 100.0)
            
        except Exception as e:
            logger.error(f"计算投资组合多样性评分失败: {str(e)}")
            return 50.0

    def _calculate_cost_efficiency(self, user_id: UUID) -> float:
        """计算成本效率评分"""
        try:
            current_year = datetime.now().year
            
            # 获取年费支出
            annual_fees = self.db.query(
                func.sum(DBFeeRecord.actual_fee)
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBFeeRecord.fee_year == current_year
                )
            ).scalar() or Decimal("0")
            
            # 获取年度消费
            year_start = datetime(current_year, 1, 1)
            annual_spending = self.db.query(
                func.sum(DBTransaction.amount)
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_type == 'expense',
                    DBTransaction.transaction_date >= year_start
                )
            ).scalar() or Decimal("0")
            
            if annual_spending == 0:
                return 50.0
            
            # 计算年费率（年费/年消费）
            fee_rate = float(annual_fees) / float(annual_spending) * 100
            
            # 评分：年费率越低越好
            if fee_rate <= 0.5:  # 年费率0.5%以下为优秀
                return 100.0
            elif fee_rate <= 1.0:  # 1%以下为良好
                return 80.0
            elif fee_rate <= 2.0:  # 2%以下为一般
                return 60.0
            else:  # 超过2%为较差
                return max(20.0, 60 - (fee_rate - 2) * 10)
                
        except Exception as e:
            logger.error(f"计算成本效率评分失败: {str(e)}")
            return 50.0

    def _generate_health_recommendations(
        self, 
        utilization_score: float, 
        payment_score: float, 
        diversity_score: float, 
        cost_score: float
    ) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        if utilization_score < 60:
            if utilization_score < 30:
                recommendations.append("建议适度增加信用卡使用频率，保持活跃的信用记录")
            else:
                recommendations.append("注意控制信用卡利用率，建议保持在30%以下")
        
        if payment_score < 70:
            recommendations.append("建议设置自动还款，确保按时还款维护信用记录")
        
        if diversity_score < 50:
            recommendations.append("考虑适当增加信用卡数量或选择不同银行的产品")
        
        if cost_score < 60:
            recommendations.append("评估年费支出合理性，考虑优化信用卡组合降低成本")
        
        if not recommendations:
            recommendations.append("您的信用卡使用状况良好，请继续保持")
        
        return recommendations

    def _identify_risk_factors(self, user_id: UUID) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        try:
            # 检查高利用率卡片
            avg_utilization = self._calculate_average_utilization(user_id)
            if avg_utilization > 80:
                risk_factors.append("信用卡利用率过高，存在逾期风险")
            
            # 检查即将到期的还款
            upcoming_payments = self.db.query(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBCard.due_date <= date.today() + timedelta(days=3),
                    DBCard.due_date >= date.today()
                )
            ).count()
            
            if upcoming_payments > 0:
                risk_factors.append(f"有{upcoming_payments}张信用卡即将到达还款日")
            
            # 检查高年费支出
            current_year = datetime.now().year
            annual_fees = self.db.query(
                func.sum(DBFeeRecord.actual_fee)
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBFeeRecord.fee_year == current_year
                )
            ).scalar() or Decimal("0")
            
            if annual_fees > 2000:
                risk_factors.append("年费支出较高，建议评估卡片性价比")
                
        except Exception as e:
            logger.error(f"识别风险因素失败: {str(e)}")
        
        return risk_factors

    def _get_period_stats(self, user_id: UUID, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """获取时期统计数据"""
        try:
            stats = self.db.query(
                func.sum(case(
                    (DBTransaction.transaction_type == 'expense', DBTransaction.amount),
                    else_=0
                )).label('total_spending'),
                func.sum(case(
                    (DBTransaction.transaction_type == 'income', DBTransaction.amount),
                    else_=0
                )).label('total_income'),
                func.count(DBTransaction.id).label('transaction_count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= start_date,
                    DBTransaction.transaction_date <= end_date
                )
            ).first()
            
            return {
                'total_spending': float(stats.total_spending) if stats.total_spending else 0.0,
                'total_income': float(stats.total_income) if stats.total_income else 0.0,
                'transaction_count': stats.transaction_count,
                'net_flow': float(stats.total_income or 0) - float(stats.total_spending or 0)
            }
            
        except Exception as e:
            logger.error(f"获取时期统计失败: {str(e)}")
            return {'total_spending': 0.0, 'total_income': 0.0, 'transaction_count': 0, 'net_flow': 0.0}

    def _is_improvement(self, metric: str, change_percent: float) -> bool:
        """判断变化是否为改善"""
        # 对于支出，减少是改善；对于收入，增加是改善
        if metric in ['total_spending']:
            return change_percent < 0
        elif metric in ['total_income']:
            return change_percent > 0
        else:
            return change_percent > 0

    def _generate_comparison_summary(self, changes: Dict[str, Any]) -> str:
        """生成对比总结"""
        improvements = []
        deteriorations = []
        
        for metric, change_data in changes.items():
            if change_data['is_improvement']:
                improvements.append(f"{metric}改善了{abs(change_data['percent_change']):.1f}%")
            else:
                deteriorations.append(f"{metric}恶化了{abs(change_data['percent_change']):.1f}%")
        
        summary_parts = []
        if improvements:
            summary_parts.append(f"改善: {', '.join(improvements)}")
        if deteriorations:
            summary_parts.append(f"需要关注: {', '.join(deteriorations)}")
        
        return "; ".join(summary_parts) if summary_parts else "整体表现平稳"

    def _get_income_expenses_breakdown(
        self, 
        user_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """获取收支明细"""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            breakdown = self.db.query(
                DBTransaction.transaction_type,
                func.sum(DBTransaction.amount).label('total_amount'),
                func.count(DBTransaction.id).label('count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= start_datetime,
                    DBTransaction.transaction_date <= end_datetime
                )
            ).group_by(DBTransaction.transaction_type).all()
            
            result = {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'income_count': 0,
                'expense_count': 0
            }
            
            for item in breakdown:
                if item.transaction_type == 'income':
                    result['total_income'] = float(item.total_amount)
                    result['income_count'] = item.count
                elif item.transaction_type == 'expense':
                    result['total_expenses'] = float(item.total_amount)
                    result['expense_count'] = item.count
            
            result['net_income'] = result['total_income'] - result['total_expenses']
            
            return result
            
        except Exception as e:
            logger.error(f"获取收支明细失败: {str(e)}")
            return {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'income_count': 0,
                'expense_count': 0,
                'net_income': 0.0
            }

    def _get_category_breakdown(
        self, 
        user_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """获取分类明细"""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            categories = self.db.query(
                DBTransaction.category,
                func.sum(DBTransaction.amount).label('total_amount'),
                func.count(DBTransaction.id).label('count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_type == 'expense',
                    DBTransaction.transaction_date >= start_datetime,
                    DBTransaction.transaction_date <= end_datetime
                )
            ).group_by(DBTransaction.category).order_by(
                desc('total_amount')
            ).all()
            
            return [
                {
                    'category': cat.category,
                    'amount': float(cat.total_amount),
                    'count': cat.count
                }
                for cat in categories
            ]
            
        except Exception as e:
            logger.error(f"获取分类明细失败: {str(e)}")
            return []

    def _get_card_usage_breakdown(
        self, 
        user_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """获取卡片使用明细"""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            card_usage = self.db.query(
                DBCard.card_name,
                DBCard.bank_name,
                func.sum(DBTransaction.amount).label('total_amount'),
                func.count(DBTransaction.id).label('count')
            ).join(DBTransaction).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBTransaction.transaction_date >= start_datetime,
                    DBTransaction.transaction_date <= end_datetime
                )
            ).group_by(DBCard.id, DBCard.card_name, DBCard.bank_name).order_by(
                desc('total_amount')
            ).all()
            
            return [
                {
                    'card_name': usage.card_name,
                    'bank_name': usage.bank_name,
                    'amount': float(usage.total_amount),
                    'count': usage.count
                }
                for usage in card_usage
            ]
            
        except Exception as e:
            logger.error(f"获取卡片使用明细失败: {str(e)}")
            return []

    def _get_annual_fee_summary(
        self, 
        user_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """获取年费汇总"""
        try:
            fee_summary = self.db.query(
                func.sum(DBFeeRecord.base_fee).label('total_base_fee'),
                func.sum(DBFeeRecord.actual_fee).label('total_actual_fee'),
                func.sum(DBFeeRecord.waiver_amount).label('total_waiver'),
                func.count(DBFeeRecord.id).label('fee_count')
            ).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBFeeRecord.created_at >= datetime.combine(start_date, datetime.min.time()),
                    DBFeeRecord.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            ).first()
            
            return {
                'total_base_fee': float(fee_summary.total_base_fee) if fee_summary.total_base_fee else 0.0,
                'total_actual_fee': float(fee_summary.total_actual_fee) if fee_summary.total_actual_fee else 0.0,
                'total_waiver': float(fee_summary.total_waiver) if fee_summary.total_waiver else 0.0,
                'fee_count': fee_summary.fee_count or 0
            }
            
        except Exception as e:
            logger.error(f"获取年费汇总失败: {str(e)}")
            return {
                'total_base_fee': 0.0,
                'total_actual_fee': 0.0,
                'total_waiver': 0.0,
                'fee_count': 0
            }

    def _calculate_key_metrics(
        self, 
        user_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, float]:
        """计算关键指标"""
        try:
            # 获取基础数据
            income_expenses = self._get_income_expenses_breakdown(user_id, start_date, end_date)
            
            # 计算储蓄率
            if income_expenses['total_income'] > 0:
                savings_rate = (income_expenses['net_income'] / income_expenses['total_income']) * 100
            else:
                savings_rate = 0.0
            
            # 计算平均交易金额
            total_transactions = income_expenses['income_count'] + income_expenses['expense_count']
            if total_transactions > 0:
                avg_transaction = (income_expenses['total_income'] + income_expenses['total_expenses']) / total_transactions
            else:
                avg_transaction = 0.0
            
            # 计算支出增长率（与上期对比）
            period_days = (end_date - start_date).days
            previous_start = start_date - timedelta(days=period_days)
            previous_end = start_date - timedelta(days=1)
            
            previous_data = self._get_income_expenses_breakdown(user_id, previous_start, previous_end)
            
            if previous_data['total_expenses'] > 0:
                expense_growth = ((income_expenses['total_expenses'] - previous_data['total_expenses']) / 
                                previous_data['total_expenses']) * 100
            else:
                expense_growth = 0.0
            
            return {
                'savings_rate': savings_rate,
                'avg_transaction_amount': avg_transaction,
                'expense_growth_rate': expense_growth,
                'daily_avg_spending': income_expenses['total_expenses'] / period_days if period_days > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"计算关键指标失败: {str(e)}")
            return {
                'savings_rate': 0.0,
                'avg_transaction_amount': 0.0,
                'expense_growth_rate': 0.0,
                'daily_avg_spending': 0.0
            }