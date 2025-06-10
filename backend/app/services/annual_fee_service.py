"""
年费管理服务层

包含年费规则和记录相关的业务逻辑，包括年费计算、减免规则评估、统计分析等功能。
新架构下的年费服务。
"""

import logging
from datetime import datetime, date, UTC
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func, extract, desc
from sqlalchemy.orm import Session

from app.models.schemas.annual_fee import (
    AnnualFeeRule,
    AnnualFeeRuleCreate,
    AnnualFeeRuleUpdate,
    AnnualFeeRecord,
    AnnualFeeRecordCreate,
    AnnualFeeRecordUpdate,
    AnnualFeeQueryFilter,
    AnnualFeeBatchOperation,
    AnnualFeeStats,
    WaiverAnalysis,
    FeeReminderSettings,
    FeeType,
    WaiverStatus,
    ConditionType
)
from app.models.database.annual_fee import (
    FeeWaiverRule as DBFeeRule,
    AnnualFeeRecord as DBFeeRecord
)
from app.models.database.card import CreditCard as DBCard
from app.models.database.transaction import Transaction as DBTransaction
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class AnnualFeeService:
    """年费管理服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 年费规则管理 ====================

    def create_fee_rule(self, rule_data: AnnualFeeRuleCreate, user_id: UUID) -> AnnualFeeRule:
        """
        创建年费规则
        
        Args:
            rule_data: 规则数据
            user_id: 用户ID
            
        Returns:
            AnnualFeeRule: 创建的年费规则
        """
        try:
            logger.info(f"创建年费规则", extra={
                "user_id": str(user_id),
                "card_id": str(rule_data.card_id),
                "condition_type": rule_data.condition_type.value
            })
            
            # 验证信用卡是否属于该用户
            card = self.db.query(DBCard).filter(
                and_(
                    DBCard.id == rule_data.card_id,
                    DBCard.user_id == user_id
                )
            ).first()
            
            if not card:
                raise ValueError("信用卡不存在或不属于该用户")
            
            # 创建规则
            rule_dict = rule_data.model_dump(exclude_unset=True)
            db_rule = DBFeeRule(**rule_dict)
            self.db.add(db_rule)
            self.db.commit()
            self.db.refresh(db_rule)
            
            logger.info(f"年费规则创建成功", extra={
                "rule_id": str(db_rule.id),
                "user_id": str(user_id)
            })
            
            return AnnualFeeRule.model_validate(db_rule)
            
        except Exception as e:
            logger.error(f"创建年费规则失败: {str(e)}", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            self.db.rollback()
            raise

    def get_fee_rules(
        self,
        user_id: UUID,
        card_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[AnnualFeeRule], int]:
        """获取年费规则列表"""
        try:
            # 通过关联查询确保只获取用户自己的规则
            query = self.db.query(DBFeeRule).join(DBCard).filter(
                DBCard.user_id == user_id
            )
            
            if card_id:
                query = query.filter(DBFeeRule.card_id == card_id)
            
            total = query.count()
            rules = query.order_by(
                desc(DBFeeRule.created_at)
            ).offset(skip).limit(limit).all()
            
            return [AnnualFeeRule.model_validate(rule) for rule in rules], total
            
        except Exception as e:
            logger.error(f"获取年费规则失败: {str(e)}")
            raise

    def get_fee_rule_by_id(self, rule_id: UUID, user_id: UUID) -> Optional[AnnualFeeRule]:
        """获取单个年费规则"""
        try:
            rule = self.db.query(DBFeeRule).join(DBCard).filter(
                and_(
                    DBFeeRule.id == rule_id,
                    DBCard.user_id == user_id
                )
            ).first()
            
            if not rule:
                return None
                
            return AnnualFeeRule.model_validate(rule)
            
        except Exception as e:
            logger.error(f"获取年费规则失败: {str(e)}")
            raise

    def update_fee_rule(
        self, 
        rule_id: UUID, 
        user_id: UUID,
        rule_data: AnnualFeeRuleUpdate
    ) -> Optional[AnnualFeeRule]:
        """更新年费规则"""
        try:
            rule = self.db.query(DBFeeRule).join(DBCard).filter(
                and_(
                    DBFeeRule.id == rule_id,
                    DBCard.user_id == user_id
                )
            ).first()
            
            if not rule:
                return None
            
            # 更新字段
            update_data = rule_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(rule, field, value)
            
            rule.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"年费规则更新成功", extra={
                "rule_id": str(rule_id),
                "user_id": str(user_id)
            })
            
            return AnnualFeeRule.model_validate(rule)
            
        except Exception as e:
            logger.error(f"更新年费规则失败: {str(e)}")
            self.db.rollback()
            raise

    def delete_fee_rule(self, rule_id: UUID, user_id: UUID) -> bool:
        """删除年费规则"""
        try:
            rule = self.db.query(DBFeeRule).join(DBCard).filter(
                and_(
                    DBFeeRule.id == rule_id,
                    DBCard.user_id == user_id
                )
            ).first()
            
            if not rule:
                return False
            
            self.db.delete(rule)
            self.db.commit()
            
            logger.info(f"年费规则删除成功", extra={
                "rule_id": str(rule_id),
                "user_id": str(user_id)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"删除年费规则失败: {str(e)}")
            self.db.rollback()
            raise

    # ==================== 年费记录管理 ====================

    def create_fee_record(self, record_data: AnnualFeeRecordCreate, user_id: UUID) -> AnnualFeeRecord:
        """创建年费记录"""
        try:
            # 验证信用卡是否属于该用户
            card = self.db.query(DBCard).filter(
                and_(
                    DBCard.id == record_data.card_id,
                    DBCard.user_id == user_id
                )
            ).first()
            
            if not card:
                raise ValueError("信用卡不存在或不属于该用户")
            
            # 自动生成年费记录（包含减免计算）
            record_dict = record_data.model_dump(exclude_unset=True)
            
            # 计算实际年费
            waiver_analysis = self.calculate_fee_waiver(record_data.card_id, record_data.fee_year)
            record_dict.update({
                'actual_fee': waiver_analysis.actual_fee,
                'waiver_amount': waiver_analysis.waiver_amount,
                'waiver_rules_applied': waiver_analysis.applied_rules,
                'waiver_reason': waiver_analysis.waiver_reason
            })
            
            db_record = DBFeeRecord(**record_dict)
            self.db.add(db_record)
            self.db.commit()
            self.db.refresh(db_record)
            
            logger.info(f"年费记录创建成功", extra={
                "record_id": str(db_record.id),
                "user_id": str(user_id)
            })
            
            return AnnualFeeRecord.model_validate(db_record)
            
        except Exception as e:
            logger.error(f"创建年费记录失败: {str(e)}")
            self.db.rollback()
            raise

    def get_fee_records(
        self,
        user_id: UUID,
        filter_params: AnnualFeeQueryFilter,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[AnnualFeeRecord], int]:
        """获取年费记录列表"""
        try:
            query = self.db.query(DBFeeRecord).join(DBCard).filter(
                DBCard.user_id == user_id
            )
            
            # 应用过滤条件
            if filter_params.card_id:
                query = query.filter(DBFeeRecord.card_id == filter_params.card_id)
            
            if filter_params.fee_year:
                query = query.filter(DBFeeRecord.fee_year == filter_params.fee_year)
            
            if filter_params.status:
                query = query.filter(DBFeeRecord.status == filter_params.status)
            
            if filter_params.keyword:
                keyword_filter = f"%{filter_params.keyword}%"
                query = query.filter(
                    or_(
                        DBCard.card_name.ilike(keyword_filter),
                        DBCard.bank_name.ilike(keyword_filter),
                        DBFeeRecord.waiver_reason.ilike(keyword_filter)
                    )
                )
            
            total = query.count()
            records = query.order_by(
                desc(DBFeeRecord.fee_year),
                desc(DBFeeRecord.created_at)
            ).offset(skip).limit(limit).all()
            
            return [AnnualFeeRecord.model_validate(record) for record in records], total
            
        except Exception as e:
            logger.error(f"获取年费记录失败: {str(e)}")
            raise

    def get_fee_record_by_id(self, record_id: UUID, user_id: UUID) -> Optional[AnnualFeeRecord]:
        """获取单个年费记录"""
        try:
            record = self.db.query(DBFeeRecord).join(DBCard).filter(
                and_(
                    DBFeeRecord.id == record_id,
                    DBCard.user_id == user_id
                )
            ).first()
            
            if not record:
                return None
                
            return AnnualFeeRecord.model_validate(record)
            
        except Exception as e:
            logger.error(f"获取年费记录失败: {str(e)}")
            raise

    def calculate_fee_waiver(self, card_id: UUID, fee_year: int) -> WaiverAnalysis:
        """计算年费减免"""
        try:
            # 获取信用卡和基础年费
            card = self.db.query(DBCard).filter(DBCard.id == card_id).first()
            if not card:
                raise ValueError("信用卡不存在")
            
            base_fee = card.annual_fee or Decimal("0")
            
            # 获取该卡的减免规则
            rules = self.db.query(DBFeeRule).filter(
                and_(
                    DBFeeRule.card_id == card_id,
                    DBFeeRule.is_enabled == True
                )
            ).all()
            
            if not rules:
                return WaiverAnalysis(
                    base_fee=base_fee,
                    actual_fee=base_fee,
                    waiver_amount=Decimal("0"),
                    waiver_reason="无减免规则",
                    applied_rules=[],
                    can_waive=False
                )
            
            # 计算年度交易数据
            year_start = datetime(fee_year, 1, 1)
            year_end = datetime(fee_year, 12, 31, 23, 59, 59)
            
            transaction_stats = self.db.query(
                func.count(DBTransaction.id).label('count'),
                func.sum(DBTransaction.amount).label('total_amount')
            ).filter(
                and_(
                    DBTransaction.card_id == card_id,
                    DBTransaction.transaction_date >= year_start,
                    DBTransaction.transaction_date <= year_end,
                    DBTransaction.transaction_type == "expense"
                )
            ).first()
            
            annual_spending = transaction_stats.total_amount or Decimal("0")
            annual_count = transaction_stats.count or 0
            
            # 评估减免规则
            total_waiver = Decimal("0")
            applied_rules = []
            waiver_reasons = []
            
            for rule in rules:
                waiver_amount = self._evaluate_waiver_rule(
                    rule, annual_spending, annual_count, base_fee
                )
                
                if waiver_amount > 0:
                    total_waiver += waiver_amount
                    applied_rules.append({
                        "rule_id": str(rule.id),
                        "rule_name": rule.rule_name,
                        "waiver_amount": float(waiver_amount)
                    })
                    waiver_reasons.append(rule.rule_name)
            
            # 减免金额不能超过基础年费
            total_waiver = min(total_waiver, base_fee)
            actual_fee = base_fee - total_waiver
            
            return WaiverAnalysis(
                base_fee=base_fee,
                actual_fee=actual_fee,
                waiver_amount=total_waiver,
                waiver_reason="; ".join(waiver_reasons) if waiver_reasons else "无减免",
                applied_rules=applied_rules,
                can_waive=total_waiver > 0
            )
            
        except Exception as e:
            logger.error(f"计算年费减免失败: {str(e)}")
            raise

    def get_fee_stats(
        self,
        user_id: UUID,
        year: Optional[int] = None
    ) -> AnnualFeeStats:
        """获取年费统计"""
        try:
            if not year:
                year = datetime.now().year
            
            # 获取用户所有年费记录
            query = self.db.query(DBFeeRecord).join(DBCard).filter(
                and_(
                    DBCard.user_id == user_id,
                    DBFeeRecord.fee_year == year
                )
            )
            
            records = query.all()
            
            total_base_fee = sum(record.base_fee for record in records)
            total_actual_fee = sum(record.actual_fee for record in records)
            total_waiver_amount = sum(record.waiver_amount for record in records)
            
            paid_count = len([r for r in records if r.status == "paid"])
            waived_count = len([r for r in records if r.status == "waived"])
            pending_count = len([r for r in records if r.status == "pending"])
            
            return AnnualFeeStats(
                year=year,
                total_cards=len(records),
                total_base_fee=total_base_fee,
                total_actual_fee=total_actual_fee,
                total_waiver_amount=total_waiver_amount,
                waiver_rate=float(total_waiver_amount / total_base_fee * 100) if total_base_fee > 0 else 0,
                paid_count=paid_count,
                waived_count=waived_count,
                pending_count=pending_count
            )
            
        except Exception as e:
            logger.error(f"获取年费统计失败: {str(e)}")
            raise

    def batch_operations(
        self, 
        user_id: UUID, 
        operation: AnnualFeeBatchOperation
    ) -> Dict[str, Any]:
        """批量操作"""
        try:
            if operation.action == "mark_paid":
                updated_count = 0
                for record_id in operation.record_ids:
                    record = self.db.query(DBFeeRecord).join(DBCard).filter(
                        and_(
                            DBFeeRecord.id == record_id,
                            DBCard.user_id == user_id
                        )
                    ).first()
                    
                    if record:
                        record.status = "paid"
                        record.paid_date = date.today()
                        record.updated_at = datetime.now(UTC)
                        updated_count += 1
                
                self.db.commit()
                return {"updated_count": updated_count, "total_requested": len(operation.record_ids)}
            
            elif operation.action == "recalculate":
                updated_count = 0
                for record_id in operation.record_ids:
                    record = self.db.query(DBFeeRecord).join(DBCard).filter(
                        and_(
                            DBFeeRecord.id == record_id,
                            DBCard.user_id == user_id
                        )
                    ).first()
                    
                    if record:
                        # 重新计算年费
                        waiver_analysis = self.calculate_fee_waiver(record.card_id, record.fee_year)
                        record.actual_fee = waiver_analysis.actual_fee
                        record.waiver_amount = waiver_analysis.waiver_amount
                        record.waiver_rules_applied = waiver_analysis.applied_rules
                        record.waiver_reason = waiver_analysis.waiver_reason
                        record.updated_at = datetime.now(UTC)
                        updated_count += 1
                
                self.db.commit()
                return {"updated_count": updated_count, "total_requested": len(operation.record_ids)}
            
            else:
                raise ValueError(f"不支持的批量操作: {operation.action}")
                
        except Exception as e:
            logger.error(f"批量操作失败: {str(e)}")
            self.db.rollback()
            raise

    def _evaluate_waiver_rule(
        self, 
        rule: DBFeeRule, 
        annual_spending: Decimal, 
        annual_count: int, 
        base_fee: Decimal
    ) -> Decimal:
        """评估单个减免规则"""
        try:
            if rule.condition_type == ConditionType.SPENDING_AMOUNT:
                if annual_spending >= (rule.condition_value or Decimal("0")):
                    return base_fee  # 完全减免
            
            elif rule.condition_type == ConditionType.TRANSACTION_COUNT:
                if annual_count >= (rule.condition_count or 0):
                    return base_fee  # 完全减免
            
            elif rule.condition_type == ConditionType.POINTS_REDEEM:
                # 这里需要查询积分兑换记录，简化实现
                return Decimal("0")
            
            return Decimal("0")
            
        except Exception as e:
            logger.error(f"评估减免规则失败: {str(e)}")
            return Decimal("0")