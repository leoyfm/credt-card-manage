"""
交易服务
提供交易记录的CRUD操作、统计分析、分类管理等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import calendar

from app.models.database.transaction import Transaction, TransactionCategory
from app.models.database.card import CreditCard
from app.models.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionListResponse, TransactionStatisticsResponse,
    CategoryStatisticsResponse, MonthlyTrendResponse
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, ValidationError, BusinessRuleError
)
from app.core.logging.logger import app_logger as  logger
from app.utils.pagination import apply_service_pagination


class TransactionService:
    """交易服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== 交易CRUD操作 ==========
    
    def create_transaction(self, user_id: UUID, transaction_data: TransactionCreate) -> TransactionResponse:
        """创建交易记录"""
        try:
            # 验证信用卡是否属于用户
            card = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.id == transaction_data.card_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not card:
                raise ResourceNotFoundError("信用卡不存在或不属于当前用户")
            
            # 验证交易分类（如果提供）
            if transaction_data.category_id:
                category = self.db.query(TransactionCategory).filter(
                    TransactionCategory.id == transaction_data.category_id
                ).first()
                if not category:
                    raise ResourceNotFoundError("交易分类不存在")
            
            # 创建交易记录
            transaction = Transaction(
                user_id=user_id,
                card_id=transaction_data.card_id,
                category_id=transaction_data.category_id,
                transaction_type=transaction_data.transaction_type,
                amount=transaction_data.amount,
                currency=transaction_data.currency or 'CNY',
                description=transaction_data.description,
                merchant_name=transaction_data.merchant_name,
                merchant_category=transaction_data.merchant_category,
                location=transaction_data.location,
                transaction_date=transaction_data.transaction_date or datetime.now(),
                notes=transaction_data.notes,
                tags=transaction_data.tags or []
            )
            
            # 计算积分和返现（基于信用卡设置）
            if transaction_data.transaction_type == 'expense':
                transaction.points_earned = int(transaction_data.amount * card.points_rate)
                transaction.cashback_earned = transaction_data.amount * card.cashback_rate / 100
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"创建交易记录成功: {transaction.id}, 用户: {user_id}")
            return self._to_transaction_response(transaction)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建交易记录失败: 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_transaction(self, user_id: UUID, transaction_id: UUID) -> TransactionResponse:
        """获取交易详情"""
        transaction = self.db.query(Transaction).filter(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id
            )
        ).first()
        
        if not transaction:
            raise ResourceNotFoundError("交易记录不存在")
        
        return self._to_transaction_response(transaction)
    
    def update_transaction(self, user_id: UUID, transaction_id: UUID, 
                          transaction_data: TransactionUpdate) -> TransactionResponse:
        """更新交易记录"""
        try:
            transaction = self.db.query(Transaction).filter(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id
                )
            ).first()
            
            if not transaction:
                raise ResourceNotFoundError("交易记录不存在")
            
            # 验证信用卡（如果更新）
            if transaction_data.card_id and transaction_data.card_id != transaction.card_id:
                card = self.db.query(CreditCard).filter(
                    and_(
                        CreditCard.id == transaction_data.card_id,
                        CreditCard.user_id == user_id
                    )
                ).first()
                if not card:
                    raise ResourceNotFoundError("信用卡不存在或不属于当前用户")
            
            # 验证交易分类（如果更新）
            if transaction_data.category_id:
                category = self.db.query(TransactionCategory).filter(
                    TransactionCategory.id == transaction_data.category_id
                ).first()
                if not category:
                    raise ResourceNotFoundError("交易分类不存在")
            
            # 更新字段
            update_data = transaction_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(transaction, field, value)
            
            # 重新计算积分和返现（如果金额或卡片变更）
            if transaction_data.amount or transaction_data.card_id:
                card = transaction.card
                if transaction.transaction_type == 'expense':
                    transaction.points_earned = int(transaction.amount * card.points_rate)
                    transaction.cashback_earned = transaction.amount * card.cashback_rate / 100
            
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"更新交易记录成功: {transaction_id}, 用户: {user_id}")
            return self._to_transaction_response(transaction)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新交易记录失败: {transaction_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def delete_transaction(self, user_id: UUID, transaction_id: UUID) -> bool:
        """删除交易记录"""
        try:
            transaction = self.db.query(Transaction).filter(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id
                )
            ).first()
            
            if not transaction:
                raise ResourceNotFoundError("交易记录不存在")
            
            self.db.delete(transaction)
            self.db.commit()
            
            logger.info(f"删除交易记录成功: {transaction_id}, 用户: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除交易记录失败: {transaction_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_user_transactions(self, user_id: UUID, page: int = 1, page_size: int = 20,
                             card_id: Optional[UUID] = None, category_id: Optional[UUID] = None,
                             transaction_type: Optional[str] = None, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None, keyword: Optional[str] = None) -> Tuple[List[TransactionResponse], int]:
        """获取用户交易列表（支持筛选和分页）"""
        
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        # 应用筛选条件
        if card_id:
            query = query.filter(Transaction.card_id == card_id)
        
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        if keyword:
            query = query.filter(
                or_(
                    Transaction.description.ilike(f'%{keyword}%'),
                    Transaction.merchant_name.ilike(f'%{keyword}%'),
                    Transaction.location.ilike(f'%{keyword}%'),
                    Transaction.notes.ilike(f'%{keyword}%')
                )
            )
        
        # 应用分页和排序
        transactions, total = apply_service_pagination(
            query,
            page,
            page_size,
            order_by=desc(Transaction.transaction_date)
        )
        
        transaction_responses = [self._to_transaction_response(t) for t in transactions]
        
        logger.info(f"获取用户交易列表成功: 用户: {user_id}, 总数: {total}")
        return transaction_responses, total
    
    # ========== 交易统计分析 ==========
    
    def get_transaction_statistics(self, user_id: UUID, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> TransactionStatisticsResponse:
        """获取交易统计数据"""
        
        # 默认查询最近30天
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        )
        
        # 基础统计
        total_transactions = query.count()
        
        # 按类型统计
        type_stats = query.with_entities(
            Transaction.transaction_type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.avg(Transaction.amount).label('avg_amount')
        ).group_by(Transaction.transaction_type).all()
        
        # 积分和返现统计
        points_cashback = query.with_entities(
            func.sum(Transaction.points_earned).label('total_points'),
            func.sum(Transaction.cashback_earned).label('total_cashback')
        ).first()
        
        # 按月统计
        monthly_stats = query.with_entities(
            extract('year', Transaction.transaction_date).label('year'),
            extract('month', Transaction.transaction_date).label('month'),
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount')
        ).group_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).order_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).all()
        
        # 构建响应
        type_distribution = {}
        total_expense = Decimal('0')
        total_income = Decimal('0')
        
        for stat in type_stats:
            type_distribution[stat.transaction_type] = {
                'count': stat.count,
                'total_amount': float(stat.total_amount or 0),
                'average_amount': float(stat.avg_amount or 0)
            }
            
            if stat.transaction_type == 'expense':
                total_expense = stat.total_amount or Decimal('0')
            elif stat.transaction_type in ['income', 'refund']:
                total_income += stat.total_amount or Decimal('0')
        
        monthly_trends = []
        for stat in monthly_stats:
            monthly_trends.append({
                'year': int(stat.year),
                'month': int(stat.month),
                'month_name': calendar.month_name[int(stat.month)],
                'transaction_count': stat.count,
                'total_amount': float(stat.total_amount or 0)
            })
        
        return TransactionStatisticsResponse(
            period_start=start_date,
            period_end=end_date,
            total_transactions=total_transactions,
            total_expense=float(total_expense),
            total_income=float(total_income),
            net_amount=float(total_income - total_expense),
            average_transaction=float((total_expense + total_income) / total_transactions) if total_transactions > 0 else 0,
            total_points_earned=int(points_cashback.total_points or 0),
            total_cashback_earned=float(points_cashback.total_cashback or 0),
            type_distribution=type_distribution,
            monthly_trends=monthly_trends
        )
    
    def get_category_statistics(self, user_id: UUID, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> CategoryStatisticsResponse:
        """获取分类统计数据"""
        
        # 默认查询最近30天
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # 查询分类统计
        category_stats = self.db.query(
            TransactionCategory.name.label('category_name'),
            TransactionCategory.icon.label('category_icon'),
            TransactionCategory.color.label('category_color'),
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount'),
            func.avg(Transaction.amount).label('average_amount')
        ).join(
            Transaction, Transaction.category_id == TransactionCategory.id
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
                Transaction.transaction_type == 'expense'  # 只统计支出
            )
        ).group_by(
            TransactionCategory.id,
            TransactionCategory.name,
            TransactionCategory.icon,
            TransactionCategory.color
        ).order_by(desc(func.sum(Transaction.amount))).all()
        
        # 计算总支出用于百分比计算
        total_expense = sum(float(stat.total_amount or 0) for stat in category_stats)
        
        # 构建分类分布
        category_distribution = []
        for stat in category_stats:
            amount = float(stat.total_amount or 0)
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            category_distribution.append({
                'category_name': stat.category_name,
                'category_icon': stat.category_icon,
                'category_color': stat.category_color,
                'transaction_count': stat.transaction_count,
                'total_amount': amount,
                'average_amount': float(stat.average_amount or 0),
                'percentage': round(percentage, 2)
            })
        
        # 获取前5大分类
        top_categories = category_distribution[:5]
        
        return CategoryStatisticsResponse(
            period_start=start_date,
            period_end=end_date,
            total_categories=len(category_distribution),
            total_expense=float(total_expense),
            category_distribution=category_distribution,
            top_categories=top_categories
        )
    
    def get_monthly_trends(self, user_id: UUID, months: int = 12) -> MonthlyTrendResponse:
        """获取月度趋势分析"""
        
        # 计算查询范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # 查询月度数据
        monthly_data = self.db.query(
            extract('year', Transaction.transaction_date).label('year'),
            extract('month', Transaction.transaction_date).label('month'),
            Transaction.transaction_type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total_amount')
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
                    'net_amount': 0.0
                }
            
            if data.transaction_type == 'expense':
                monthly_trends[key]['expense_count'] = data.count
                monthly_trends[key]['expense_amount'] = float(data.total_amount or 0)
            elif data.transaction_type in ['income', 'refund']:
                monthly_trends[key]['income_count'] += data.count
                monthly_trends[key]['income_amount'] += float(data.total_amount or 0)
        
        # 计算净额
        for trend in monthly_trends.values():
            trend['net_amount'] = trend['income_amount'] - trend['expense_amount']
        
        # 转换为列表并排序
        trends_list = list(monthly_trends.values())
        trends_list.sort(key=lambda x: (x['year'], x['month']))
        
        # 计算趋势
        if len(trends_list) >= 2:
            recent_expense = trends_list[-1]['expense_amount']
            previous_expense = trends_list[-2]['expense_amount']
            expense_trend = 'increasing' if recent_expense > previous_expense else 'decreasing' if recent_expense < previous_expense else 'stable'
        else:
            expense_trend = 'stable'
        
        return MonthlyTrendResponse(
            analysis_period=f"{months}个月",
            monthly_trends=trends_list,
            expense_trend=expense_trend,
            total_months=len(trends_list)
        )
    
    # ========== 交易分类管理 ==========
    
    def get_transaction_categories(self) -> List[Dict[str, Any]]:
        """获取交易分类列表"""
        categories = self.db.query(TransactionCategory).filter(
            TransactionCategory.is_active == True
        ).order_by(TransactionCategory.sort_order, TransactionCategory.name).all()
        
        return [
            {
                'id': str(category.id),
                'name': category.name,
                'icon': category.icon,
                'color': category.color,
                'parent_id': str(category.parent_id) if category.parent_id else None,
                'is_system': category.is_system
            }
            for category in categories
        ]
    
    # ========== 私有方法 ==========
    
    def _to_transaction_response(self, transaction: Transaction) -> TransactionResponse:
        """转换为交易响应模型"""
        return TransactionResponse(
            id=transaction.id,
            card_id=transaction.card_id,
            category_id=transaction.category_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            currency=transaction.currency,
            description=transaction.description,
            merchant_name=transaction.merchant_name,
            merchant_category=transaction.merchant_category,
            location=transaction.location,
            points_earned=transaction.points_earned,
            cashback_earned=transaction.cashback_earned,
            status=transaction.status,
            transaction_date=transaction.transaction_date,
            notes=transaction.notes,
            tags=transaction.tags,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            # 关联数据
            card_name=transaction.card.card_name if transaction.card else None,
            category_name=transaction.category.name if transaction.category else None
        ) 