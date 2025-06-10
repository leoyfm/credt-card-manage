"""
交易管理服务层

包含交易记录相关的业务逻辑，包括增删改查、统计分析、年费进度更新等功能。
新架构下的交易服务。
"""

import logging
from datetime import datetime, date, UTC
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func, extract, desc, case
from sqlalchemy.orm import Session

from app.models.schemas.transaction import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    TransactionQueryFilter,
    TransactionBatchOperation,
    TransactionStats,
    TransactionSummary,
    CategoryStats,
    MonthlyTrend,
    TransactionType,
    TransactionStatus
)
from app.models.database.transaction import Transaction as DBTransaction
from app.models.database.card import Card as DBCard
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class TransactionsService:
    """交易管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction_data: TransactionCreate, user_id: UUID) -> Transaction:
        """
        创建交易记录
        
        Args:
            transaction_data: 交易数据
            user_id: 用户ID
            
        Returns:
            Transaction: 创建的交易记录
        """
        try:
            logger.info(f"创建交易记录", extra={
                "user_id": str(user_id),
                "card_id": str(transaction_data.card_id),
                "amount": float(transaction_data.amount),
                "type": transaction_data.transaction_type.value
            })
            
            # 验证信用卡是否属于该用户
            card = self.db.query(DBCard).filter(
                and_(
                    DBCard.id == transaction_data.card_id,
                    DBCard.user_id == user_id,
                    DBCard.status != "closed"
                )
            ).first()
            
            if not card:
                raise ValueError("信用卡不存在或不属于该用户")
            
            # 创建交易记录
            transaction_dict = transaction_data.model_dump(exclude_unset=True)
            transaction_dict['user_id'] = user_id
            
            # 设置默认值
            if 'transaction_date' not in transaction_dict:
                transaction_dict['transaction_date'] = datetime.now(UTC)
            if 'status' not in transaction_dict:
                transaction_dict['status'] = TransactionStatus.COMPLETED
            
            # 自动计算积分和返现
            if transaction_data.transaction_type == TransactionType.EXPENSE:
                transaction_dict['points_earned'] = self._calculate_points(
                    transaction_data.amount, 
                    card.points_rate or Decimal("1.0")
                )
                transaction_dict['cashback_earned'] = self._calculate_cashback(
                    transaction_data.amount,
                    card.cashback_rate or Decimal("0.0")
                )
            
            db_transaction = DBTransaction(**transaction_dict)
            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)
            
            # 更新信用卡使用额度
            if transaction_data.transaction_type == TransactionType.EXPENSE:
                self._update_card_used_limit(card, transaction_data.amount)
            
            logger.info(f"交易记录创建成功", extra={
                "transaction_id": str(db_transaction.id),
                "user_id": str(user_id)
            })
            
            return Transaction.model_validate(db_transaction)
            
        except Exception as e:
            logger.error(f"创建交易记录失败: {str(e)}", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            self.db.rollback()
            raise

    def get_transactions(
        self,
        user_id: UUID,
        filter_params: TransactionQueryFilter,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Transaction], int]:
        """
        获取交易记录列表
        
        Args:
            user_id: 用户ID
            filter_params: 查询过滤参数
            skip: 跳过记录数
            limit: 限制记录数
            
        Returns:
            交易记录列表和总数
        """
        try:
            logger.info(f"获取交易记录列表", extra={
                "user_id": str(user_id),
                "skip": skip,
                "limit": limit
            })
            
            query = self.db.query(DBTransaction).filter(
                DBTransaction.user_id == user_id
            )
            
            # 应用过滤条件
            query = self._apply_transaction_filters(query, filter_params)
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据
            transactions = query.order_by(
                desc(DBTransaction.transaction_date),
                desc(DBTransaction.created_at)
            ).offset(skip).limit(limit).all()
            
            logger.info(f"获取交易记录成功", extra={
                "count": len(transactions),
                "total": total,
                "user_id": str(user_id)
            })
            
            return [Transaction.model_validate(t) for t in transactions], total
            
        except Exception as e:
            logger.error(f"获取交易记录失败: {str(e)}", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            raise

    def get_transaction_by_id(self, transaction_id: UUID, user_id: UUID) -> Optional[Transaction]:
        """获取单个交易记录"""
        try:
            transaction = self.db.query(DBTransaction).filter(
                and_(
                    DBTransaction.id == transaction_id,
                    DBTransaction.user_id == user_id
                )
            ).first()
            
            if not transaction:
                return None
                
            return Transaction.model_validate(transaction)
            
        except Exception as e:
            logger.error(f"获取交易记录失败: {str(e)}")
            raise

    def update_transaction(
        self, 
        transaction_id: UUID, 
        user_id: UUID,
        transaction_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """更新交易记录"""
        try:
            transaction = self.db.query(DBTransaction).filter(
                and_(
                    DBTransaction.id == transaction_id,
                    DBTransaction.user_id == user_id
                )
            ).first()
            
            if not transaction:
                return None
            
            # 保存原始金额用于更新卡片额度
            original_amount = transaction.amount
            original_type = transaction.transaction_type
            
            # 更新字段
            update_data = transaction_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(transaction, field, value)
            
            transaction.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(transaction)
            
            # 更新信用卡使用额度
            if original_type == TransactionType.EXPENSE or transaction.transaction_type == TransactionType.EXPENSE:
                card = self.db.query(DBCard).filter(DBCard.id == transaction.card_id).first()
                if card:
                    # 恢复原金额，重新计算
                    if original_type == TransactionType.EXPENSE:
                        card.used_limit = max(Decimal("0"), card.used_limit - original_amount)
                    if transaction.transaction_type == TransactionType.EXPENSE:
                        card.used_limit += transaction.amount
                        card.available_limit = card.credit_limit - card.used_limit
                    self.db.commit()
            
            logger.info(f"交易记录更新成功", extra={
                "transaction_id": str(transaction_id),
                "user_id": str(user_id)
            })
            
            return Transaction.model_validate(transaction)
            
        except Exception as e:
            logger.error(f"更新交易记录失败: {str(e)}")
            self.db.rollback()
            raise

    def delete_transaction(self, transaction_id: UUID, user_id: UUID) -> bool:
        """删除交易记录"""
        try:
            transaction = self.db.query(DBTransaction).filter(
                and_(
                    DBTransaction.id == transaction_id,
                    DBTransaction.user_id == user_id
                )
            ).first()
            
            if not transaction:
                return False
            
            # 恢复信用卡使用额度
            if transaction.transaction_type == TransactionType.EXPENSE:
                card = self.db.query(DBCard).filter(DBCard.id == transaction.card_id).first()
                if card:
                    card.used_limit = max(Decimal("0"), card.used_limit - transaction.amount)
                    card.available_limit = card.credit_limit - card.used_limit
            
            self.db.delete(transaction)
            self.db.commit()
            
            logger.info(f"交易记录删除成功", extra={
                "transaction_id": str(transaction_id),
                "user_id": str(user_id)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"删除交易记录失败: {str(e)}")
            self.db.rollback()
            raise

    def get_transaction_stats(
        self,
        user_id: UUID,
        card_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TransactionStats:
        """获取交易统计"""
        try:
            query = self.db.query(DBTransaction).filter(
                DBTransaction.user_id == user_id
            )
            
            if card_id:
                query = query.filter(DBTransaction.card_id == card_id)
            if start_date:
                query = query.filter(DBTransaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(DBTransaction.transaction_date <= end_date)
            
            # 基础统计
            total_count = query.count()
            
            expense_query = query.filter(DBTransaction.transaction_type == TransactionType.EXPENSE)
            income_query = query.filter(DBTransaction.transaction_type == TransactionType.INCOME)
            
            total_expense = expense_query.with_entities(func.sum(DBTransaction.amount)).scalar() or Decimal("0")
            total_income = income_query.with_entities(func.sum(DBTransaction.amount)).scalar() or Decimal("0")
            
            expense_count = expense_query.count()
            income_count = income_query.count()
            
            # 积分和返现统计
            total_points = query.with_entities(func.sum(DBTransaction.points_earned)).scalar() or 0
            total_cashback = query.with_entities(func.sum(DBTransaction.cashback_earned)).scalar() or Decimal("0")
            
            # 平均金额
            avg_transaction = query.with_entities(func.avg(DBTransaction.amount)).scalar() or Decimal("0")
            avg_expense = expense_query.with_entities(func.avg(DBTransaction.amount)).scalar() or Decimal("0")
            
            return TransactionStats(
                total_count=total_count,
                expense_count=expense_count,
                income_count=income_count,
                total_expense=total_expense,
                total_income=total_income,
                net_amount=total_income - total_expense,
                avg_transaction=avg_transaction,
                avg_expense=avg_expense,
                total_points_earned=total_points,
                total_cashback_earned=total_cashback
            )
            
        except Exception as e:
            logger.error(f"获取交易统计失败: {str(e)}")
            raise

    def get_category_stats(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CategoryStats]:
        """获取分类统计"""
        try:
            query = self.db.query(
                DBTransaction.category,
                func.count(DBTransaction.id).label('count'),
                func.sum(DBTransaction.amount).label('total_amount'),
                func.avg(DBTransaction.amount).label('avg_amount')
            ).filter(
                DBTransaction.user_id == user_id,
                DBTransaction.transaction_type == TransactionType.EXPENSE
            ).group_by(DBTransaction.category)
            
            if start_date:
                query = query.filter(DBTransaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(DBTransaction.transaction_date <= end_date)
            
            results = query.all()
            
            category_stats = []
            for result in results:
                category_stats.append(CategoryStats(
                    category=result.category or "其他",
                    count=result.count,
                    total_amount=result.total_amount or Decimal("0"),
                    avg_amount=result.avg_amount or Decimal("0")
                ))
            
            # 按金额排序
            category_stats.sort(key=lambda x: x.total_amount, reverse=True)
            
            return category_stats
            
        except Exception as e:
            logger.error(f"获取分类统计失败: {str(e)}")
            raise

    def get_monthly_trends(
        self,
        user_id: UUID,
        year: Optional[int] = None,
        card_id: Optional[UUID] = None
    ) -> List[MonthlyTrend]:
        """获取月度趋势"""
        try:
            if not year:
                year = datetime.now().year
            
            query = self.db.query(
                extract('month', DBTransaction.transaction_date).label('month'),
                func.count(DBTransaction.id).label('count'),
                func.sum(case(
                    (DBTransaction.transaction_type == TransactionType.EXPENSE, DBTransaction.amount),
                    else_=0
                )).label('expense'),
                func.sum(case(
                    (DBTransaction.transaction_type == TransactionType.INCOME, DBTransaction.amount),
                    else_=0
                )).label('income')
            ).filter(
                DBTransaction.user_id == user_id,
                extract('year', DBTransaction.transaction_date) == year
            ).group_by(extract('month', DBTransaction.transaction_date))
            
            if card_id:
                query = query.filter(DBTransaction.card_id == card_id)
            
            results = query.all()
            
            # 创建12个月的数据，未有数据的月份填0
            monthly_data = {}
            for result in results:
                monthly_data[int(result.month)] = MonthlyTrend(
                    month=int(result.month),
                    year=year,
                    transaction_count=result.count,
                    total_expense=result.expense or Decimal("0"),
                    total_income=result.income or Decimal("0"),
                    net_amount=(result.income or Decimal("0")) - (result.expense or Decimal("0"))
                )
            
            # 填充缺失月份
            trends = []
            for month in range(1, 13):
                if month in monthly_data:
                    trends.append(monthly_data[month])
                else:
                    trends.append(MonthlyTrend(
                        month=month,
                        year=year,
                        transaction_count=0,
                        total_expense=Decimal("0"),
                        total_income=Decimal("0"),
                        net_amount=Decimal("0")
                    ))
            
            return trends
            
        except Exception as e:
            logger.error(f"获取月度趋势失败: {str(e)}")
            raise

    def batch_operations(
        self, 
        user_id: UUID, 
        operation: TransactionBatchOperation
    ) -> Dict[str, Any]:
        """批量操作"""
        try:
            if operation.action == "delete":
                deleted_count = 0
                for transaction_id in operation.transaction_ids:
                    if self.delete_transaction(transaction_id, user_id):
                        deleted_count += 1
                
                return {"deleted_count": deleted_count, "total_requested": len(operation.transaction_ids)}
            
            elif operation.action == "update_category":
                if not operation.update_data or "category" not in operation.update_data:
                    raise ValueError("批量更新分类需要提供category字段")
                
                updated_count = self.db.query(DBTransaction).filter(
                    and_(
                        DBTransaction.id.in_(operation.transaction_ids),
                        DBTransaction.user_id == user_id
                    )
                ).update(
                    {"category": operation.update_data["category"], "updated_at": datetime.now(UTC)},
                    synchronize_session=False
                )
                
                self.db.commit()
                return {"updated_count": updated_count, "total_requested": len(operation.transaction_ids)}
            
            else:
                raise ValueError(f"不支持的批量操作: {operation.action}")
                
        except Exception as e:
            logger.error(f"批量操作失败: {str(e)}")
            self.db.rollback()
            raise

    def _apply_transaction_filters(self, query, filter_params: TransactionQueryFilter):
        """应用交易查询过滤条件"""
        if filter_params.card_id:
            query = query.filter(DBTransaction.card_id == filter_params.card_id)
        
        if filter_params.transaction_type:
            query = query.filter(DBTransaction.transaction_type == filter_params.transaction_type)
        
        if filter_params.category:
            query = query.filter(DBTransaction.category == filter_params.category)
        
        if filter_params.status:
            query = query.filter(DBTransaction.status == filter_params.status)
        
        if filter_params.start_date:
            query = query.filter(DBTransaction.transaction_date >= filter_params.start_date)
        
        if filter_params.end_date:
            query = query.filter(DBTransaction.transaction_date <= filter_params.end_date)
        
        if filter_params.min_amount:
            query = query.filter(DBTransaction.amount >= filter_params.min_amount)
        
        if filter_params.max_amount:
            query = query.filter(DBTransaction.amount <= filter_params.max_amount)
        
        if filter_params.merchant_name:
            query = query.filter(DBTransaction.merchant_name.ilike(f"%{filter_params.merchant_name}%"))
        
        # 关键词搜索
        if filter_params.keyword:
            keyword_filter = f"%{filter_params.keyword}%"
            query = query.filter(
                or_(
                    DBTransaction.merchant_name.ilike(keyword_filter),
                    DBTransaction.description.ilike(keyword_filter),
                    DBTransaction.notes.ilike(keyword_filter),
                    DBTransaction.location.ilike(keyword_filter)
                )
            )
        
        return query

    def _calculate_points(self, amount: Decimal, rate: Decimal) -> int:
        """计算积分"""
        return int(amount * rate)

    def _calculate_cashback(self, amount: Decimal, rate: Decimal) -> Decimal:
        """计算返现"""
        return amount * rate / Decimal("100")

    def _update_card_used_limit(self, card: DBCard, amount: Decimal):
        """更新信用卡使用额度"""
        try:
            card.used_limit = (card.used_limit or Decimal("0")) + amount
            card.available_limit = card.credit_limit - card.used_limit
            self.db.commit()
        except Exception as e:
            logger.error(f"更新信用卡额度失败: {str(e)}")
            self.db.rollback()
            raise