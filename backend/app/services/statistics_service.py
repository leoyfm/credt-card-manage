"""
统计服务
提供仪表板数据、趋势分析、财务报告等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
from uuid import UUID
import calendar

from app.models.database.card import CreditCard
from app.models.database.transaction import Transaction
from app.models.database.annual_fee import AnnualFeeRecord
from app.models.database.reminder import ReminderSetting, ReminderRecord
from app.core.exceptions.custom import (
    ResourceNotFoundError, ValidationError, BusinessRuleError
)
from app.core.logging.logger import app_logger as logger


class StatisticsService:
    """统计服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== 仪表板数据 ==========
    
    def get_dashboard_overview(self, user_id: UUID) -> Dict[str, Any]:
        """获取仪表板概览数据"""
        
        # 信用卡统计
        cards_stats = self._get_cards_overview(user_id)
        
        # 交易统计（最近30天）
        transactions_stats = self._get_transactions_overview(user_id)
        
        # 年费统计（当前年度）
        annual_fee_stats = self._get_annual_fee_overview(user_id)
        
        # 提醒统计
        reminders_stats = self._get_reminders_overview(user_id)
        
        # 财务健康评分
        health_score = self._calculate_financial_health_score(user_id)
        
        return {
            'cards': cards_stats,
            'transactions': transactions_stats,
            'annual_fees': annual_fee_stats,
            'reminders': reminders_stats,
            'health_score': health_score,
            'last_updated': datetime.now()
        }
    
    def get_monthly_trends(self, user_id: UUID, months: int = 12) -> Dict[str, Any]:
        """获取月度趋势分析"""
        
        # 计算查询范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # 查询月度交易数据
        monthly_data = self.db.query(
            extract('year', Transaction.transaction_date).label('year'),
            extract('month', Transaction.transaction_date).label('month'),
            Transaction.transaction_type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.sum(Transaction.points_earned).label('total_points'),
            func.sum(Transaction.cashback_earned).label('total_cashback')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date),
            Transaction.transaction_type
        ).order_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).all()
        
        # 组织数据
        monthly_trends = {}
        for data in monthly_data:
            key = f"{int(data.year)}-{int(data.month):02d}"
            if key not in monthly_trends:
                monthly_trends[key] = {
                    'year': int(data.year),
                    'month': int(data.month),
                    'month_name': calendar.month_name[int(data.month)],
                    'expense_count': 0,
                    'expense_amount': 0.0,
                    'income_count': 0,
                    'income_amount': 0.0,
                    'total_points': 0,
                    'total_cashback': 0.0,
                    'net_amount': 0.0
                }
            
            if data.transaction_type == 'expense':
                monthly_trends[key]['expense_count'] = data.count
                monthly_trends[key]['expense_amount'] = float(data.total_amount or 0)
                monthly_trends[key]['total_points'] += int(data.total_points or 0)
                monthly_trends[key]['total_cashback'] += float(data.total_cashback or 0)
            elif data.transaction_type in ['income', 'refund']:
                monthly_trends[key]['income_count'] += data.count
                monthly_trends[key]['income_amount'] += float(data.total_amount or 0)
        
        # 计算净额和趋势
        trends_list = list(monthly_trends.values())
        trends_list.sort(key=lambda x: (x['year'], x['month']))
        
        for trend in trends_list:
            trend['net_amount'] = trend['income_amount'] - trend['expense_amount']
        
        # 计算趋势指标
        trend_analysis = self._analyze_trends(trends_list)
        
        return {
            'analysis_period': f"{months}个月",
            'monthly_trends': trends_list,
            'trend_analysis': trend_analysis,
            'total_months': len(trends_list)
        }
    
    def get_spending_analysis(self, user_id: UUID, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """获取消费分析"""
        
        # 默认查询最近30天
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # 按分类统计
        category_stats = self.db.query(
            Transaction.category.has().label('category_name'),
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.avg(Transaction.amount).label('average_amount')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(Transaction.category_id).all()
        
        # 按信用卡统计
        card_stats = self.db.query(
            CreditCard.card_name,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.sum(Transaction.points_earned).label('total_points'),
            func.sum(Transaction.cashback_earned).label('total_cashback')
        ).join(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(CreditCard.id, CreditCard.card_name).all()
        
        # 按日期统计（每日消费）
        daily_stats = self.db.query(
            func.date(Transaction.transaction_date).label('date'),
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(func.date(Transaction.transaction_date))\
         .order_by(func.date(Transaction.transaction_date)).all()
        
        # 计算总支出
        total_expense = sum(stat.total_amount or 0 for stat in card_stats)
        
        # 构建分类分布
        category_distribution = []
        for stat in category_stats:
            amount = float(stat.total_amount or 0)
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            category_distribution.append({
                'category_name': stat.category_name or '未分类',
                'transaction_count': stat.transaction_count,
                'total_amount': amount,
                'average_amount': float(stat.average_amount or 0),
                'percentage': round(percentage, 2)
            })
        
        # 构建信用卡分布
        card_distribution = []
        for stat in card_stats:
            amount = float(stat.total_amount or 0)
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            card_distribution.append({
                'card_name': stat.card_name,
                'transaction_count': stat.transaction_count,
                'total_amount': amount,
                'total_points': int(stat.total_points or 0),
                'total_cashback': float(stat.total_cashback or 0),
                'percentage': round(percentage, 2)
            })
        
        # 构建每日趋势
        daily_trends = []
        for stat in daily_stats:
            daily_trends.append({
                'date': stat.date,
                'transaction_count': stat.transaction_count,
                'total_amount': float(stat.total_amount or 0)
            })
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'total_expense': float(total_expense),
            'category_distribution': sorted(category_distribution, key=lambda x: x['total_amount'], reverse=True),
            'card_distribution': sorted(card_distribution, key=lambda x: x['total_amount'], reverse=True),
            'daily_trends': daily_trends,
            'top_categories': category_distribution[:5],
            'top_cards': card_distribution[:3]
        }
    
    def get_financial_report(self, user_id: UUID, year: Optional[int] = None) -> Dict[str, Any]:
        """获取财务报告"""
        
        if not year:
            year = datetime.now().year
        
        # 年度交易统计
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)
        
        # 总体统计
        total_stats = self.db.query(
            func.count(Transaction.id).label('total_transactions'),
            func.sum(case(
                (Transaction.transaction_type == 'expense', Transaction.amount),
                else_=0
            )).label('total_expense'),
            func.sum(case(
                (Transaction.transaction_type.in_(['income', 'refund']), Transaction.amount),
                else_=0
            )).label('total_income'),
            func.sum(Transaction.points_earned).label('total_points'),
            func.sum(Transaction.cashback_earned).label('total_cashback')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= year_start,
                Transaction.transaction_date <= year_end
            )
        ).first()
        
        # 月度统计
        monthly_stats = self.db.query(
            extract('month', Transaction.transaction_date).label('month'),
            func.sum(case(
                (Transaction.transaction_type == 'expense', Transaction.amount),
                else_=0
            )).label('expense'),
            func.sum(case(
                (Transaction.transaction_type.in_(['income', 'refund']), Transaction.amount),
                else_=0
            )).label('income'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= year_start,
                Transaction.transaction_date <= year_end
            )
        ).group_by(extract('month', Transaction.transaction_date))\
         .order_by(extract('month', Transaction.transaction_date)).all()
        
        # 年费统计
        annual_fee_stats = self.db.query(
            func.count(AnnualFeeRecord.id).label('total_fees'),
            func.sum(AnnualFeeRecord.base_fee).label('total_base_fee'),
            func.sum(AnnualFeeRecord.actual_fee).label('total_actual_fee'),
            func.sum(AnnualFeeRecord.waiver_amount).label('total_waived')
        ).join(AnnualFeeRecord.rule).join(CreditCard).filter(
            and_(
                CreditCard.user_id == user_id,
                AnnualFeeRecord.fee_year == year
            )
        ).first()
        
        # 信用卡利用率统计
        card_utilization = self.db.query(
            CreditCard.card_name,
            CreditCard.credit_limit,
            CreditCard.used_limit,
            (CreditCard.used_limit * 100.0 / CreditCard.credit_limit).label('utilization_rate')
        ).filter(
            and_(
                CreditCard.user_id == user_id,
                CreditCard.status == 'active',
                CreditCard.credit_limit > 0
            )
        ).all()
        
        # 构建月度数据
        monthly_data = []
        for i in range(1, 13):
            month_stat = next((s for s in monthly_stats if s.month == i), None)
            monthly_data.append({
                'month': i,
                'month_name': calendar.month_name[i],
                'expense': float(month_stat.expense or 0) if month_stat else 0.0,
                'income': float(month_stat.income or 0) if month_stat else 0.0,
                'net_amount': float((month_stat.income or 0) - (month_stat.expense or 0)) if month_stat else 0.0,
                'transaction_count': month_stat.transaction_count if month_stat else 0
            })
        
        # 构建信用卡利用率数据
        utilization_data = []
        for card in card_utilization:
            utilization_data.append({
                'card_name': card.card_name,
                'credit_limit': float(card.credit_limit),
                'used_limit': float(card.used_limit),
                'utilization_rate': round(float(card.utilization_rate), 2),
                'available_limit': float(card.credit_limit - card.used_limit)
            })
        
        # 计算关键指标
        total_expense = float(total_stats.total_expense or 0)
        total_income = float(total_stats.total_income or 0)
        net_income = total_income - total_expense
        
        savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
        avg_monthly_expense = total_expense / 12
        avg_monthly_income = total_income / 12
        
        return {
            'year': year,
            'summary': {
                'total_transactions': total_stats.total_transactions,
                'total_expense': total_expense,
                'total_income': total_income,
                'net_income': net_income,
                'total_points': int(total_stats.total_points or 0),
                'total_cashback': float(total_stats.total_cashback or 0),
                'savings_rate': round(savings_rate, 2),
                'avg_monthly_expense': round(avg_monthly_expense, 2),
                'avg_monthly_income': round(avg_monthly_income, 2)
            },
            'monthly_data': monthly_data,
            'annual_fees': {
                'total_fees': annual_fee_stats.total_fees if annual_fee_stats else 0,
                'total_base_fee': float(annual_fee_stats.total_base_fee or 0) if annual_fee_stats else 0.0,
                'total_actual_fee': float(annual_fee_stats.total_actual_fee or 0) if annual_fee_stats else 0.0,
                'total_waived': float(annual_fee_stats.total_waived or 0) if annual_fee_stats else 0.0,
                'waiver_rate': round((float(annual_fee_stats.total_waived or 0) / float(annual_fee_stats.total_base_fee or 1) * 100), 2) if annual_fee_stats and annual_fee_stats.total_base_fee else 0.0
            },
            'card_utilization': utilization_data
        }
    
    # ========== 私有方法 ==========
    
    def _get_cards_overview(self, user_id: UUID) -> Dict[str, Any]:
        """获取信用卡概览"""
        
        cards_stats = self.db.query(
            func.count(CreditCard.id).label('total_cards'),
            func.sum(case(
                (CreditCard.status == 'active', 1),
                else_=0
            )).label('active_cards'),
            func.sum(CreditCard.credit_limit).label('total_credit_limit'),
            func.sum(CreditCard.used_limit).label('total_used_limit')
        ).filter(CreditCard.user_id == user_id).first()
        
        total_credit = float(cards_stats.total_credit_limit or 0)
        total_used = float(cards_stats.total_used_limit or 0)
        utilization_rate = (total_used / total_credit * 100) if total_credit > 0 else 0
        
        return {
            'total_cards': cards_stats.total_cards,
            'active_cards': cards_stats.active_cards,
            'total_credit_limit': total_credit,
            'total_used_limit': total_used,
            'available_limit': total_credit - total_used,
            'utilization_rate': round(utilization_rate, 2)
        }
    
    def _get_transactions_overview(self, user_id: UUID) -> Dict[str, Any]:
        """获取交易概览（最近30天）"""
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        transactions_stats = self.db.query(
            func.count(Transaction.id).label('total_transactions'),
            func.sum(case(
                (Transaction.transaction_type == 'expense', Transaction.amount),
                else_=0
            )).label('total_expense'),
            func.sum(case(
                (Transaction.transaction_type.in_(['income', 'refund']), Transaction.amount),
                else_=0
            )).label('total_income'),
            func.sum(Transaction.points_earned).label('total_points'),
            func.sum(Transaction.cashback_earned).label('total_cashback')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= thirty_days_ago
            )
        ).first()
        
        total_expense = float(transactions_stats.total_expense or 0)
        total_income = float(transactions_stats.total_income or 0)
        
        return {
            'total_transactions': transactions_stats.total_transactions,
            'total_expense': total_expense,
            'total_income': total_income,
            'net_amount': total_income - total_expense,
            'total_points': int(transactions_stats.total_points or 0),
            'total_cashback': float(transactions_stats.total_cashback or 0),
            'avg_daily_expense': round(total_expense / 30, 2)
        }
    
    def _get_annual_fee_overview(self, user_id: UUID) -> Dict[str, Any]:
        """获取年费概览（当前年度）"""
        
        current_year = datetime.now().year
        
        fee_stats = self.db.query(
            func.count(AnnualFeeRecord.id).label('total_fees'),
            func.sum(AnnualFeeRecord.base_fee).label('total_base_fee'),
            func.sum(AnnualFeeRecord.actual_fee).label('total_actual_fee'),
            func.sum(AnnualFeeRecord.waiver_amount).label('total_waived'),
            func.sum(case(
                (AnnualFeeRecord.status == 'pending', 1),
                else_=0
            )).label('pending_fees')
        ).join(AnnualFeeRecord.rule).join(CreditCard).filter(
            and_(
                CreditCard.user_id == user_id,
                AnnualFeeRecord.fee_year == current_year
            )
        ).first()
        
        if not fee_stats or fee_stats.total_fees == 0:
            return {
                'total_fees': 0,
                'total_base_fee': 0.0,
                'total_actual_fee': 0.0,
                'total_waived': 0.0,
                'pending_fees': 0,
                'waiver_rate': 0.0
            }
        
        total_base = float(fee_stats.total_base_fee or 0)
        total_waived = float(fee_stats.total_waived or 0)
        waiver_rate = (total_waived / total_base * 100) if total_base > 0 else 0
        
        return {
            'total_fees': fee_stats.total_fees,
            'total_base_fee': total_base,
            'total_actual_fee': float(fee_stats.total_actual_fee or 0),
            'total_waived': total_waived,
            'pending_fees': fee_stats.pending_fees,
            'waiver_rate': round(waiver_rate, 2)
        }
    
    def _get_reminders_overview(self, user_id: UUID) -> Dict[str, Any]:
        """获取提醒概览"""
        
        # 提醒设置统计
        settings_stats = self.db.query(
            func.count(ReminderSetting.id).label('total_settings'),
            func.sum(case(
                (ReminderSetting.is_enabled == True, 1),
                else_=0
            )).label('active_settings')
        ).filter(ReminderSetting.user_id == user_id).first()
        
        # 最近7天的提醒记录
        seven_days_ago = date.today() - timedelta(days=7)
        
        records_stats = self.db.query(
            func.count(ReminderRecord.id).label('total_reminders'),
            func.sum(case(
                (ReminderRecord.status == 'pending', 1),
                else_=0
            )).label('pending_reminders'),
            func.sum(case(
                (ReminderRecord.status == 'sent', 1),
                else_=0
            )).label('sent_reminders'),
            func.sum(case(
                (ReminderRecord.status == 'read', 1),
                else_=0
            )).label('read_reminders')
        ).join(ReminderSetting).filter(
            and_(
                ReminderSetting.user_id == user_id,
                ReminderRecord.reminder_date >= seven_days_ago
            )
        ).first()
        
        sent_count = records_stats.sent_reminders if records_stats else 0
        read_count = records_stats.read_reminders if records_stats else 0
        read_rate = (read_count / sent_count * 100) if sent_count > 0 else 0
        
        return {
            'total_settings': settings_stats.total_settings if settings_stats else 0,
            'active_settings': settings_stats.active_settings if settings_stats else 0,
            'total_reminders_7days': records_stats.total_reminders if records_stats else 0,
            'pending_reminders': records_stats.pending_reminders if records_stats else 0,
            'sent_reminders': sent_count,
            'read_reminders': read_count,
            'read_rate': round(read_rate, 2)
        }
    
    def _calculate_financial_health_score(self, user_id: UUID) -> Dict[str, Any]:
        """计算财务健康评分"""
        
        score = 100  # 基础分数
        factors = []
        
        # 信用卡利用率评分（30分）
        cards = self.db.query(CreditCard).filter(
            and_(
                CreditCard.user_id == user_id,
                CreditCard.status == 'active',
                CreditCard.credit_limit > 0
            )
        ).all()
        
        if cards:
            total_limit = sum(card.credit_limit for card in cards)
            total_used = sum(card.used_limit for card in cards)
            utilization_rate = total_used / total_limit * 100
            
            if utilization_rate <= 30:
                utilization_score = 30
                utilization_status = 'excellent'
            elif utilization_rate <= 50:
                utilization_score = 25
                utilization_status = 'good'
            elif utilization_rate <= 70:
                utilization_score = 20
                utilization_status = 'fair'
            else:
                utilization_score = 10
                utilization_status = 'poor'
            
            factors.append({
                'factor': 'credit_utilization',
                'name': '信用利用率',
                'score': utilization_score,
                'max_score': 30,
                'status': utilization_status,
                'value': round(utilization_rate, 2),
                'description': f'信用卡利用率 {utilization_rate:.1f}%'
            })
        else:
            utilization_score = 0
            factors.append({
                'factor': 'credit_utilization',
                'name': '信用利用率',
                'score': 0,
                'max_score': 30,
                'status': 'no_data',
                'value': 0,
                'description': '无信用卡数据'
            })
        
        # 交易活跃度评分（20分）
        thirty_days_ago = datetime.now() - timedelta(days=30)
        transaction_count = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= thirty_days_ago
            )
        ).count()
        
        if transaction_count >= 20:
            activity_score = 20
            activity_status = 'excellent'
        elif transaction_count >= 10:
            activity_score = 15
            activity_status = 'good'
        elif transaction_count >= 5:
            activity_score = 10
            activity_status = 'fair'
        else:
            activity_score = 5
            activity_status = 'poor'
        
        factors.append({
            'factor': 'transaction_activity',
            'name': '交易活跃度',
            'score': activity_score,
            'max_score': 20,
            'status': activity_status,
            'value': transaction_count,
            'description': f'最近30天交易 {transaction_count} 笔'
        })
        
        # 年费管理评分（20分）
        current_year = datetime.now().year
        fee_records = self.db.query(AnnualFeeRecord).join(AnnualFeeRecord.rule).join(CreditCard).filter(
            and_(
                CreditCard.user_id == user_id,
                AnnualFeeRecord.fee_year == current_year
            )
        ).all()
        
        if fee_records:
            total_base = sum(record.base_fee for record in fee_records)
            total_waived = sum(record.waiver_amount for record in fee_records)
            waiver_rate = total_waived / total_base * 100 if total_base > 0 else 0
            
            if waiver_rate >= 80:
                fee_score = 20
                fee_status = 'excellent'
            elif waiver_rate >= 60:
                fee_score = 15
                fee_status = 'good'
            elif waiver_rate >= 40:
                fee_score = 10
                fee_status = 'fair'
            else:
                fee_score = 5
                fee_status = 'poor'
            
            factors.append({
                'factor': 'annual_fee_management',
                'name': '年费管理',
                'score': fee_score,
                'max_score': 20,
                'status': fee_status,
                'value': round(waiver_rate, 2),
                'description': f'年费减免率 {waiver_rate:.1f}%'
            })
        else:
            fee_score = 10  # 无年费数据给中等分数
            factors.append({
                'factor': 'annual_fee_management',
                'name': '年费管理',
                'score': 10,
                'max_score': 20,
                'status': 'no_data',
                'value': 0,
                'description': '无年费数据'
            })
        
        # 提醒使用评分（15分）
        active_reminders = self.db.query(ReminderSetting).filter(
            and_(
                ReminderSetting.user_id == user_id,
                ReminderSetting.is_enabled == True
            )
        ).count()
        
        if active_reminders >= 3:
            reminder_score = 15
            reminder_status = 'excellent'
        elif active_reminders >= 2:
            reminder_score = 12
            reminder_status = 'good'
        elif active_reminders >= 1:
            reminder_score = 8
            reminder_status = 'fair'
        else:
            reminder_score = 0
            reminder_status = 'poor'
        
        factors.append({
            'factor': 'reminder_usage',
            'name': '提醒使用',
            'score': reminder_score,
            'max_score': 15,
            'status': reminder_status,
            'value': active_reminders,
            'description': f'启用提醒 {active_reminders} 个'
        })
        
        # 记录完整性评分（15分）
        cards_with_complete_info = self.db.query(CreditCard).filter(
            and_(
                CreditCard.user_id == user_id,
                CreditCard.card_name.isnot(None),
                CreditCard.credit_limit > 0,
                CreditCard.billing_date.isnot(None)
            )
        ).count()
        
        total_cards = self.db.query(CreditCard).filter(CreditCard.user_id == user_id).count()
        
        if total_cards > 0:
            completeness_rate = cards_with_complete_info / total_cards * 100
            
            if completeness_rate >= 90:
                completeness_score = 15
                completeness_status = 'excellent'
            elif completeness_rate >= 70:
                completeness_score = 12
                completeness_status = 'good'
            elif completeness_rate >= 50:
                completeness_score = 8
                completeness_status = 'fair'
            else:
                completeness_score = 5
                completeness_status = 'poor'
            
            factors.append({
                'factor': 'data_completeness',
                'name': '数据完整性',
                'score': completeness_score,
                'max_score': 15,
                'status': completeness_status,
                'value': round(completeness_rate, 2),
                'description': f'信息完整度 {completeness_rate:.1f}%'
            })
        else:
            completeness_score = 0
            factors.append({
                'factor': 'data_completeness',
                'name': '数据完整性',
                'score': 0,
                'max_score': 15,
                'status': 'no_data',
                'value': 0,
                'description': '无信用卡数据'
            })
        
        # 计算总分
        total_score = utilization_score + activity_score + fee_score + reminder_score + completeness_score
        
        # 确定等级
        if total_score >= 90:
            grade = 'A+'
            level = 'excellent'
        elif total_score >= 80:
            grade = 'A'
            level = 'very_good'
        elif total_score >= 70:
            grade = 'B+'
            level = 'good'
        elif total_score >= 60:
            grade = 'B'
            level = 'fair'
        elif total_score >= 50:
            grade = 'C+'
            level = 'poor'
        else:
            grade = 'C'
            level = 'very_poor'
        
        return {
            'total_score': total_score,
            'max_score': 100,
            'grade': grade,
            'level': level,
            'factors': factors,
            'recommendations': self._get_health_recommendations(factors)
        }
    
    def _analyze_trends(self, trends_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析趋势数据"""
        
        if len(trends_list) < 2:
            return {
                'expense_trend': 'stable',
                'income_trend': 'stable',
                'growth_rate': 0.0,
                'volatility': 'low'
            }
        
        # 计算支出趋势
        recent_expense = trends_list[-1]['expense_amount']
        previous_expense = trends_list[-2]['expense_amount']
        
        if recent_expense > previous_expense * 1.1:
            expense_trend = 'increasing'
        elif recent_expense < previous_expense * 0.9:
            expense_trend = 'decreasing'
        else:
            expense_trend = 'stable'
        
        # 计算收入趋势
        recent_income = trends_list[-1]['income_amount']
        previous_income = trends_list[-2]['income_amount']
        
        if recent_income > previous_income * 1.1:
            income_trend = 'increasing'
        elif recent_income < previous_income * 0.9:
            income_trend = 'decreasing'
        else:
            income_trend = 'stable'
        
        # 计算增长率（基于支出）
        if previous_expense > 0:
            growth_rate = (recent_expense - previous_expense) / previous_expense * 100
        else:
            growth_rate = 0.0
        
        # 计算波动性
        expense_amounts = [trend['expense_amount'] for trend in trends_list]
        if len(expense_amounts) > 1:
            avg_expense = sum(expense_amounts) / len(expense_amounts)
            variance = sum((x - avg_expense) ** 2 for x in expense_amounts) / len(expense_amounts)
            std_dev = variance ** 0.5
            cv = std_dev / avg_expense if avg_expense > 0 else 0
            
            if cv > 0.3:
                volatility = 'high'
            elif cv > 0.15:
                volatility = 'medium'
            else:
                volatility = 'low'
        else:
            volatility = 'low'
        
        return {
            'expense_trend': expense_trend,
            'income_trend': income_trend,
            'growth_rate': round(growth_rate, 2),
            'volatility': volatility
        }
    
    def _get_health_recommendations(self, factors: List[Dict[str, Any]]) -> List[str]:
        """获取健康评分建议"""
        
        recommendations = []
        
        for factor in factors:
            if factor['status'] == 'poor':
                if factor['factor'] == 'credit_utilization':
                    recommendations.append("建议降低信用卡使用率至30%以下，可考虑分期付款或增加还款频率")
                elif factor['factor'] == 'transaction_activity':
                    recommendations.append("建议增加信用卡使用频率，合理规划日常消费")
                elif factor['factor'] == 'annual_fee_management':
                    recommendations.append("建议关注年费减免条件，通过达标消费或积分兑换减免年费")
                elif factor['factor'] == 'reminder_usage':
                    recommendations.append("建议设置还款提醒和年费提醒，避免逾期和遗忘")
                elif factor['factor'] == 'data_completeness':
                    recommendations.append("建议完善信用卡信息，包括账单日、额度等关键数据")
            elif factor['status'] == 'fair':
                if factor['factor'] == 'credit_utilization':
                    recommendations.append("信用卡使用率偏高，建议控制在30%以内")
                elif factor['factor'] == 'annual_fee_management':
                    recommendations.append("可进一步优化年费减免策略，提高减免率")
        
        if not recommendations:
            recommendations.append("您的财务管理状况良好，继续保持！")
        
        return recommendations 