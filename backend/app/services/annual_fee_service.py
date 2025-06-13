"""
年费服务
提供年费规则管理、减免评估、记录管理等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import calendar

from app.models.database.annual_fee import AnnualFeeRule, AnnualFeeRecord
from app.models.database.card import CreditCard
from app.models.database.transaction import Transaction
from app.models.schemas.annual_fee import (
    AnnualFeeRuleCreate, AnnualFeeRuleUpdate, AnnualFeeRuleResponse,
    AnnualFeeRecordCreate, AnnualFeeRecordUpdate, AnnualFeeRecordResponse,
    AnnualFeeStatisticsResponse, WaiverEvaluationResponse
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, ValidationError, BusinessRuleError
)
from app.core.logging.logger import app_logger as logger


class AnnualFeeService:
    """年费服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== 年费规则管理 ==========
    
    def create_annual_fee_rule(self, user_id: UUID, rule_data: AnnualFeeRuleCreate) -> AnnualFeeRuleResponse:
        """创建年费规则"""
        try:
            # 验证信用卡是否属于用户
            card = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.id == rule_data.card_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not card:
                raise ResourceNotFoundError("信用卡不存在或不属于当前用户")
            
            # 检查是否已存在相同年份的规则
            existing_rule = self.db.query(AnnualFeeRule).filter(
                and_(
                    AnnualFeeRule.card_id == rule_data.card_id,
                    AnnualFeeRule.fee_year == rule_data.fee_year
                )
            ).first()
            
            if existing_rule:
                raise BusinessRuleError(f"信用卡在{rule_data.fee_year}年的年费规则已存在")
            
            # 创建年费规则
            rule = AnnualFeeRule(
                card_id=rule_data.card_id,
                fee_year=rule_data.fee_year,
                base_fee=rule_data.base_fee,
                waiver_type=rule_data.waiver_type,
                waiver_condition_value=rule_data.waiver_condition_value,
                waiver_condition_unit=rule_data.waiver_condition_unit,
                points_per_yuan=rule_data.points_per_yuan,
                is_active=rule_data.is_active,
                notes=rule_data.notes
            )
            
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"创建年费规则成功: {rule.id}, 用户: {user_id}")
            return self._to_rule_response(rule)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建年费规则失败: 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_annual_fee_rule(self, user_id: UUID, rule_id: UUID) -> AnnualFeeRuleResponse:
        """获取年费规则详情"""
        rule = self.db.query(AnnualFeeRule).join(CreditCard).filter(
            and_(
                AnnualFeeRule.id == rule_id,
                CreditCard.user_id == user_id
            )
        ).first()
        
        if not rule:
            raise ResourceNotFoundError("年费规则不存在")
        
        return self._to_rule_response(rule)
    
    def update_annual_fee_rule(self, user_id: UUID, rule_id: UUID, 
                              rule_data: AnnualFeeRuleUpdate) -> AnnualFeeRuleResponse:
        """更新年费规则"""
        try:
            rule = self.db.query(AnnualFeeRule).join(CreditCard).filter(
                and_(
                    AnnualFeeRule.id == rule_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not rule:
                raise ResourceNotFoundError("年费规则不存在")
            
            # 更新字段
            update_data = rule_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(rule, field, value)
            
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"更新年费规则成功: {rule_id}, 用户: {user_id}")
            return self._to_rule_response(rule)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新年费规则失败: {rule_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def delete_annual_fee_rule(self, user_id: UUID, rule_id: UUID) -> bool:
        """删除年费规则"""
        try:
            rule = self.db.query(AnnualFeeRule).join(CreditCard).filter(
                and_(
                    AnnualFeeRule.id == rule_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not rule:
                raise ResourceNotFoundError("年费规则不存在")
            
            # 检查是否有关联的年费记录
            record_count = self.db.query(AnnualFeeRecord).filter(
                AnnualFeeRecord.rule_id == rule_id
            ).count()
            
            if record_count > 0:
                raise BusinessRuleError("存在关联的年费记录，无法删除规则")
            
            self.db.delete(rule)
            self.db.commit()
            
            logger.info(f"删除年费规则成功: {rule_id}, 用户: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除年费规则失败: {rule_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_user_annual_fee_rules(self, user_id: UUID, page: int = 1, page_size: int = 20,
                                 card_id: Optional[UUID] = None, fee_year: Optional[int] = None,
                                 waiver_type: Optional[str] = None, is_active: Optional[bool] = None) -> Tuple[List[AnnualFeeRuleResponse], int]:
        """获取用户年费规则列表（支持筛选和分页）"""
        
        query = self.db.query(AnnualFeeRule).join(CreditCard).filter(
            CreditCard.user_id == user_id
        )
        
        # 应用筛选条件
        if card_id:
            query = query.filter(AnnualFeeRule.card_id == card_id)
        
        if fee_year:
            query = query.filter(AnnualFeeRule.fee_year == fee_year)
        
        if waiver_type:
            query = query.filter(AnnualFeeRule.waiver_type == waiver_type)
        
        if is_active is not None:
            query = query.filter(AnnualFeeRule.is_active == is_active)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        rules = query.order_by(desc(AnnualFeeRule.fee_year), desc(AnnualFeeRule.created_at))\
                     .offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()
        
        rule_responses = [self._to_rule_response(rule) for rule in rules]
        
        logger.info(f"获取用户年费规则列表成功: 用户: {user_id}, 总数: {total}")
        return rule_responses, total
    
    # ========== 年费记录管理 ==========
    
    def create_annual_fee_record(self, user_id: UUID, record_data: AnnualFeeRecordCreate) -> AnnualFeeRecordResponse:
        """创建年费记录"""
        try:
            # 验证年费规则是否属于用户
            rule = self.db.query(AnnualFeeRule).join(CreditCard).filter(
                and_(
                    AnnualFeeRule.id == record_data.rule_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not rule:
                raise ResourceNotFoundError("年费规则不存在或不属于当前用户")
            
            # 检查是否已存在记录
            existing_record = self.db.query(AnnualFeeRecord).filter(
                AnnualFeeRecord.rule_id == record_data.rule_id
            ).first()
            
            if existing_record:
                raise BusinessRuleError("该年费规则已存在记录")
            
            # 创建年费记录
            record = AnnualFeeRecord(
                rule_id=record_data.rule_id,
                fee_year=rule.fee_year,
                base_fee=record_data.base_fee or rule.base_fee,
                actual_fee=record_data.actual_fee,
                waiver_amount=record_data.waiver_amount or Decimal('0'),
                waiver_reason=record_data.waiver_reason,
                status=record_data.status,
                due_date=record_data.due_date,
                paid_date=record_data.paid_date,
                notes=record_data.notes
            )
            
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"创建年费记录成功: {record.id}, 用户: {user_id}")
            return self._to_record_response(record)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建年费记录失败: 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_annual_fee_record(self, user_id: UUID, record_id: UUID) -> AnnualFeeRecordResponse:
        """获取年费记录详情"""
        record = self.db.query(AnnualFeeRecord).join(AnnualFeeRule).join(CreditCard).filter(
            and_(
                AnnualFeeRecord.id == record_id,
                CreditCard.user_id == user_id
            )
        ).first()
        
        if not record:
            raise ResourceNotFoundError("年费记录不存在")
        
        return self._to_record_response(record)
    
    def update_annual_fee_record(self, user_id: UUID, record_id: UUID, 
                                record_data: AnnualFeeRecordUpdate) -> AnnualFeeRecordResponse:
        """更新年费记录"""
        try:
            record = self.db.query(AnnualFeeRecord).join(AnnualFeeRule).join(CreditCard).filter(
                and_(
                    AnnualFeeRecord.id == record_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not record:
                raise ResourceNotFoundError("年费记录不存在")
            
            # 更新字段
            update_data = record_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(record, field, value)
            
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"更新年费记录成功: {record_id}, 用户: {user_id}")
            return self._to_record_response(record)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新年费记录失败: {record_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def delete_annual_fee_record(self, user_id: UUID, record_id: UUID) -> bool:
        """删除年费记录"""
        try:
            record = self.db.query(AnnualFeeRecord).join(AnnualFeeRule).join(CreditCard).filter(
                and_(
                    AnnualFeeRecord.id == record_id,
                    CreditCard.user_id == user_id
                )
            ).first()
            
            if not record:
                raise ResourceNotFoundError("年费记录不存在")
            
            self.db.delete(record)
            self.db.commit()
            
            logger.info(f"删除年费记录成功: {record_id}, 用户: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除年费记录失败: {record_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_user_annual_fee_records(self, user_id: UUID, page: int = 1, page_size: int = 20,
                                   card_id: Optional[UUID] = None, fee_year: Optional[int] = None,
                                   status: Optional[str] = None) -> Tuple[List[AnnualFeeRecordResponse], int]:
        """获取用户年费记录列表（支持筛选和分页）"""
        
        query = self.db.query(AnnualFeeRecord).join(AnnualFeeRule).join(CreditCard).filter(
            CreditCard.user_id == user_id
        )
        
        # 应用筛选条件
        if card_id:
            query = query.filter(AnnualFeeRule.card_id == card_id)
        
        if fee_year:
            query = query.filter(AnnualFeeRecord.fee_year == fee_year)
        
        if status:
            query = query.filter(AnnualFeeRecord.status == status)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        records = query.order_by(desc(AnnualFeeRecord.fee_year), desc(AnnualFeeRecord.created_at))\
                       .offset((page - 1) * page_size)\
                       .limit(page_size)\
                       .all()
        
        record_responses = [self._to_record_response(record) for record in records]
        
        logger.info(f"获取用户年费记录列表成功: 用户: {user_id}, 总数: {total}")
        return record_responses, total
    
    # ========== 年费减免评估 ==========
    
    def evaluate_waiver_eligibility(self, user_id: UUID, rule_id: UUID) -> WaiverEvaluationResponse:
        """评估年费减免资格"""
        
        # 获取年费规则
        rule = self.db.query(AnnualFeeRule).join(CreditCard).filter(
            and_(
                AnnualFeeRule.id == rule_id,
                CreditCard.user_id == user_id
            )
        ).first()
        
        if not rule:
            raise ResourceNotFoundError("年费规则不存在")
        
        # 如果是刚性年费，无法减免
        if rule.waiver_type == 'rigid':
            return WaiverEvaluationResponse(
                rule_id=rule_id,
                waiver_type=rule.waiver_type,
                is_eligible=False,
                current_progress=0,
                required_target=0,
                completion_percentage=0.0,
                estimated_waiver_amount=Decimal('0'),
                evaluation_message="刚性年费，无法减免"
            )
        
        # 计算当前年度的交易数据
        year_start = datetime(rule.fee_year, 1, 1)
        year_end = datetime(rule.fee_year, 12, 31, 23, 59, 59)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.card_id == rule.card_id,
                Transaction.transaction_date >= year_start,
                Transaction.transaction_date <= year_end,
                Transaction.transaction_type == 'expense'
            )
        ).all()
        
        # 根据减免类型评估
        if rule.waiver_type == 'spending_amount':
            # 刷卡金额减免
            current_spending = sum(t.amount for t in transactions)
            required_spending = rule.waiver_condition_value
            
            is_eligible = current_spending >= required_spending
            completion_percentage = (current_spending / required_spending * 100) if required_spending > 0 else 0
            
            return WaiverEvaluationResponse(
                rule_id=rule_id,
                waiver_type=rule.waiver_type,
                is_eligible=is_eligible,
                current_progress=float(current_spending),
                required_target=float(required_spending),
                completion_percentage=min(completion_percentage, 100.0),
                estimated_waiver_amount=rule.base_fee if is_eligible else Decimal('0'),
                evaluation_message=f"当前消费金额: ¥{current_spending:,.2f}, 需要: ¥{required_spending:,.2f}"
            )
        
        elif rule.waiver_type == 'transaction_count':
            # 刷卡次数减免
            current_count = len(transactions)
            required_count = int(rule.waiver_condition_value)
            
            is_eligible = current_count >= required_count
            completion_percentage = (current_count / required_count * 100) if required_count > 0 else 0
            
            return WaiverEvaluationResponse(
                rule_id=rule_id,
                waiver_type=rule.waiver_type,
                is_eligible=is_eligible,
                current_progress=current_count,
                required_target=required_count,
                completion_percentage=min(completion_percentage, 100.0),
                estimated_waiver_amount=rule.base_fee if is_eligible else Decimal('0'),
                evaluation_message=f"当前交易次数: {current_count}次, 需要: {required_count}次"
            )
        
        elif rule.waiver_type == 'points_redemption':
            # 积分兑换减免
            total_points = sum(t.points_earned or 0 for t in transactions)
            required_points = int(rule.waiver_condition_value)
            
            is_eligible = total_points >= required_points
            completion_percentage = (total_points / required_points * 100) if required_points > 0 else 0
            
            return WaiverEvaluationResponse(
                rule_id=rule_id,
                waiver_type=rule.waiver_type,
                is_eligible=is_eligible,
                current_progress=total_points,
                required_target=required_points,
                completion_percentage=min(completion_percentage, 100.0),
                estimated_waiver_amount=rule.base_fee if is_eligible else Decimal('0'),
                evaluation_message=f"当前积分: {total_points}分, 需要: {required_points}分"
            )
        
        else:
            return WaiverEvaluationResponse(
                rule_id=rule_id,
                waiver_type=rule.waiver_type,
                is_eligible=False,
                current_progress=0,
                required_target=0,
                completion_percentage=0.0,
                estimated_waiver_amount=Decimal('0'),
                evaluation_message="未知的减免类型"
            )
    
    # ========== 年费统计分析 ==========
    
    def get_annual_fee_statistics(self, user_id: UUID, year: Optional[int] = None) -> AnnualFeeStatisticsResponse:
        """获取年费统计数据"""
        
        if not year:
            year = datetime.now().year
        
        # 查询用户的年费记录
        records = self.db.query(AnnualFeeRecord).join(AnnualFeeRule).join(CreditCard).filter(
            and_(
                CreditCard.user_id == user_id,
                AnnualFeeRecord.fee_year == year
            )
        ).all()
        
        if not records:
            return AnnualFeeStatisticsResponse(
                year=year,
                total_cards_with_fee=0,
                total_base_fee=Decimal('0'),
                total_actual_fee=Decimal('0'),
                total_waived_amount=Decimal('0'),
                waiver_rate=Decimal('0'),
                status_distribution={},
                waiver_type_distribution={},
                upcoming_due_fees=[]
            )
        
        # 基础统计
        total_cards_with_fee = len(records)
        total_base_fee = sum(record.base_fee for record in records)
        total_actual_fee = sum(record.actual_fee for record in records)
        total_waived_amount = sum(record.waiver_amount for record in records)
        
        waiver_rate = (total_waived_amount / total_base_fee * 100) if total_base_fee > 0 else Decimal('0')
        
        # 状态分布
        status_distribution = {}
        for record in records:
            status = record.status
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # 减免类型分布
        waiver_type_distribution = {}
        for record in records:
            waiver_type = record.rule.waiver_type
            waiver_type_distribution[waiver_type] = waiver_type_distribution.get(waiver_type, 0) + 1
        
        # 即将到期的年费
        upcoming_due_fees = []
        current_date = datetime.now().date()
        for record in records:
            if record.status == 'pending' and record.due_date:
                days_until_due = (record.due_date - current_date).days
                if days_until_due <= 30:  # 30天内到期
                    upcoming_due_fees.append({
                        'record_id': str(record.id),
                        'card_name': record.rule.card.card_name,
                        'base_fee': float(record.base_fee),
                        'actual_fee': float(record.actual_fee),
                        'due_date': record.due_date,
                        'days_until_due': days_until_due
                    })
        
        # 按到期时间排序
        upcoming_due_fees.sort(key=lambda x: x['days_until_due'])
        
        return AnnualFeeStatisticsResponse(
            year=year,
            total_cards_with_fee=total_cards_with_fee,
            total_base_fee=total_base_fee,
            total_actual_fee=total_actual_fee,
            total_waived_amount=total_waived_amount,
            waiver_rate=waiver_rate,
            status_distribution=status_distribution,
            waiver_type_distribution=waiver_type_distribution,
            upcoming_due_fees=upcoming_due_fees
        )
    
    # ========== 私有方法 ==========
    
    def _to_rule_response(self, rule: AnnualFeeRule) -> AnnualFeeRuleResponse:
        """转换为年费规则响应模型"""
        return AnnualFeeRuleResponse(
            id=rule.id,
            card_id=rule.card_id,
            fee_year=rule.fee_year,
            base_fee=rule.base_fee,
            waiver_type=rule.waiver_type,
            waiver_condition_value=rule.waiver_condition_value,
            waiver_condition_unit=rule.waiver_condition_unit,
            points_per_yuan=rule.points_per_yuan,
            is_active=rule.is_active,
            notes=rule.notes,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            # 关联数据
            card_name=rule.card.card_name if rule.card else None
        )
    
    def _to_record_response(self, record: AnnualFeeRecord) -> AnnualFeeRecordResponse:
        """转换为年费记录响应模型"""
        return AnnualFeeRecordResponse(
            id=record.id,
            rule_id=record.rule_id,
            fee_year=record.fee_year,
            base_fee=record.base_fee,
            actual_fee=record.actual_fee,
            waiver_amount=record.waiver_amount,
            waiver_reason=record.waiver_reason,
            status=record.status,
            due_date=record.due_date,
            paid_date=record.paid_date,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at,
            # 关联数据
            card_name=record.rule.card.card_name if record.rule and record.rule.card else None,
            waiver_type=record.rule.waiver_type if record.rule else None
        ) 