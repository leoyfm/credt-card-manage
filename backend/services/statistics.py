"""
统计服务层

提供各种统计数据的业务逻辑处理。
"""

import logging
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, text, case
from collections import defaultdict

from db_models.cards import CreditCard
from db_models.transactions import Transaction, TransactionType, TransactionCategory
from db_models.annual_fee import AnnualFeeRecord
from models.annual_fee import WaiverStatus
from db_models.users import User
from models.statistics import (
    OverallStatistics, CardStatistics, CreditLimitStatistics, 
    TransactionStatistics, CategoryStatistics, MonthlyStatistics,
    AnnualFeeStatistics, BankStatistics, DetailedStatisticsQuery
)

logger = logging.getLogger(__name__)

class StatisticsService:
    """统计服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_overall_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None) -> OverallStatistics:
        """
        获取总体统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            
        Returns:
            OverallStatistics: 总体统计信息
        """
        logger.info(f"获取用户 {user_id} 的总体统计信息")
        
        try:
            # 基础查询条件
            base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
            
            # 处理查询参数
            if query:
                if query.bank_name:
                    base_filter.append(CreditCard.bank_name == query.bank_name)
                if query.card_id:
                    base_filter.append(CreditCard.id == query.card_id)
                if not query.include_cancelled:
                    base_filter.append(CreditCard.status != "cancelled")
            
            # 获取各项统计
            card_stats = await self._get_card_statistics(user_id, base_filter)
            credit_stats = await self._get_credit_limit_statistics(user_id, base_filter)
            transaction_stats = await self._get_transaction_statistics(user_id, base_filter, query)
            annual_fee_stats = await self._get_annual_fee_statistics(user_id, base_filter)
            top_categories = await self._get_top_categories_statistics(user_id, base_filter, query)
            monthly_trends = await self._get_monthly_trends(user_id, base_filter, query)
            bank_distribution = await self._get_bank_distribution(user_id, base_filter)
            
            return OverallStatistics(
                card_stats=card_stats,
                credit_stats=credit_stats,
                transaction_stats=transaction_stats,
                annual_fee_stats=annual_fee_stats,
                top_categories=top_categories,
                monthly_trends=monthly_trends,
                bank_distribution=bank_distribution
            )
            
        except Exception as e:
            logger.error(f"获取总体统计信息失败: {str(e)}")
            raise

    async def get_card_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None) -> CardStatistics:
        """
        获取信用卡统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            
        Returns:
            CardStatistics: 信用卡统计信息
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_card_statistics(user_id, base_filter)

    async def get_credit_limit_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None) -> CreditLimitStatistics:
        """
        获取信用额度统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            
        Returns:
            CreditLimitStatistics: 信用额度统计信息
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_credit_limit_statistics(user_id, base_filter)

    async def get_transaction_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None) -> TransactionStatistics:
        """
        获取交易统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            
        Returns:
            TransactionStatistics: 交易统计信息
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_transaction_statistics(user_id, base_filter, query)

    async def get_annual_fee_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None) -> AnnualFeeStatistics:
        """
        获取年费统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            
        Returns:
            AnnualFeeStatistics: 年费统计信息
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_annual_fee_statistics(user_id, base_filter)

    async def get_category_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None, limit: int = 10) -> List[CategoryStatistics]:
        """
        获取消费分类统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            limit: 返回的分类数量限制
            
        Returns:
            List[CategoryStatistics]: 消费分类统计信息列表
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_top_categories_statistics(user_id, base_filter, query, limit)

    async def get_monthly_trends(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None, months: int = 12) -> List[MonthlyStatistics]:
        """
        获取月度统计趋势
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            months: 返回的月份数量
            
        Returns:
            List[MonthlyStatistics]: 月度统计趋势列表
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_monthly_trends(user_id, base_filter, query, months)

    async def get_bank_statistics(self, user_id: str, query: Optional[DetailedStatisticsQuery] = None) -> List[BankStatistics]:
        """
        获取银行分布统计信息
        
        Args:
            user_id: 用户ID
            query: 查询参数（可选）
            
        Returns:
            List[BankStatistics]: 银行分布统计信息列表
        """
        # 基础查询条件
        base_filter = [CreditCard.user_id == user_id, CreditCard.is_deleted == False]
        
        # 处理查询参数
        if query:
            if query.bank_name:
                base_filter.append(CreditCard.bank_name == query.bank_name)
            if query.card_id:
                base_filter.append(CreditCard.id == query.card_id)
            if not query.include_cancelled:
                base_filter.append(CreditCard.status != "cancelled")
        
        return await self._get_bank_distribution(user_id, base_filter)

    async def _get_card_statistics(self, user_id: str, base_filter: List) -> CardStatistics:
        """获取信用卡统计信息"""
        
        # 获取所有符合条件的信用卡
        cards = self.db.query(CreditCard).filter(and_(*base_filter)).all()
        
        total_cards = len(cards)
        active_cards = sum(1 for card in cards if card.status == "active")
        inactive_cards = sum(1 for card in cards if card.status == "inactive")
        frozen_cards = sum(1 for card in cards if card.status == "frozen")
        cancelled_cards = sum(1 for card in cards if card.status == "cancelled")
        
        # 计算过期和即将过期的卡片
        today = date.today()
        expired_cards = sum(1 for card in cards if card.is_expired)
        
        # 即将到期（未来3个月内）
        three_months_later = today + timedelta(days=90)  # 简化为90天
        expiring_soon_cards = 0
        for card in cards:
            if not card.is_expired:
                # 使用月底日期进行比较
                try:
                    if card.expiry_month == 12:
                        card_expiry = date(card.expiry_year + 1, 1, 1) - timedelta(days=1)
                    else:
                        card_expiry = date(card.expiry_year, card.expiry_month + 1, 1) - timedelta(days=1)
                    
                    if today <= card_expiry <= three_months_later:
                        expiring_soon_cards += 1
                except ValueError:
                    # 处理无效日期
                    pass
        
        return CardStatistics(
            total_cards=total_cards,
            active_cards=active_cards,
            inactive_cards=inactive_cards,
            frozen_cards=frozen_cards,
            cancelled_cards=cancelled_cards,
            expired_cards=expired_cards,
            expiring_soon_cards=expiring_soon_cards
        )

    async def _get_credit_limit_statistics(self, user_id: str, base_filter: List) -> CreditLimitStatistics:
        """获取信用额度统计信息"""
        
        # 查询额度统计
        result = self.db.query(
            func.sum(CreditCard.credit_limit).label('total_credit_limit'),
            func.sum(CreditCard.used_amount).label('total_used_amount'),
            func.max(CreditCard.used_amount / CreditCard.credit_limit * 100).label('highest_utilization'),
            func.min(CreditCard.used_amount / CreditCard.credit_limit * 100).label('lowest_utilization'),
            func.avg(CreditCard.used_amount / CreditCard.credit_limit * 100).label('avg_utilization')
        ).filter(
            and_(*base_filter),
            CreditCard.credit_limit > 0  # 避免除零错误
        ).first()
        
        total_credit_limit = result.total_credit_limit or Decimal('0')
        total_used_amount = result.total_used_amount or Decimal('0')
        total_available_amount = total_credit_limit - total_used_amount
        
        overall_utilization_rate = 0.0
        if total_credit_limit > 0:
            overall_utilization_rate = float(total_used_amount / total_credit_limit * 100)
        
        highest_utilization_rate = float(result.highest_utilization or 0)
        lowest_utilization_rate = float(result.lowest_utilization or 0)
        average_utilization_rate = float(result.avg_utilization or 0)
        
        return CreditLimitStatistics(
            total_credit_limit=total_credit_limit,
            total_used_amount=total_used_amount,
            total_available_amount=total_available_amount,
            overall_utilization_rate=overall_utilization_rate,
            highest_utilization_rate=highest_utilization_rate,
            lowest_utilization_rate=lowest_utilization_rate,
            average_utilization_rate=average_utilization_rate
        )

    async def _get_transaction_statistics(self, user_id: str, base_filter: List, query: Optional[DetailedStatisticsQuery]) -> TransactionStatistics:
        """获取交易统计信息"""
        
        # 构建交易查询条件
        transaction_filter = [Transaction.user_id == user_id, Transaction.is_deleted == False]
        
        # 如果有卡片筛选条件，添加到交易查询中
        if query and query.card_id:
            transaction_filter.append(Transaction.card_id == query.card_id)
        elif len(base_filter) > 2:  # 有其他筛选条件时，需要关联查询
            # 获取符合条件的卡片ID列表
            card_ids_subquery = self.db.query(CreditCard.id).filter(and_(*base_filter)).subquery()
            transaction_filter.append(Transaction.card_id.in_(self.db.query(card_ids_subquery.c.id)))
        
        # 时间范围筛选
        if query and query.start_date:
            transaction_filter.append(Transaction.transaction_date >= query.start_date)
        if query and query.end_date:
            transaction_filter.append(Transaction.transaction_date <= query.end_date)
        
        # 总交易统计
        total_result = self.db.query(
            func.count(Transaction.id).label('total_transactions'),
            func.sum(case(
                (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
                else_=0
            )).label('total_expense_amount'),
            func.sum(case(
                (Transaction.transaction_type == TransactionType.PAYMENT, Transaction.amount),
                else_=0
            )).label('total_payment_amount'),
            func.sum(Transaction.points_earned).label('total_points_earned'),
            func.avg(Transaction.amount).label('avg_amount')
        ).filter(and_(*transaction_filter)).first()
        
        # 本月统计
        current_month_start = date.today().replace(day=1)
        current_month_filter = transaction_filter + [Transaction.transaction_date >= current_month_start]
        
        current_month_result = self.db.query(
            func.count(Transaction.id).label('current_month_transactions'),
            func.sum(case(
                (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
                else_=0
            )).label('current_month_expense')
        ).filter(and_(*current_month_filter)).first()
        
        return TransactionStatistics(
            total_transactions=total_result.total_transactions or 0,
            total_expense_amount=total_result.total_expense_amount or Decimal('0'),
            total_payment_amount=total_result.total_payment_amount or Decimal('0'),
            total_points_earned=total_result.total_points_earned or Decimal('0'),
            current_month_transactions=current_month_result.current_month_transactions or 0,
            current_month_expense_amount=current_month_result.current_month_expense or Decimal('0'),
            average_transaction_amount=total_result.avg_amount or Decimal('0')
        )

    async def _get_annual_fee_statistics(self, user_id: str, base_filter: List) -> AnnualFeeStatistics:
        """获取年费统计信息"""
        
        # 获取符合条件的卡片ID
        card_ids_query = self.db.query(CreditCard.id).filter(and_(*base_filter))
        card_ids = [row[0] for row in card_ids_query.all()]
        
        if not card_ids:
            return AnnualFeeStatistics(
                total_annual_fee=Decimal('0'),
                waived_count=0,
                pending_count=0,
                paid_count=0,
                overdue_count=0,
                current_year_due_amount=Decimal('0'),
                savings_from_waiver=Decimal('0')
            )
        
        # 年费记录统计
        fee_result = self.db.query(
            func.sum(AnnualFeeRecord.fee_amount).label('total_annual_fee'),
            func.count(case(
                (AnnualFeeRecord.waiver_status == WaiverStatus.WAIVED, 1)
            )).label('waived_count'),
            func.count(case(
                (AnnualFeeRecord.waiver_status == WaiverStatus.PENDING, 1)
            )).label('pending_count'),
            func.count(case(
                (AnnualFeeRecord.waiver_status == WaiverStatus.PAID, 1)
            )).label('paid_count'),
            func.count(case(
                (AnnualFeeRecord.waiver_status == WaiverStatus.OVERDUE, 1)
            )).label('overdue_count'),
            func.sum(case(
                (AnnualFeeRecord.waiver_status == WaiverStatus.WAIVED, AnnualFeeRecord.fee_amount),
                else_=0
            )).label('savings_from_waiver')
        ).filter(
            AnnualFeeRecord.card_id.in_(card_ids),
            AnnualFeeRecord.is_deleted == False
        ).first()
        
        # 当前年度应缴年费
        current_year = date.today().year
        current_year_fee = self.db.query(
            func.sum(AnnualFeeRecord.fee_amount)
        ).filter(
            AnnualFeeRecord.card_id.in_(card_ids),
            AnnualFeeRecord.fee_year == current_year,
            AnnualFeeRecord.waiver_status.in_([WaiverStatus.PENDING, WaiverStatus.OVERDUE]),
            AnnualFeeRecord.is_deleted == False
        ).scalar() or Decimal('0')
        
        return AnnualFeeStatistics(
            total_annual_fee=fee_result.total_annual_fee or Decimal('0'),
            waived_count=fee_result.waived_count or 0,
            pending_count=fee_result.pending_count or 0,
            paid_count=fee_result.paid_count or 0,
            overdue_count=fee_result.overdue_count or 0,
            current_year_due_amount=current_year_fee,
            savings_from_waiver=fee_result.savings_from_waiver or Decimal('0')
        )

    async def _get_top_categories_statistics(self, user_id: str, base_filter: List, query: Optional[DetailedStatisticsQuery], limit: int = 10) -> List[CategoryStatistics]:
        """获取消费分类统计（前N名）"""
        
        # 构建交易查询条件
        transaction_filter = [
            Transaction.user_id == user_id, 
            Transaction.is_deleted == False,
            Transaction.transaction_type == TransactionType.EXPENSE
        ]
        
        # 如果有卡片筛选条件，添加到交易查询中
        if query and query.card_id:
            transaction_filter.append(Transaction.card_id == query.card_id)
        elif len(base_filter) > 2:
            card_ids_subquery = self.db.query(CreditCard.id).filter(and_(*base_filter)).subquery()
            transaction_filter.append(Transaction.card_id.in_(self.db.query(card_ids_subquery.c.id)))
        
        # 时间范围筛选
        if query and query.start_date:
            transaction_filter.append(Transaction.transaction_date >= query.start_date)
        if query and query.end_date:
            transaction_filter.append(Transaction.transaction_date <= query.end_date)
        
        # 计算总消费金额（用于计算百分比）
        total_expense = self.db.query(
            func.sum(Transaction.amount)
        ).filter(and_(*transaction_filter)).scalar() or Decimal('0')
        
        # 分类统计查询
        category_results = self.db.query(
            Transaction.category,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            and_(*transaction_filter)
        ).group_by(
            Transaction.category
        ).order_by(
            func.sum(Transaction.amount).desc()
        ).limit(limit).all()
        
        # 分类名称映射
        category_names = {
            TransactionCategory.DINING: "餐饮美食",
            TransactionCategory.SHOPPING: "购物消费",
            TransactionCategory.TRANSPORT: "交通出行",
            TransactionCategory.ENTERTAINMENT: "娱乐休闲",
            TransactionCategory.MEDICAL: "医疗健康",
            TransactionCategory.EDUCATION: "教育培训",
            TransactionCategory.TRAVEL: "旅游酒店",
            TransactionCategory.FUEL: "加油充值",
            TransactionCategory.SUPERMARKET: "超市便利",
            TransactionCategory.ONLINE: "网上购物",
            TransactionCategory.OTHER: "其他消费"
        }
        
        categories = []
        for result in category_results:
            percentage = 0.0
            if total_expense > 0:
                percentage = float(result.total_amount / total_expense * 100)
            
            categories.append(CategoryStatistics(
                category=result.category.value,
                category_name=category_names.get(result.category, result.category.value),
                transaction_count=result.transaction_count,
                total_amount=result.total_amount,
                percentage=percentage
            ))
        
        return categories

    async def _get_monthly_trends(self, user_id: str, base_filter: List, query: Optional[DetailedStatisticsQuery], months: int = 12) -> List[MonthlyStatistics]:
        """获取月度统计趋势（最近N个月）"""
        
        # 构建交易查询条件
        transaction_filter = [Transaction.user_id == user_id, Transaction.is_deleted == False]
        
        # 如果有卡片筛选条件，添加到交易查询中
        if query and query.card_id:
            transaction_filter.append(Transaction.card_id == query.card_id)
        elif len(base_filter) > 2:
            card_ids_subquery = self.db.query(CreditCard.id).filter(and_(*base_filter)).subquery()
            transaction_filter.append(Transaction.card_id.in_(self.db.query(card_ids_subquery.c.id)))
        
        # 计算时间范围（最近N个月）
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)  # 简化为30天一个月
        
        # 如果查询参数中有时间范围，使用查询参数
        if query and query.start_date:
            start_date = query.start_date
        if query and query.end_date:
            end_date = query.end_date
        
        transaction_filter.extend([
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ])
        
        # 月度统计查询
        monthly_results = self.db.query(
            extract('year', Transaction.transaction_date).label('year'),
            extract('month', Transaction.transaction_date).label('month'),
            func.count(Transaction.id).label('transaction_count'),
            func.sum(case(
                (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
                else_=0
            )).label('expense_amount'),
            func.sum(case(
                (Transaction.transaction_type == TransactionType.PAYMENT, Transaction.amount),
                else_=0
            )).label('payment_amount'),
            func.sum(Transaction.points_earned).label('points_earned')
        ).filter(
            and_(*transaction_filter)
        ).group_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).order_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).all()
        
        monthly_trends = []
        for result in monthly_results:
            year_month = f"{int(result.year)}-{int(result.month):02d}"
            monthly_trends.append(MonthlyStatistics(
                year_month=year_month,
                transaction_count=result.transaction_count or 0,
                expense_amount=result.expense_amount or Decimal('0'),
                payment_amount=result.payment_amount or Decimal('0'),
                points_earned=result.points_earned or Decimal('0')
            ))
        
        return monthly_trends

    async def _get_bank_distribution(self, user_id: str, base_filter: List) -> List[BankStatistics]:
        """获取银行分布统计"""
        
        bank_results = self.db.query(
            CreditCard.bank_name,
            func.count(CreditCard.id).label('card_count'),
            func.sum(CreditCard.credit_limit).label('total_credit_limit'),
            func.sum(CreditCard.used_amount).label('total_used_amount')
        ).filter(
            and_(*base_filter)
        ).group_by(
            CreditCard.bank_name
        ).order_by(
            func.sum(CreditCard.credit_limit).desc()
        ).all()
        
        bank_distribution = []
        for result in bank_results:
            utilization_rate = 0.0
            if result.total_credit_limit and result.total_credit_limit > 0:
                utilization_rate = float(result.total_used_amount / result.total_credit_limit * 100)
            
            bank_distribution.append(BankStatistics(
                bank_name=result.bank_name,
                card_count=result.card_count,
                total_credit_limit=result.total_credit_limit or Decimal('0'),
                total_used_amount=result.total_used_amount or Decimal('0'),
                utilization_rate=utilization_rate
            ))
        
        return bank_distribution 