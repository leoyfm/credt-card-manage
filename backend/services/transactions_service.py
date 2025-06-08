"""
交易记录服务

提供交易记录的业务逻辑处理，包括CRUD操作、统计分析、年费进度更新等功能。
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, extract, desc, literal_column, case
from sqlalchemy.orm import Session, joinedload

from models.transactions import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TransactionStatistics,
    TransactionCategoryStatistics,
    MonthlyTransactionTrend,
    get_transaction_category_display,
)
from db_models.transactions import TransactionType, TransactionCategory, TransactionStatus

logger = logging.getLogger(__name__)


class TransactionsService:
    """交易记录服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== CRUD操作 ====================

    def create_transaction(self, user_id: UUID, transaction_data: TransactionCreate) -> Transaction:
        """
        创建交易记录
        
        Args:
            user_id: 用户ID
            transaction_data: 交易数据
            
        Returns:
            Transaction: 创建的交易记录
        """
        try:
            logger.info(f"创建交易记录: 用户{user_id}, 卡片{transaction_data.card_id}")
            
            # 验证信用卡是否属于该用户
            card = self.db.query(self._get_credit_card_model()).filter(
                and_(
                    self._get_credit_card_model().id == transaction_data.card_id,
                    self._get_credit_card_model().user_id == user_id,
                    self._get_credit_card_model().is_deleted == False
                )
            ).first()
            
            if not card:
                raise ValueError("信用卡不存在或不属于该用户")
            
            # 创建交易记录
            transaction_dict = transaction_data.model_dump()
            transaction_dict['user_id'] = user_id
            
            # 自动计算积分（如果未提供）
            if transaction_dict.get('points_earned') is None:
                transaction_dict['points_earned'] = self._calculate_points(
                    transaction_dict['amount'], 
                    transaction_dict.get('points_rate', 1.0)
                )
            
            db_transaction = self._create_transaction_db(transaction_dict)
            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)
            
            # 如果是消费交易，更新年费进度
            if (transaction_data.transaction_type == TransactionType.EXPENSE and 
                transaction_data.status == TransactionStatus.COMPLETED):
                self._update_annual_fee_progress(transaction_data.card_id, transaction_data.amount)
            
            logger.info(f"交易记录创建成功: {db_transaction.id}")
            return Transaction.model_validate(db_transaction)
            
        except Exception as e:
            logger.error(f"创建交易记录失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"创建交易记录失败: {str(e)}")

    def get_transactions(
        self,
        user_id: UUID,
        card_id: Optional[UUID] = None,
        transaction_type: Optional[TransactionType] = None,
        category: Optional[TransactionCategory] = None,
        status: Optional[TransactionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        merchant_name: Optional[str] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        keyword: str = "",
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Transaction], int]:
        """
        获取交易记录列表
        
        支持多种筛选条件和模糊搜索功能。
        
        Args:
            user_id: 用户ID
            card_id: 信用卡ID过滤
            transaction_type: 交易类型过滤
            category: 交易分类过滤
            status: 交易状态过滤
            start_date: 开始时间
            end_date: 结束时间
            merchant_name: 商户名称模糊搜索
            min_amount: 最小金额
            max_amount: 最大金额
            keyword: 关键词模糊搜索
            skip: 跳过的记录数
            limit: 返回的记录数限制
        """
        try:
            logger.info(f"获取交易记录列表: 用户{user_id}")
            
            query = self.db.query(self._get_transaction_model()).filter(
                self._get_transaction_model().user_id == user_id
            )
            
            # 基础过滤条件
            if card_id:
                query = query.filter(self._get_transaction_model().card_id == card_id)
            if transaction_type:
                query = query.filter(self._get_transaction_model().transaction_type == transaction_type)
            if category:
                query = query.filter(self._get_transaction_model().category == category)
            if status:
                query = query.filter(self._get_transaction_model().status == status)
            if start_date:
                query = query.filter(self._get_transaction_model().transaction_date >= start_date)
            if end_date:
                query = query.filter(self._get_transaction_model().transaction_date <= end_date)
            if min_amount:
                query = query.filter(self._get_transaction_model().amount >= min_amount)
            if max_amount:
                query = query.filter(self._get_transaction_model().amount <= max_amount)
            if merchant_name:
                query = query.filter(self._get_transaction_model().merchant_name.ilike(f"%{merchant_name}%"))
            
            # 关键词模糊搜索
            if keyword:
                keyword_filter = f"%{keyword}%"
                query = query.filter(
                    or_(
                        self._get_transaction_model().merchant_name.ilike(keyword_filter),
                        self._get_transaction_model().description.ilike(keyword_filter),
                        self._get_transaction_model().notes.ilike(keyword_filter),
                        self._get_transaction_model().location.ilike(keyword_filter)
                    )
                )
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据，按交易时间倒序
            transactions = query.order_by(
                desc(self._get_transaction_model().transaction_date),
                desc(self._get_transaction_model().created_at)
            ).offset(skip).limit(limit).all()
            
            logger.info(f"找到 {len(transactions)} 条交易记录，总计 {total} 条")
            return [Transaction.model_validate(transaction) for transaction in transactions], total
            
        except Exception as e:
            logger.error(f"获取交易记录列表失败: {str(e)}")
            raise Exception(f"获取交易记录列表失败: {str(e)}")

    def get_transaction(self, transaction_id: UUID, user_id: UUID) -> Optional[Transaction]:
        """获取单个交易记录"""
        try:
            transaction = self.db.query(self._get_transaction_model()).filter(
                self._get_transaction_model().id == transaction_id,
                self._get_transaction_model().user_id == user_id,
                self._get_transaction_model().is_deleted == False
            ).first()
            
            if not transaction:
                return None
                
            return Transaction.model_validate(transaction)
            
        except Exception as e:
            logger.error(f"获取交易记录失败: {str(e)}")
            raise Exception(f"获取交易记录失败: {str(e)}")

    def update_transaction(
        self, 
        transaction_id: UUID, 
        user_id: UUID,
        transaction_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """更新交易记录"""
        try:
            transaction = self.db.query(self._get_transaction_model()).filter(
                self._get_transaction_model().id == transaction_id,
                self._get_transaction_model().user_id == user_id,
                self._get_transaction_model().is_deleted == False
            ).first()
            
            if not transaction:
                return None
            
            update_data = transaction_data.model_dump(exclude_unset=True)
            
            # 验证信用卡是否属于用户（如果更新了card_id）
            if 'card_id' in update_data and update_data['card_id']:
                card = self.db.query(self._get_card_model()).filter(
                    self._get_card_model().id == update_data['card_id'],
                    self._get_card_model().user_id == user_id,
                    self._get_card_model().is_deleted == False
                ).first()
                
                if not card:
                    raise ValueError("指定的信用卡不存在或不属于当前用户")
            
            for field, value in update_data.items():
                if hasattr(transaction, field):
                    setattr(transaction, field, value)
            
            self.db.commit()
            self.db.refresh(transaction)
            
            return Transaction.model_validate(transaction)
            
        except Exception as e:
            logger.error(f"更新交易记录失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"更新交易记录失败: {str(e)}")

    def delete_transaction(self, transaction_id: UUID, user_id: UUID) -> bool:
        """
        删除交易记录
        
        Args:
            transaction_id: 交易记录ID
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            logger.info(f"删除交易记录: {transaction_id}")
            
            transaction = self.db.query(self._get_transaction_model()).filter(
                and_(
                    self._get_transaction_model().id == transaction_id,
                    self._get_transaction_model().user_id == user_id
                )
            ).first()
            
            if not transaction:
                logger.warning(f"交易记录不存在: {transaction_id}")
                return False
            
            card_id = transaction.card_id
            
            # 删除交易记录
            self.db.delete(transaction)
            self.db.commit()
            
            # 重新计算年费进度
            self._recalculate_annual_fee_progress(card_id)
            
            logger.info(f"交易记录删除成功: {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除交易记录失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"删除交易记录失败: {str(e)}")

    # ==================== 统计分析 ====================

    def get_transaction_statistics(
        self, 
        user_id: UUID,
        card_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TransactionStatistics:
        """
        获取交易统计信息
        
        Args:
            user_id: 用户ID
            card_id: 信用卡ID过滤
            start_date: 开始时间
            end_date: 结束时间
            
        Returns:
            TransactionStatistics: 统计信息
        """
        try:
            logger.info(f"获取交易统计: 用户{user_id}")
            
            query = self.db.query(self._get_transaction_model()).filter(
                self._get_transaction_model().user_id == user_id
            )
            
            if card_id:
                query = query.filter(self._get_transaction_model().card_id == card_id)
            if start_date:
                query = query.filter(self._get_transaction_model().transaction_date >= start_date)
            if end_date:
                query = query.filter(self._get_transaction_model().transaction_date <= end_date)
            
            transactions = query.all()
            
            # 基础统计
            total_transactions = len(transactions)
            total_amount = sum(t.amount for t in transactions)
            expense_amount = sum(
                t.amount for t in transactions 
                if t.transaction_type in [TransactionType.EXPENSE, TransactionType.WITHDRAWAL, TransactionType.FEE]
            )
            income_amount = sum(
                t.amount for t in transactions 
                if t.transaction_type in [TransactionType.PAYMENT, TransactionType.REFUND]
            )
            points_earned = sum(t.points_earned or 0 for t in transactions)
            
            # 分类统计
            category_stats = {}
            for transaction in transactions:
                if transaction.transaction_type == TransactionType.EXPENSE:
                    category = transaction.category
                    if category not in category_stats:
                        category_stats[category] = {"count": 0, "amount": Decimal("0")}
                    category_stats[category]["count"] += 1
                    category_stats[category]["amount"] += transaction.amount
            
            categories = [
                {
                    "category": category.value,
                    "category_display": get_transaction_category_display(category),
                    "count": stats["count"],
                    "amount": float(stats["amount"])
                }
                for category, stats in category_stats.items()
            ]
            
            return TransactionStatistics(
                total_transactions=total_transactions,
                total_amount=total_amount,
                expense_amount=expense_amount,
                income_amount=income_amount,
                points_earned=points_earned,
                categories=categories
            )
            
        except Exception as e:
            logger.error(f"获取交易统计失败: {str(e)}")
            raise Exception(f"获取交易统计失败: {str(e)}")

    def get_category_statistics(
        self, 
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TransactionCategoryStatistics]:
        """
        获取交易分类统计
        
        Args:
            user_id: 用户ID
            start_date: 开始时间
            end_date: 结束时间
            
        Returns:
            List[TransactionCategoryStatistics]: 分类统计列表
        """
        try:
            logger.info(f"获取分类统计: 用户{user_id}")
            
            query = self.db.query(
                self._get_transaction_model().category,
                func.count().label('transaction_count'),
                func.sum(self._get_transaction_model().amount).label('total_amount')
            ).filter(
                and_(
                    self._get_transaction_model().user_id == user_id,
                    self._get_transaction_model().transaction_type == TransactionType.EXPENSE
                )
            )
            
            if start_date:
                query = query.filter(self._get_transaction_model().transaction_date >= start_date)
            if end_date:
                query = query.filter(self._get_transaction_model().transaction_date <= end_date)
            
            results = query.group_by(
                self._get_transaction_model().category
            ).order_by(func.sum(self._get_transaction_model().amount).desc()).all()
            
            # 计算总金额用于百分比计算
            total_amount = sum(result.total_amount for result in results)
            
            statistics = []
            for result in results:
                percentage = float(result.total_amount / total_amount * 100) if total_amount > 0 else 0
                average_amount = result.total_amount / result.transaction_count if result.transaction_count > 0 else 0
                
                statistics.append(TransactionCategoryStatistics(
                    category=result.category,
                    category_display=get_transaction_category_display(result.category),
                    transaction_count=result.transaction_count,
                    total_amount=result.total_amount,
                    average_amount=average_amount,
                    percentage=percentage
                ))
            
            logger.info(f"分类统计获取成功，共 {len(statistics)} 个分类")
            return statistics
            
        except Exception as e:
            logger.error(f"获取分类统计失败: {str(e)}")
            raise Exception(f"获取分类统计失败: {str(e)}")

    def get_monthly_trend(
        self, 
        user_id: UUID,
        year: Optional[int] = None,
        card_id: Optional[UUID] = None
    ) -> List[MonthlyTransactionTrend]:
        """
        获取月度交易趋势
        
        Args:
            user_id: 用户ID
            year: 年份，默认当前年份
            card_id: 信用卡ID过滤
            
        Returns:
            List[MonthlyTransactionTrend]: 月度趋势列表
        """
        try:
            if year is None:
                year = datetime.now().year
                
            logger.info(f"获取月度趋势: 用户{user_id}, 年份{year}")
            
            query = self.db.query(
                extract('month', self._get_transaction_model().transaction_date).label('month'),
                func.count().label('transaction_count'),
                func.coalesce(func.sum(
                    case(
                        (self._get_transaction_model().transaction_type.in_([
                            TransactionType.EXPENSE, 
                            TransactionType.WITHDRAWAL, 
                            TransactionType.FEE
                        ]), self._get_transaction_model().amount),
                        else_=0
                    )
                ), 0).label('expense_amount'),
                func.coalesce(func.sum(
                    case(
                        (self._get_transaction_model().transaction_type.in_([
                            TransactionType.PAYMENT, 
                            TransactionType.REFUND
                        ]), self._get_transaction_model().amount),
                        else_=0
                    )
                ), 0).label('income_amount'),
                func.sum(self._get_transaction_model().amount).label('total_amount')
            ).filter(
                and_(
                    self._get_transaction_model().user_id == user_id,
                    extract('year', self._get_transaction_model().transaction_date) == year
                )
            )
            
            if card_id:
                query = query.filter(self._get_transaction_model().card_id == card_id)
            
            results = query.group_by(
                extract('month', self._get_transaction_model().transaction_date)
            ).order_by('month').all()
            
            # 填充所有月份（没有数据的月份用0填充）
            trends = []
            result_dict = {result.month: result for result in results}
            
            for month in range(1, 13):
                result = result_dict.get(month)
                if result:
                    trends.append(MonthlyTransactionTrend(
                        year=year,
                        month=int(result.month),
                        transaction_count=result.transaction_count,
                        total_amount=result.total_amount or 0,
                        expense_amount=result.expense_amount or 0,
                        income_amount=result.income_amount or 0
                    ))
                else:
                    trends.append(MonthlyTransactionTrend(
                        year=year,
                        month=month,
                        transaction_count=0,
                        total_amount=Decimal("0"),
                        expense_amount=Decimal("0"),
                        income_amount=Decimal("0")
                    ))
            
            logger.info(f"月度趋势获取成功，共 {len(trends)} 个月")
            return trends
            
        except Exception as e:
            logger.error(f"获取月度趋势失败: {str(e)}")
            raise Exception(f"获取月度趋势失败: {str(e)}")

    # ==================== 年费进度相关 ====================

    def _update_annual_fee_progress(self, card_id: UUID, transaction_amount: Decimal):
        """
        更新年费减免进度
        
        Args:
            card_id: 信用卡ID
            transaction_amount: 交易金额
        """
        try:
            current_year = date.today().year
            
            # 获取年费记录
            annual_fee_record = self.db.query(self._get_annual_fee_record_model()).filter(
                and_(
                    self._get_annual_fee_record_model().card_id == card_id,
                    self._get_annual_fee_record_model().fee_year == current_year
                )
            ).first()
            
            if not annual_fee_record:
                return
            
            # 获取年费规则
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id
            ).first()
            
            if not card or not card.annual_fee_rule_id:
                return
            
            rule = self.db.query(self._get_annual_fee_rule_model()).filter(
                self._get_annual_fee_rule_model().id == card.annual_fee_rule_id
            ).first()
            
            if not rule:
                return
            
            # 根据规则类型更新进度
            from models.annual_fee import FeeType
            
            if rule.fee_type == FeeType.TRANSACTION_COUNT:
                # 刷卡次数：增加1次
                annual_fee_record.current_progress += 1
            elif rule.fee_type == FeeType.TRANSACTION_AMOUNT:
                # 刷卡金额：增加交易金额
                annual_fee_record.current_progress += transaction_amount
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"更新年费进度失败: {str(e)}")

    def _recalculate_annual_fee_progress(self, card_id: UUID):
        """
        重新计算年费减免进度
        
        Args:
            card_id: 信用卡ID
        """
        try:
            current_year = date.today().year
            
            # 获取年费记录和规则
            annual_fee_record = self.db.query(self._get_annual_fee_record_model()).filter(
                and_(
                    self._get_annual_fee_record_model().card_id == card_id,
                    self._get_annual_fee_record_model().fee_year == current_year
                )
            ).first()
            
            if not annual_fee_record:
                return
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id
            ).first()
            
            if not card or not card.annual_fee_rule_id:
                return
            
            rule = self.db.query(self._get_annual_fee_rule_model()).filter(
                self._get_annual_fee_rule_model().id == card.annual_fee_rule_id
            ).first()
            
            if not rule:
                return
            
            # 获取当年所有有效消费交易
            start_of_year = datetime(current_year, 1, 1)
            end_of_year = datetime(current_year, 12, 31, 23, 59, 59)
            
            valid_transactions = self.db.query(self._get_transaction_model()).filter(
                and_(
                    self._get_transaction_model().card_id == card_id,
                    self._get_transaction_model().transaction_type == TransactionType.EXPENSE,
                    self._get_transaction_model().status == TransactionStatus.COMPLETED,
                    self._get_transaction_model().transaction_date >= start_of_year,
                    self._get_transaction_model().transaction_date <= end_of_year
                )
            ).all()
            
            # 根据规则类型重新计算进度
            from models.annual_fee import FeeType
            
            if rule.fee_type == FeeType.TRANSACTION_COUNT:
                # 刷卡次数
                annual_fee_record.current_progress = len(valid_transactions)
            elif rule.fee_type == FeeType.TRANSACTION_AMOUNT:
                # 刷卡金额
                annual_fee_record.current_progress = sum(t.amount for t in valid_transactions)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"重新计算年费进度失败: {str(e)}")

    # ==================== 辅助方法 ====================

    def _calculate_points(self, amount: Decimal, rate: Decimal = Decimal("1.0")) -> Decimal:
        """
        计算积分
        
        Args:
            amount: 交易金额
            rate: 积分倍率
            
        Returns:
            Decimal: 获得积分数
        """
        # 默认规则：1元 = 1积分
        base_points = amount * Decimal("1.0")
        return base_points * rate

    def _create_transaction_db(self, transaction_data: dict):
        """创建交易记录数据库对象"""
        from db_models.transactions import Transaction as TransactionDB
        return TransactionDB(**transaction_data)

    def _get_transaction_model(self):
        """获取交易记录数据库模型"""
        from db_models.transactions import Transaction as TransactionDB
        return TransactionDB

    def _get_credit_card_model(self):
        """获取信用卡数据库模型"""
        from db_models.cards import CreditCard
        return CreditCard

    def _get_annual_fee_record_model(self):
        """获取年费记录数据库模型"""
        from db_models.annual_fee import AnnualFeeRecord
        return AnnualFeeRecord

    def _get_annual_fee_rule_model(self):
        """获取年费规则数据库模型"""
        from db_models.annual_fee import AnnualFeeRule
        return AnnualFeeRule

    def _get_card_model(self):
        """获取信用卡数据库模型"""
        from db_models.cards import CreditCard
        return CreditCard 