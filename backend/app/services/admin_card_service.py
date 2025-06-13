"""
管理员信用卡服务
提供系统级信用卡统计和分析功能（数据脱敏）
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract, desc
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

from app.models.database.card import CreditCard, Bank
from app.models.database.user import User
from app.models.database.transaction import Transaction
from app.models.database.annual_fee import AnnualFeeRecord
from app.core.exceptions.custom import ResourceNotFoundError


class AdminCardService:
    """管理员信用卡服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_card_statistics(self) -> Dict[str, Any]:
        """获取信用卡系统统计数据（脱敏）"""
        
        # 基础统计
        total_cards = self.db.query(CreditCard).count()
        active_cards = self.db.query(CreditCard).filter(CreditCard.status == 'active').count()
        frozen_cards = self.db.query(CreditCard).filter(CreditCard.status == 'frozen').count()
        closed_cards = self.db.query(CreditCard).filter(CreditCard.status == 'closed').count()
        
        # 额度统计
        credit_stats = self.db.query(
            func.sum(CreditCard.credit_limit).label('total_credit'),
            func.sum(CreditCard.used_limit).label('total_used'),
            func.avg(
                case(
                    (CreditCard.credit_limit > 0, 
                     CreditCard.used_limit * 100.0 / CreditCard.credit_limit),
                    else_=0
                )
            ).label('avg_utilization')
        ).filter(CreditCard.status == 'active').first()
        
        total_credit_limit = credit_stats.total_credit or Decimal('0')
        total_used_limit = credit_stats.total_used or Decimal('0')
        average_utilization = credit_stats.avg_utilization or Decimal('0')
        
        # 按状态分类统计
        cards_by_status = {
            'active': active_cards,
            'frozen': frozen_cards,
            'closed': closed_cards
        }
        
        # 按类型分类统计
        type_stats = self.db.query(
            CreditCard.card_type,
            func.count(CreditCard.id).label('count')
        ).group_by(CreditCard.card_type).all()
        
        cards_by_type = {stat.card_type: stat.count for stat in type_stats}
        
        # 按等级分类统计
        level_stats = self.db.query(
            CreditCard.card_level,
            func.count(CreditCard.id).label('count')
        ).filter(CreditCard.card_level.isnot(None)).group_by(CreditCard.card_level).all()
        
        cards_by_level = {stat.card_level: stat.count for stat in level_stats}
        
        return {
            'total_cards': total_cards,
            'active_cards': active_cards,
            'frozen_cards': frozen_cards,
            'closed_cards': closed_cards,
            'total_credit_limit': total_credit_limit,
            'total_used_limit': total_used_limit,
            'average_utilization': round(average_utilization, 2),
            'cards_by_status': cards_by_status,
            'cards_by_type': cards_by_type,
            'cards_by_level': cards_by_level
        }
    
    def get_bank_distribution(self) -> Dict[str, Any]:
        """获取银行分布统计"""
        
        # 银行分布统计
        bank_stats = self.db.query(
            Bank.bank_name,
            Bank.bank_code,
            func.count(CreditCard.id).label('card_count'),
            func.sum(CreditCard.credit_limit).label('total_credit'),
            func.avg(CreditCard.credit_limit).label('avg_credit')
        ).join(
            CreditCard, Bank.id == CreditCard.bank_id
        ).group_by(
            Bank.id, Bank.bank_name, Bank.bank_code
        ).order_by(
            desc(func.count(CreditCard.id))
        ).all()
        
        total_cards = sum(stat.card_count for stat in bank_stats)
        
        bank_distribution = []
        for stat in bank_stats:
            percentage = (stat.card_count * 100.0 / total_cards) if total_cards > 0 else 0
            bank_distribution.append({
                'bank_name': stat.bank_name,
                'bank_code': stat.bank_code,
                'card_count': stat.card_count,
                'percentage': round(percentage, 2),
                'total_credit_limit': stat.total_credit or Decimal('0'),
                'average_credit_limit': round(stat.avg_credit or Decimal('0'), 2)
            })
        
        # 前十大银行
        top_banks = [dist['bank_name'] for dist in bank_distribution[:10]]
        
        return {
            'total_banks': len(bank_stats),
            'bank_distribution': bank_distribution,
            'bank_stats': bank_distribution,  # 添加别名字段
            'top_banks': top_banks
        }
    
    def get_card_types_distribution(self) -> Dict[str, Any]:
        """获取卡片类型分布统计"""
        
        # 卡片类型分布
        type_distribution = self.db.query(
            CreditCard.card_type,
            func.count(CreditCard.id).label('count'),
            func.avg(CreditCard.credit_limit).label('avg_limit')
        ).group_by(CreditCard.card_type).all()
        
        # 卡片等级分布
        level_distribution = self.db.query(
            CreditCard.card_level,
            func.count(CreditCard.id).label('count'),
            func.avg(CreditCard.credit_limit).label('avg_limit')
        ).filter(
            CreditCard.card_level.isnot(None)
        ).group_by(CreditCard.card_level).all()
        
        # 卡组织分布
        network_distribution = self.db.query(
            CreditCard.card_network,
            func.count(CreditCard.id).label('count')
        ).filter(
            CreditCard.card_network.isnot(None)
        ).group_by(CreditCard.card_network).all()
        
        return {
            'type_distribution': [
                {
                    'type': stat.card_type,
                    'count': stat.count,
                    'average_limit': round(stat.avg_limit or Decimal('0'), 2)
                }
                for stat in type_distribution
            ],
            'level_distribution': [
                {
                    'level': stat.card_level,
                    'count': stat.count,
                    'average_limit': round(stat.avg_limit or Decimal('0'), 2)
                }
                for stat in level_distribution
            ],
            'network_distribution': [
                {
                    'network': stat.card_network,
                    'count': stat.count
                }
                for stat in network_distribution
            ]
        }
    
    def get_card_health_status(self) -> Dict[str, Any]:
        """获取信用卡健康状况分析"""
        
        # 利用率分布统计
        utilization_ranges = [
            ('low_risk', 0, 30),
            ('medium_risk', 30, 70),
            ('high_risk', 70, 90),
            ('critical_risk', 90, 100)
        ]
        
        utilization_distribution = {}
        total_active_cards = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            CreditCard.credit_limit > 0
        ).count()
        
        for risk_level, min_util, max_util in utilization_ranges:
            count = self.db.query(CreditCard).filter(
                CreditCard.status == 'active',
                CreditCard.credit_limit > 0,
                and_(
                    (CreditCard.used_limit * 100.0 / CreditCard.credit_limit) >= min_util,
                    (CreditCard.used_limit * 100.0 / CreditCard.credit_limit) < max_util
                )
            ).count()
            
            percentage = (count * 100.0 / total_active_cards) if total_active_cards > 0 else 0
            utilization_distribution[risk_level] = {
                'range': f'{min_util}-{max_util}%',
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        # 即将到期统计
        now = datetime.now()
        next_month = now + timedelta(days=30)
        next_3_months = now + timedelta(days=90)
        next_6_months = now + timedelta(days=180)
        
        expiring_next_month = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            or_(
                and_(
                    CreditCard.expiry_year == next_month.year,
                    CreditCard.expiry_month == next_month.month
                ),
                and_(
                    CreditCard.expiry_year == now.year,
                    CreditCard.expiry_month == now.month
                )
            )
        ).count()
        
        expiring_3_months = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            or_(
                CreditCard.expiry_year < next_3_months.year,
                and_(
                    CreditCard.expiry_year == next_3_months.year,
                    CreditCard.expiry_month <= next_3_months.month
                )
            ),
            or_(
                CreditCard.expiry_year > now.year,
                and_(
                    CreditCard.expiry_year == now.year,
                    CreditCard.expiry_month >= now.month
                )
            )
        ).count()
        
        expiring_6_months = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            or_(
                CreditCard.expiry_year < next_6_months.year,
                and_(
                    CreditCard.expiry_year == next_6_months.year,
                    CreditCard.expiry_month <= next_6_months.month
                )
            ),
            or_(
                CreditCard.expiry_year > now.year,
                and_(
                    CreditCard.expiry_year == now.year,
                    CreditCard.expiry_month >= now.month
                )
            )
        ).count()
        
        # 不活跃卡片统计（基于交易记录）
        cutoff_30_days = now - timedelta(days=30)
        cutoff_90_days = now - timedelta(days=90)
        cutoff_180_days = now - timedelta(days=180)
        
        # 30天内无交易的活跃卡片
        inactive_30_days = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            ~CreditCard.id.in_(
                self.db.query(Transaction.card_id).filter(
                    Transaction.transaction_date >= cutoff_30_days
                ).distinct()
            )
        ).count()
        
        # 90天内无交易的活跃卡片
        inactive_90_days = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            ~CreditCard.id.in_(
                self.db.query(Transaction.card_id).filter(
                    Transaction.transaction_date >= cutoff_90_days
                ).distinct()
            )
        ).count()
        
        # 180天内无交易的活跃卡片
        inactive_180_days = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            ~CreditCard.id.in_(
                self.db.query(Transaction.card_id).filter(
                    Transaction.transaction_date >= cutoff_180_days
                ).distinct()
            )
        ).count()
        
        # 计算整体健康评分
        high_risk_count = utilization_distribution['high_risk']['count']
        critical_risk_count = utilization_distribution['critical_risk']['count']
        
        health_score = 100
        if total_active_cards > 0:
            # 高风险利用率扣分
            health_score -= (high_risk_count * 10 / total_active_cards)
            # 极高风险利用率扣分
            health_score -= (critical_risk_count * 20 / total_active_cards)
            # 即将到期扣分
            health_score -= (expiring_next_month * 5 / total_active_cards)
            # 不活跃卡片扣分
            health_score -= (inactive_90_days * 3 / total_active_cards)
        
        health_score = max(0, min(100, health_score))
        
        return {
            'overall_health_score': round(health_score, 1),
            'utilization_distribution': utilization_distribution,
            'expiring_soon': {
                'next_month': expiring_next_month,
                'next_3_months': expiring_3_months,
                'next_6_months': expiring_6_months
            },
            'inactive_cards': {
                'no_transactions_30_days': inactive_30_days,
                'no_transactions_90_days': inactive_90_days,
                'no_transactions_180_days': inactive_180_days
            }
        }
    
    def get_card_trends(self, months: int = 6) -> Dict[str, Any]:
        """获取信用卡趋势分析"""
        
        now = datetime.now()
        start_date = now - timedelta(days=months * 30)
        
        monthly_trends = []
        
        for i in range(months):
            month_start = start_date + timedelta(days=i * 30)
            month_end = month_start + timedelta(days=30)
            
            # 当月新增卡片
            new_cards = self.db.query(CreditCard).filter(
                CreditCard.created_at >= month_start,
                CreditCard.created_at < month_end
            ).count()
            
            # 当月关闭卡片
            closed_cards = self.db.query(CreditCard).filter(
                CreditCard.status == 'closed',
                CreditCard.updated_at >= month_start,
                CreditCard.updated_at < month_end
            ).count()
            
            # 月末总卡片数
            total_cards = self.db.query(CreditCard).filter(
                CreditCard.created_at <= month_end
            ).count()
            
            # 当月平均利用率
            avg_utilization = self.db.query(
                func.avg(
                    case(
                        (CreditCard.credit_limit > 0,
                         CreditCard.used_limit * 100.0 / CreditCard.credit_limit),
                        else_=0
                    )
                )
            ).filter(
                CreditCard.status == 'active',
                CreditCard.created_at <= month_end
            ).scalar() or 0
            
            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'new_cards': new_cards,
                'closed_cards': closed_cards,
                'net_growth': new_cards - closed_cards,
                'total_cards': total_cards,
                'average_utilization': round(avg_utilization, 1)
            })
        
        # 计算增长率
        if len(monthly_trends) >= 2:
            first_month = monthly_trends[0]['total_cards']
            last_month = monthly_trends[-1]['total_cards']
            growth_rate = ((last_month - first_month) * 100.0 / first_month) if first_month > 0 else 0
        else:
            growth_rate = 0
        
        # 利用率趋势分析
        utilizations = [trend['average_utilization'] for trend in monthly_trends]
        if len(utilizations) >= 2:
            if utilizations[-1] > utilizations[0] + 5:
                utilization_trend = "上升"
            elif utilizations[-1] < utilizations[0] - 5:
                utilization_trend = "下降"
            else:
                utilization_trend = "稳定"
        else:
            utilization_trend = "稳定"
        
        # 简单预测（基于线性趋势）
        if len(monthly_trends) >= 3:
            recent_growth = sum(trend['net_growth'] for trend in monthly_trends[-3:]) / 3
            next_month_new_cards = max(0, int(recent_growth))
            next_month_total = monthly_trends[-1]['total_cards'] + next_month_new_cards
        else:
            next_month_new_cards = 0
            next_month_total = monthly_trends[-1]['total_cards'] if monthly_trends else 0
        
        return {
            'analysis_period': f'{months}个月',
            'monthly_trends': monthly_trends,
            'monthly_stats': monthly_trends,  # 添加别名字段
            'growth_rate': round(growth_rate, 1),
            'utilization_trend': utilization_trend,
            'predictions': {
                'next_month_new_cards': next_month_new_cards,
                'next_month_total': next_month_total
            },
            'growth_prediction': {  # 添加别名字段
                'next_month_new_cards': next_month_new_cards,
                'next_month_total': next_month_total
            }
        }
    
    def get_utilization_analysis(self) -> Dict[str, Any]:
        """获取信用额度利用率分析"""
        
        # 整体利用率
        overall_utilization = self.db.query(
            func.avg(
                case(
                    (CreditCard.credit_limit > 0,
                     CreditCard.used_limit * 100.0 / CreditCard.credit_limit),
                    else_=0
                )
            )
        ).filter(CreditCard.status == 'active').scalar() or 0
        
        # 风险分布
        total_cards = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            CreditCard.credit_limit > 0
        ).count()
        
        risk_ranges = [
            ('low_risk', 0, 50),
            ('medium_risk', 50, 70),
            ('high_risk', 70, 90),
            ('critical_risk', 90, 100)
        ]
        
        risk_distribution = {}
        for risk_level, min_util, max_util in risk_ranges:
            count = self.db.query(CreditCard).filter(
                CreditCard.status == 'active',
                CreditCard.credit_limit > 0,
                and_(
                    (CreditCard.used_limit * 100.0 / CreditCard.credit_limit) >= min_util,
                    (CreditCard.used_limit * 100.0 / CreditCard.credit_limit) < max_util
                )
            ).count()
            
            percentage = (count * 100.0 / total_cards) if total_cards > 0 else 0
            risk_distribution[risk_level] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        # 按银行分析利用率
        utilization_by_bank = self.db.query(
            Bank.bank_name,
            func.avg(
                case(
                    (CreditCard.credit_limit > 0,
                     CreditCard.used_limit * 100.0 / CreditCard.credit_limit),
                    else_=0
                )
            ).label('avg_utilization')
        ).join(
            CreditCard, Bank.id == CreditCard.bank_id
        ).filter(
            CreditCard.status == 'active'
        ).group_by(Bank.bank_name).order_by(
            desc('avg_utilization')
        ).all()
        
        # 按卡片等级分析利用率
        utilization_by_level = self.db.query(
            CreditCard.card_level,
            func.avg(
                case(
                    (CreditCard.credit_limit > 0,
                     CreditCard.used_limit * 100.0 / CreditCard.credit_limit),
                    else_=0
                )
            ).label('avg_utilization')
        ).filter(
            CreditCard.status == 'active',
            CreditCard.card_level.isnot(None)
        ).group_by(CreditCard.card_level).order_by(
            desc('avg_utilization')
        ).all()
        
        # 生成分析建议
        recommendations = []
        
        if risk_distribution['critical_risk']['percentage'] > 5:
            recommendations.append("建议关注利用率超过90%的用户，可能存在还款风险")
        
        if risk_distribution['high_risk']['percentage'] > 15:
            recommendations.append("高利用率用户较多，建议推广额度提升服务")
        
        # 找出利用率最高的银行
        if utilization_by_bank:
            highest_bank = utilization_by_bank[0]
            if highest_bank.avg_utilization > 50:
                recommendations.append(f"{highest_bank.bank_name}的用户利用率较高，需要重点关注")
        
        # 找出利用率最高的卡片等级
        if utilization_by_level:
            highest_level = utilization_by_level[0]
            if highest_level.avg_utilization > 40:
                recommendations.append(f"{highest_level.card_level}用户利用率偏高，可推荐升级到更高等级")
        
        return {
            'overall_utilization': round(overall_utilization, 1),
            'risk_distribution': risk_distribution,
            'utilization_by_bank': [
                {
                    'bank_name': stat.bank_name,
                    'average_utilization': round(stat.avg_utilization, 1)
                }
                for stat in utilization_by_bank
            ],
            'utilization_by_card_level': [
                {
                    'card_level': stat.card_level,
                    'average_utilization': round(stat.avg_utilization, 1)
                }
                for stat in utilization_by_level
            ],
            'recommendations': recommendations
        }
    
    def get_expiry_alerts(self, months_ahead: int = 3) -> Dict[str, Any]:
        """获取即将到期卡片统计"""
        
        now = datetime.now()
        
        # 计算各个时间点的到期卡片
        expiring_cards = {}
        expiring_by_bank = {}
        
        for month in range(1, months_ahead + 1):
            target_date = now + timedelta(days=month * 30)
            
            # 查询即将到期的卡片
            expiring = self.db.query(CreditCard).filter(
                CreditCard.status == 'active',
                or_(
                    and_(
                        CreditCard.expiry_year == target_date.year,
                        CreditCard.expiry_month == target_date.month
                    ),
                    and_(
                        CreditCard.expiry_year < target_date.year
                    ),
                    and_(
                        CreditCard.expiry_year == target_date.year,
                        CreditCard.expiry_month < target_date.month
                    )
                ),
                or_(
                    CreditCard.expiry_year > now.year,
                    and_(
                        CreditCard.expiry_year == now.year,
                        CreditCard.expiry_month >= now.month
                    )
                )
            ).count()
            
            expiring_cards[f'next_{month}_month{"s" if month > 1 else ""}'] = expiring
        
        # 按银行统计即将到期的卡片
        bank_expiry_stats = self.db.query(
            Bank.bank_name,
            func.count(CreditCard.id).label('count')
        ).join(
            CreditCard, Bank.id == CreditCard.bank_id
        ).filter(
            CreditCard.status == 'active',
            or_(
                and_(
                    CreditCard.expiry_year == (now + timedelta(days=months_ahead * 30)).year,
                    CreditCard.expiry_month <= (now + timedelta(days=months_ahead * 30)).month
                ),
                CreditCard.expiry_year < (now + timedelta(days=months_ahead * 30)).year
            ),
            or_(
                CreditCard.expiry_year > now.year,
                and_(
                    CreditCard.expiry_year == now.year,
                    CreditCard.expiry_month >= now.month
                )
            )
        ).group_by(Bank.bank_name).order_by(desc('count')).all()
        
        expiring_by_bank = [
            {
                'bank_name': stat.bank_name,
                'count': stat.count
            }
            for stat in bank_expiry_stats
        ]
        
        # 计算历史续卡率（简化计算）
        # 查询过去一年到期的卡片和仍然活跃的卡片比例
        last_year = now - timedelta(days=365)
        
        expired_last_year = self.db.query(CreditCard).filter(
            or_(
                and_(
                    CreditCard.expiry_year == last_year.year,
                    CreditCard.expiry_month == last_year.month
                ),
                and_(
                    CreditCard.expiry_year < last_year.year
                )
            )
        ).count()
        
        still_active_from_expired = self.db.query(CreditCard).filter(
            CreditCard.status == 'active',
            or_(
                and_(
                    CreditCard.expiry_year == last_year.year,
                    CreditCard.expiry_month == last_year.month
                ),
                and_(
                    CreditCard.expiry_year < last_year.year
                )
            )
        ).count()
        
        renewal_rate = (still_active_from_expired * 100.0 / expired_last_year) if expired_last_year > 0 else 85.0
        
        # 生成管理建议
        recommendations = []
        
        total_expiring = sum(expiring_cards.values())
        if total_expiring > 100:
            recommendations.append("即将到期卡片数量较多，建议提前通知用户更新卡片信息")
        
        if renewal_rate < 80:
            recommendations.append("续卡率偏低，建议优化续卡流程和用户体验")
        
        if expiring_by_bank:
            top_expiring_bank = expiring_by_bank[0]
            if top_expiring_bank['count'] > 50:
                recommendations.append(f"关注{top_expiring_bank['bank_name']}的到期卡片较多")
        
        return {
            'analysis_months': months_ahead,
            'expiring_cards': expiring_cards,
            'expiring_by_bank': expiring_by_bank,
            'renewal_rate': round(renewal_rate, 1),
            'recommendations': recommendations
        }
    
    def get_annual_fee_summary(self, year: int) -> Dict[str, Any]:
        """获取年费管理概览"""
        
        # 查询指定年份的年费记录
        fee_records = self.db.query(AnnualFeeRecord).filter(
            AnnualFeeRecord.fee_year == year
        ).all()
        
        if not fee_records:
            return {
                'year': year,
                'total_cards_with_fee': 0,
                'total_base_fee': Decimal('0'),
                'total_actual_fee': Decimal('0'),
                'total_revenue': Decimal('0'),  # 添加别名字段
                'total_waived_amount': Decimal('0'),
                'waiver_rate': Decimal('0'),
                'fee_status_distribution': {},
                'waiver_methods': {},
                'waiver_stats': {},  # 添加别名字段
                'revenue_impact': {}
            }
        
        # 基础统计
        total_cards_with_fee = len(fee_records)
        total_base_fee = sum(record.base_fee for record in fee_records)
        total_actual_fee = sum(record.actual_fee for record in fee_records)
        total_waived_amount = sum(record.waiver_amount for record in fee_records)
        
        waiver_rate = (total_waived_amount * Decimal('100') / total_base_fee) if total_base_fee > 0 else Decimal('0')
        
        # 年费状态分布
        status_distribution = {}
        for record in fee_records:
            status = record.status
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # 减免方式统计（基于减免原因）
        waiver_methods = {}
        for record in fee_records:
            if record.waiver_amount > 0 and record.waiver_reason:
                # 简化的减免方式分类
                if '刷卡金额' in record.waiver_reason or '消费' in record.waiver_reason:
                    method = 'spending_amount'
                elif '刷卡次数' in record.waiver_reason or '笔数' in record.waiver_reason:
                    method = 'transaction_count'
                elif '积分' in record.waiver_reason:
                    method = 'points_redeem'
                else:
                    method = 'other'
                
                waiver_methods[method] = waiver_methods.get(method, 0) + 1
        
        # 收入影响分析
        collected_fees = sum(
            record.actual_fee for record in fee_records 
            if record.status == 'paid'
        )
        waived_fees = sum(
            record.waiver_amount for record in fee_records 
            if record.status == 'waived'
        )
        collection_rate = (collected_fees * Decimal('100') / total_base_fee) if total_base_fee > 0 else Decimal('0')
        
        revenue_impact = {
            'collected_fees': collected_fees,
            'waived_fees': waived_fees,
            'collection_rate': round(collection_rate, 2)
        }
        
        return {
            'year': year,
            'total_cards_with_fee': total_cards_with_fee,
            'total_base_fee': total_base_fee,
            'total_actual_fee': total_actual_fee,
            'total_revenue': total_actual_fee,  # 添加别名字段
            'total_waived_amount': total_waived_amount,
            'waiver_rate': round(waiver_rate, 2),
            'fee_status_distribution': status_distribution,
            'waiver_methods': waiver_methods,
            'waiver_stats': waiver_methods,  # 添加别名字段
            'revenue_impact': revenue_impact
        } 