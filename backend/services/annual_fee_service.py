from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, extract, func, text
from sqlalchemy.orm import Session

from models.annual_fee import (
    AnnualFeeRecord,
    AnnualFeeRecordCreate,
    AnnualFeeRecordUpdate,
    AnnualFeeRule,
    AnnualFeeRuleCreate,
    AnnualFeeRuleUpdate,
    AnnualFeeStatistics,
    AnnualFeeWaiverCheck,
    FeeType,
    WaiverStatus,
)


class AnnualFeeService:
    """年费管理服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 年费规则管理 ====================

    def create_annual_fee_rule(self, rule_data: AnnualFeeRuleCreate) -> AnnualFeeRule:
        """创建年费规则"""
        db_rule = self._create_annual_fee_rule_db(rule_data)
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        return AnnualFeeRule.model_validate(db_rule)

    def get_annual_fee_rules(
        self, skip: int = 0, limit: int = 100, fee_type: Optional[FeeType] = None, keyword: str = ""
    ) -> tuple[List[AnnualFeeRule], int]:
        """
        获取年费规则列表
        
        支持分页、类型过滤和模糊搜索功能。
        
        参数:
        - skip: 跳过的记录数
        - limit: 返回的记录数限制
        - fee_type: 年费类型过滤
        - keyword: 模糊搜索关键词，支持规则名称、描述搜索
        """
        query = self.db.query(self._get_annual_fee_rule_model())
        
        # 年费类型过滤
        if fee_type:
            query = query.filter(self._get_annual_fee_rule_model().fee_type == fee_type)
        
        # 关键词模糊搜索
        if keyword:
            keyword_filter = f"%{keyword}%"
            query = query.filter(
                self._get_annual_fee_rule_model().description.ilike(keyword_filter)
            )
        
        # 获取总数
        total = query.count()
        
        # 获取分页数据
        rules = query.offset(skip).limit(limit).all()
        return [AnnualFeeRule.model_validate(rule) for rule in rules], total

    def get_annual_fee_rule(self, rule_id: UUID) -> Optional[AnnualFeeRule]:
        """根据ID获取年费规则"""
        rule = self.db.query(self._get_annual_fee_rule_model()).filter(
            self._get_annual_fee_rule_model().id == rule_id
        ).first()
        return AnnualFeeRule.model_validate(rule) if rule else None

    def update_annual_fee_rule(
        self, rule_id: UUID, rule_data: AnnualFeeRuleUpdate
    ) -> Optional[AnnualFeeRule]:
        """更新年费规则"""
        rule = self.db.query(self._get_annual_fee_rule_model()).filter(
            self._get_annual_fee_rule_model().id == rule_id
        ).first()
        if not rule:
            return None

        for field, value in rule_data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)

        self.db.commit()
        self.db.refresh(rule)
        return AnnualFeeRule.model_validate(rule)

    def delete_annual_fee_rule(self, rule_id: UUID) -> bool:
        """删除年费规则"""
        rule = self.db.query(self._get_annual_fee_rule_model()).filter(
            self._get_annual_fee_rule_model().id == rule_id
        ).first()
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()
        return True

    # ==================== 年费记录管理 ====================

    def create_annual_fee_record(self, record_data: AnnualFeeRecordCreate) -> AnnualFeeRecord:
        """创建年费记录"""
        db_record = self._create_annual_fee_record_db(record_data)
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return AnnualFeeRecord.model_validate(db_record)

    def create_annual_fee_record_auto(self, card_id: UUID, fee_year: int) -> Optional[UUID]:
        """自动创建年费记录（使用数据库函数）"""
        try:
            result = self.db.execute(
                text("SELECT create_annual_fee_record(:card_id, :fee_year)"),
                {"card_id": card_id, "fee_year": fee_year}
            )
            record_id = result.scalar()
            self.db.commit()
            return record_id
        except Exception as e:
            self.db.rollback()
            raise e

    def get_annual_fee_records(
        self,
        card_id: Optional[UUID] = None,
        fee_year: Optional[int] = None,
        waiver_status: Optional[WaiverStatus] = None,
        keyword: str = "",
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AnnualFeeRecord], int]:
        """
        获取年费记录列表
        
        支持多种筛选条件和模糊搜索功能。
        
        参数:
        - card_id: 信用卡ID过滤
        - fee_year: 年费年份过滤
        - waiver_status: 减免状态过滤
        - keyword: 模糊搜索关键词，通过关联查询搜索卡片名称、银行名称
        - skip: 跳过的记录数
        - limit: 返回的记录数限制
        """
        query = self.db.query(self._get_annual_fee_record_model())
        
        # 基础过滤条件
        if card_id:
            query = query.filter(self._get_annual_fee_record_model().card_id == card_id)
        if fee_year:
            query = query.filter(self._get_annual_fee_record_model().fee_year == fee_year)
        if waiver_status:
            query = query.filter(self._get_annual_fee_record_model().waiver_status == waiver_status)

        # 关键词模糊搜索（需要关联信用卡表）
        if keyword:
            keyword_filter = f"%{keyword}%"
            query = query.join(self._get_credit_card_model()).filter(
                self._get_credit_card_model().bank_name.ilike(keyword_filter) |
                self._get_credit_card_model().card_name.ilike(keyword_filter)
            )

        # 获取总数
        total = query.count()
        
        # 获取分页数据
        records = query.offset(skip).limit(limit).all()
        return [AnnualFeeRecord.model_validate(record) for record in records], total

    def get_annual_fee_record(self, record_id: UUID) -> Optional[AnnualFeeRecord]:
        """根据ID获取年费记录"""
        record = self.db.query(self._get_annual_fee_record_model()).filter(
            self._get_annual_fee_record_model().id == record_id
        ).first()
        return AnnualFeeRecord.model_validate(record) if record else None

    def update_annual_fee_record(
        self, record_id: UUID, record_data: AnnualFeeRecordUpdate
    ) -> Optional[AnnualFeeRecord]:
        """更新年费记录"""
        record = self.db.query(self._get_annual_fee_record_model()).filter(
            self._get_annual_fee_record_model().id == record_id
        ).first()
        if not record:
            return None

        for field, value in record_data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)

        self.db.commit()
        self.db.refresh(record)
        return AnnualFeeRecord.model_validate(record)

    # ==================== 年费减免检查 ====================

    def check_annual_fee_waiver(self, card_id: UUID, fee_year: int) -> AnnualFeeWaiverCheck:
        """检查年费减免条件"""
        try:
            # 使用数据库函数检查减免条件
            result = self.db.execute(
                text("SELECT check_annual_fee_waiver(:card_id, :fee_year)"),
                {"card_id": card_id, "fee_year": fee_year}
            )
            waiver_eligible = result.scalar()

            # 获取年费记录和规则信息
            record = self.db.query(self._get_annual_fee_record_model()).filter(
                and_(
                    self._get_annual_fee_record_model().card_id == card_id,
                    self._get_annual_fee_record_model().fee_year == fee_year,
                )
            ).first()

            if not record:
                raise ValueError(f"Annual fee record not found for card {card_id} and year {fee_year}")

            # 获取信用卡信息和年费规则
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id
            ).first()
            
            rule = self.db.query(self._get_annual_fee_rule_model()).filter(
                self._get_annual_fee_rule_model().id == card.annual_fee_rule_id
            ).first()

            # 计算剩余天数
            today = date.today()
            days_remaining = (record.due_date - today).days

            # 生成进度描述
            progress_description = self._generate_progress_description(
                rule.fee_type, record.current_progress, rule.waiver_condition_value
            )

            return AnnualFeeWaiverCheck(
                card_id=card_id,
                fee_year=fee_year,
                waiver_eligible=waiver_eligible,
                current_progress=record.current_progress,
                required_progress=rule.waiver_condition_value,
                progress_description=progress_description,
                days_remaining=days_remaining,
            )
        except Exception as e:
            raise e

    def check_all_annual_fee_waivers(self, user_id: UUID, year: Optional[int] = None) -> List[AnnualFeeWaiverCheck]:
        """检查用户所有信用卡的年费减免条件"""
        if year is None:
            year = date.today().year

        # 获取用户所有信用卡
        cards = self.db.query(self._get_credit_card_model()).filter(
            self._get_credit_card_model().user_id == user_id
        ).all()

        results = []
        for card in cards:
            try:
                waiver_check = self.check_annual_fee_waiver(card.id, year)
                results.append(waiver_check)
            except Exception:
                # 如果某张卡没有年费记录，跳过
                continue

        return results

    # ==================== 年费统计 ====================

    def get_annual_fee_statistics(self, user_id: UUID, year: Optional[int] = None) -> AnnualFeeStatistics:
        """获取年费统计信息"""
        if year is None:
            year = date.today().year

        # 获取用户所有信用卡
        cards = self.db.query(self._get_credit_card_model()).filter(
            self._get_credit_card_model().user_id == user_id
        ).all()
        card_ids = [card.id for card in cards]

        if not card_ids:
            return AnnualFeeStatistics(
                total_cards=0,
                total_annual_fees=Decimal("0"),
                waived_fees=Decimal("0"),
                paid_fees=Decimal("0"),
                pending_fees=Decimal("0"),
                overdue_fees=Decimal("0"),
                waiver_rate=0.0,
            )

        # 查询年费记录统计
        records = self.db.query(self._get_annual_fee_record_model()).filter(
            and_(
                self._get_annual_fee_record_model().card_id.in_(card_ids),
                self._get_annual_fee_record_model().fee_year == year,
            )
        ).all()

        total_cards = len(card_ids)
        total_annual_fees = sum(record.fee_amount for record in records)
        waived_fees = sum(
            record.fee_amount for record in records if record.waiver_status == WaiverStatus.WAIVED
        )
        paid_fees = sum(
            record.fee_amount for record in records if record.waiver_status == WaiverStatus.PAID
        )
        pending_fees = sum(
            record.fee_amount for record in records if record.waiver_status == WaiverStatus.PENDING
        )
        overdue_fees = sum(
            record.fee_amount for record in records if record.waiver_status == WaiverStatus.OVERDUE
        )

        waiver_rate = float(waived_fees / total_annual_fees * 100) if total_annual_fees > 0 else 0.0

        return AnnualFeeStatistics(
            total_cards=total_cards,
            total_annual_fees=total_annual_fees,
            waived_fees=waived_fees,
            paid_fees=paid_fees,
            pending_fees=pending_fees,
            overdue_fees=overdue_fees,
            waiver_rate=waiver_rate,
        )

    # ==================== 辅助方法 ====================

    def _generate_progress_description(self, fee_type: str, current: Decimal, required: Optional[Decimal]) -> str:
        """生成进度描述"""
        if fee_type == FeeType.RIGID:
            return "刚性年费，无减免条件"
        elif fee_type == FeeType.TRANSACTION_COUNT:
            return f"已刷卡 {int(current)} 次，需要 {int(required or 0)} 次"
        elif fee_type == FeeType.TRANSACTION_AMOUNT:
            return f"已刷卡 {current:,.0f} 元，需要 {required or 0:,.0f} 元"
        elif fee_type == FeeType.POINTS_EXCHANGE:
            return f"可用积分兑换，需要 {int(required or 0)} 积分"
        else:
            return "未知减免条件"

    def _create_annual_fee_rule_db(self, rule_data: AnnualFeeRuleCreate):
        """创建数据库年费规则对象"""
        from db_models.annual_fee import AnnualFeeRule as AnnualFeeRuleDB
        return AnnualFeeRuleDB(**rule_data.model_dump())

    def _create_annual_fee_record_db(self, record_data: AnnualFeeRecordCreate):
        """创建数据库年费记录对象"""
        from db_models.annual_fee import AnnualFeeRecord as AnnualFeeRecordDB
        return AnnualFeeRecordDB(**record_data.model_dump())

    def _get_annual_fee_rule_model(self):
        """获取年费规则数据库模型"""
        from db_models.annual_fee import AnnualFeeRule as AnnualFeeRuleDB
        return AnnualFeeRuleDB

    def _get_annual_fee_record_model(self):
        """获取年费记录数据库模型"""
        from db_models.annual_fee import AnnualFeeRecord as AnnualFeeRecordDB
        return AnnualFeeRecordDB

    def _get_credit_card_model(self):
        """获取信用卡数据库模型"""
        from db_models.cards import CreditCard
        return CreditCard 