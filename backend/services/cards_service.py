"""
信用卡服务

实现信用卡相关的业务逻辑，包括增删改查、额度管理、年费管理等功能。
"""

import logging
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, datetime

from models.cards import (
    Card, CardCreate, CardUpdate, 
    CardWithAnnualFeeCreate, CardWithAnnualFeeUpdate, CardWithAnnualFee,
    CardSummary, CardSummaryWithAnnualFee
)
from models.annual_fee import AnnualFeeRuleCreate, FeeType
from services.annual_fee_service import AnnualFeeService
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)


class CardsService:
    """
    信用卡服务类
    
    提供信用卡相关的业务逻辑处理，包括CRUD操作、额度管理、年费管理等功能。
    """

    def __init__(self, db: Session):
        """
        初始化信用卡服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.annual_fee_service = AnnualFeeService(db)

    def create_card(self, card_data: CardCreate, user_id: UUID) -> Card:
        """
        创建信用卡
        
        Args:
            card_data: 信用卡创建数据
            user_id: 用户ID
            
        Returns:
            Card: 创建的信用卡信息
            
        Raises:
            ValueError: 参数验证失败
            Exception: 创建失败
        """
        try:
            logger.info(f"创建信用卡: {card_data.bank_name} - {card_data.card_name}")
            
            # 检查卡号是否已存在
            existing_card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().card_number == card_data.card_number,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if existing_card:
                raise ValueError("信用卡号已存在")
            
            # 创建信用卡记录
            card_dict = card_data.dict()
            card_dict['user_id'] = user_id
            
            # 移除available_amount字段，因为它是计算属性
            if 'available_amount' in card_dict:
                card_dict.pop('available_amount')
            
            db_card = self._create_card_db(card_dict)
            self.db.add(db_card)
            self.db.commit()
            self.db.refresh(db_card)
            
            logger.info(f"信用卡创建成功: {db_card.id}")
            return Card.from_orm(db_card)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"创建信用卡失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"创建信用卡失败: {str(e)}")

    def create_card_with_annual_fee(
        self, 
        card_data: CardWithAnnualFeeCreate, 
        user_id: UUID
    ) -> CardWithAnnualFee:
        """
        创建信用卡（集成年费管理）
        
        Args:
            card_data: 信用卡创建数据（包含年费信息）
            user_id: 用户ID
            
        Returns:
            CardWithAnnualFee: 创建的信用卡信息（包含年费）
            
        Raises:
            ValueError: 参数验证失败
            Exception: 创建失败
        """
        try:
            logger.info(f"创建信用卡（含年费）: {card_data.bank_name} - {card_data.card_name}")
            
            # 检查卡号是否已存在
            existing_card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().card_number == card_data.card_number,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if existing_card:
                raise ValueError("信用卡号已存在")
            
            # 创建信用卡记录
            card_dict = card_data.dict()
            
            # 提取年费相关字段
            annual_fee_enabled = card_dict.pop('annual_fee_enabled', False)
            fee_type = card_dict.pop('fee_type', None)
            base_fee = card_dict.pop('base_fee', None)
            waiver_condition_value = card_dict.pop('waiver_condition_value', None)
            points_per_yuan = card_dict.pop('points_per_yuan', None)
            annual_fee_month = card_dict.pop('annual_fee_month', None)
            annual_fee_day = card_dict.pop('annual_fee_day', None)
            fee_description = card_dict.pop('fee_description', None)
            
            card_dict['user_id'] = user_id
            
            # 移除available_amount字段，因为它是计算属性
            if 'available_amount' in card_dict:
                card_dict.pop('available_amount')
            
            # 先创建年费规则（如果启用）
            annual_fee_rule = None
            if annual_fee_enabled and fee_type and base_fee:
                rule_data = AnnualFeeRuleCreate(
                    fee_type=fee_type,
                    base_fee=base_fee,
                    waiver_condition_value=waiver_condition_value,
                    points_per_yuan=points_per_yuan,
                    annual_fee_month=annual_fee_month,
                    annual_fee_day=annual_fee_day,
                    description=fee_description
                )
                
                annual_fee_rule = self.annual_fee_service.create_annual_fee_rule(rule_data)
                # 将年费规则ID添加到信用卡数据中
                card_dict['annual_fee_rule_id'] = annual_fee_rule.id
            
            # 创建信用卡
            db_card = self._create_card_db(card_dict)
            self.db.add(db_card)
            self.db.flush()  # 获取card id但不提交
            
            # 创建年费记录（如果有年费规则）
            if annual_fee_rule:
                from models.annual_fee import AnnualFeeRecordCreate, WaiverStatus
                current_year = datetime.now().year
                due_date = annual_fee_rule.get_annual_due_date(current_year) or date(current_year, 12, 31)
                record_data = AnnualFeeRecordCreate(
                    card_id=db_card.id,
                    fee_year=current_year,
                    due_date=due_date,
                    fee_amount=annual_fee_rule.base_fee,
                    waiver_status=WaiverStatus.PENDING,
                    waiver_condition_met=False,
                    current_progress=0
                )
                self.annual_fee_service.create_annual_fee_record(record_data)
            
            self.db.commit()
            self.db.refresh(db_card)
            
            # 构建响应数据
            card_response = CardWithAnnualFee(
                **Card.from_orm(db_card).dict(),
                annual_fee_rule=annual_fee_rule,
                has_annual_fee=annual_fee_rule is not None,
                current_year_fee_status="pending" if annual_fee_rule else None,
                next_fee_due_date=annual_fee_rule.get_annual_due_date(datetime.now().year) if annual_fee_rule else None
            )
            
            logger.info(f"信用卡（含年费）创建成功: {db_card.id}")
            return card_response
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"创建信用卡（含年费）失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"创建信用卡（含年费）失败: {str(e)}")

    def get_cards(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        keyword: str = ""
    ) -> Tuple[List[Card], int]:
        """
        获取信用卡列表
        
        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 限制记录数
            keyword: 搜索关键词
            
        Returns:
            Tuple[List[Card], int]: 信用卡列表和总数
        """
        try:
            logger.info(f"获取信用卡列表: user_id={user_id}, keyword='{keyword}'")
            
            query = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            )
            
            # 模糊搜索
            if keyword.strip():
                search_filter = or_(
                    self._get_credit_card_model().bank_name.ilike(f"%{keyword}%"),
                    self._get_credit_card_model().card_name.ilike(f"%{keyword}%"),
                    self._get_credit_card_model().notes.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            cards = query.order_by(
                self._get_credit_card_model().created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.info(f"找到 {len(cards)} 张信用卡，总计 {total} 张")
            return [Card.from_orm(card) for card in cards], total
            
        except Exception as e:
            logger.error(f"获取信用卡列表失败: {str(e)}")
            raise Exception(f"获取信用卡列表失败: {str(e)}")

    def get_cards_with_annual_fee(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        keyword: str = ""
    ) -> Tuple[List[CardSummaryWithAnnualFee], int]:
        """
        获取信用卡列表（包含年费信息）
        
        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 限制记录数
            keyword: 搜索关键词
            
        Returns:
            Tuple[List[CardSummaryWithAnnualFee], int]: 信用卡列表和总数
        """
        try:
            logger.info(f"获取信用卡列表（含年费）: user_id={user_id}, keyword='{keyword}'")
            
            # 导入年费模型
            from db_models.annual_fee import AnnualFeeRule, AnnualFeeRecord
            
            # 左连接年费规则和记录
            query = self.db.query(
                self._get_credit_card_model(),
                AnnualFeeRule,
                AnnualFeeRecord
            ).outerjoin(
                AnnualFeeRule, 
                self._get_credit_card_model().annual_fee_rule_id == AnnualFeeRule.id
            ).outerjoin(
                AnnualFeeRecord,
                (AnnualFeeRecord.card_id == self._get_credit_card_model().id) & 
                (AnnualFeeRecord.fee_year == datetime.now().year)
            ).filter(
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            )
            
            # 模糊搜索
            if keyword.strip():
                search_filter = or_(
                    self._get_credit_card_model().bank_name.ilike(f"%{keyword}%"),
                    self._get_credit_card_model().card_name.ilike(f"%{keyword}%"),
                    self._get_credit_card_model().notes.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            results = query.order_by(
                self._get_credit_card_model().created_at.desc()
            ).offset(skip).limit(limit).all()
            
            # 构建响应数据
            card_summaries = []
            for card, rule, record in results:
                card_summary = CardSummaryWithAnnualFee(
                    id=card.id,
                    bank_name=card.bank_name,
                    card_name=card.card_name,
                    card_type=card.card_type,
                    credit_limit=card.credit_limit,
                    used_amount=card.used_amount,
                    available_amount=card.available_amount,
                    status=card.status,
                    card_color=card.card_color,
                    has_annual_fee=rule is not None,
                    annual_fee_amount=rule.base_fee if rule else None,
                    fee_type_display=self._get_fee_type_display(rule.fee_type) if rule else None,
                    current_year_fee_status=record.waiver_status if record else None
                )
                card_summaries.append(card_summary)
            
            logger.info(f"找到 {len(card_summaries)} 张信用卡（含年费），总计 {total} 张")
            return card_summaries, total
            
        except Exception as e:
            logger.error(f"获取信用卡列表（含年费）失败: {str(e)}")
            raise Exception(f"获取信用卡列表（含年费）失败: {str(e)}")

    def get_card(self, card_id: UUID, user_id: UUID) -> Optional[Card]:
        """
        获取单张信用卡详情
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            
        Returns:
            Optional[Card]: 信用卡信息
        """
        try:
            logger.info(f"获取信用卡详情: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return None
                
            return Card.from_orm(card)
            
        except Exception as e:
            logger.error(f"获取信用卡详情失败: {str(e)}")
            raise Exception(f"获取信用卡详情失败: {str(e)}")

    def get_card_with_annual_fee( 
        self, 
        card_id: UUID, 
        user_id: UUID
    ) -> Optional[CardWithAnnualFee]:
        """
        获取单张信用卡详情（包含年费信息）
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            
        Returns:
            Optional[CardWithAnnualFee]: 信用卡信息（包含年费）
        """
        try:
            logger.info(f"获取信用卡详情（含年费）: {card_id}")
            
            # 导入年费模型
            from db_models.annual_fee import AnnualFeeRule, AnnualFeeRecord
            from models.annual_fee import AnnualFeeRule as AnnualFeeRuleModel
            
            # 左连接年费规则和记录
            result = self.db.query(
                self._get_credit_card_model(),
                AnnualFeeRule,
                AnnualFeeRecord
            ).outerjoin(
                AnnualFeeRule, 
                self._get_credit_card_model().annual_fee_rule_id == AnnualFeeRule.id
            ).outerjoin(
                AnnualFeeRecord,
                (AnnualFeeRecord.card_id == self._get_credit_card_model().id) & 
                (AnnualFeeRecord.fee_year == datetime.now().year)
            ).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not result or not result[0]:
                logger.warning(f"信用卡不存在: {card_id}")
                return None
            
            card, rule, record = result
            
            # 构建响应数据
            if rule:
                annual_fee_rule_data = AnnualFeeRuleModel(
                    id=rule.id,
                    fee_type=rule.fee_type,
                    base_fee=rule.base_fee,
                    waiver_condition_value=rule.waiver_condition_value,
                    points_per_yuan=rule.points_per_yuan,
                    annual_fee_month=rule.annual_fee_month,
                    annual_fee_day=rule.annual_fee_day,
                    description=rule.description,
                    created_at=rule.created_at
                )
                next_fee_due_date = None
                if rule.annual_fee_month and rule.annual_fee_day:
                    try:
                        current_year = datetime.now().year
                        next_fee_due_date = date(current_year, rule.annual_fee_month, rule.annual_fee_day)
                    except ValueError:
                        if rule.annual_fee_month == 2 and rule.annual_fee_day == 29:
                            next_fee_due_date = date(current_year, 2, 28)
            else:
                annual_fee_rule_data = None
                next_fee_due_date = None
            
            card_response = CardWithAnnualFee(
                **Card.from_orm(card).dict(),
                annual_fee_rule=annual_fee_rule_data,
                has_annual_fee=rule is not None,
                current_year_fee_status=record.waiver_status if record else None,
                next_fee_due_date=next_fee_due_date
            )
                
            return card_response
            
        except Exception as e:
            logger.error(f"获取信用卡详情（含年费）失败: {str(e)}")
            raise Exception(f"获取信用卡详情（含年费）失败: {str(e)}")

    def update_card(
        self, 
        card_id: UUID, 
        user_id: UUID,
        card_data: CardUpdate
    ) -> Optional[Card]:
        """
        更新信用卡信息
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            card_data: 更新数据
            
        Returns:
            Optional[Card]: 更新后的信用卡信息
        """
        try:
            logger.info(f"更新信用卡: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return None
            
            # 更新字段
            update_data = card_data.dict(exclude_unset=True)
            # 移除available_amount字段，因为它是计算属性
            if 'available_amount' in update_data:
                update_data.pop('available_amount')
                
            for field, value in update_data.items():
                if hasattr(card, field):
                    setattr(card, field, value)
            
            self.db.commit()
            self.db.refresh(card)
            
            logger.info(f"信用卡更新成功: {card_id}")
            return Card.from_orm(card)
            
        except Exception as e:
            logger.error(f"更新信用卡失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"更新信用卡失败: {str(e)}")

    def update_card_with_annual_fee(
        self, 
        card_id: UUID, 
        user_id: UUID,
        card_data: CardWithAnnualFeeUpdate
    ) -> Optional[CardWithAnnualFee]:
        """
        更新信用卡信息（集成年费管理）
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            card_data: 更新数据（包含年费信息）
            
        Returns:
            Optional[CardWithAnnualFee]: 更新后的信用卡信息（包含年费）
        """
        try:
            logger.info(f"更新信用卡（含年费）: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return None
            
            update_data = card_data.dict(exclude_unset=True)
            
            # 提取年费相关字段
            annual_fee_enabled = update_data.pop('annual_fee_enabled', None)
            fee_type = update_data.pop('fee_type', None)
            base_fee = update_data.pop('base_fee', None)
            waiver_condition_value = update_data.pop('waiver_condition_value', None)
            points_per_yuan = update_data.pop('points_per_yuan', None)
            annual_fee_month = update_data.pop('annual_fee_month', None)
            annual_fee_day = update_data.pop('annual_fee_day', None)
            fee_description = update_data.pop('fee_description', None)
            
            # 移除available_amount字段，因为它是计算属性
            if 'available_amount' in update_data:
                update_data.pop('available_amount')
            
            # 更新信用卡基本信息
            for field, value in update_data.items():
                if hasattr(card, field):
                    setattr(card, field, value)
            
            # 处理年费管理
            annual_fee_rule = None
            if annual_fee_enabled is not None:
                if annual_fee_enabled is False:
                    # 禁用年费管理，删除现有规则和记录
                    if card.annual_fee_rule_id:
                        self.annual_fee_service.delete_annual_fee_rule(card.annual_fee_rule_id)
                        card.annual_fee_rule_id = None
                elif annual_fee_enabled is True:
                    # 启用年费管理
                    if fee_type and base_fee:
                        if card.annual_fee_rule_id:
                            # 更新现有规则
                            rule_update_data = {}
                            if fee_type is not None:
                                rule_update_data['fee_type'] = fee_type
                            if base_fee is not None:
                                rule_update_data['base_fee'] = base_fee
                            if waiver_condition_value is not None:
                                rule_update_data['waiver_condition_value'] = waiver_condition_value
                            if points_per_yuan is not None:
                                rule_update_data['points_per_yuan'] = points_per_yuan
                            if annual_fee_month is not None:
                                rule_update_data['annual_fee_month'] = annual_fee_month
                            if annual_fee_day is not None:
                                rule_update_data['annual_fee_day'] = annual_fee_day
                            if fee_description is not None:
                                rule_update_data['description'] = fee_description
                            
                            from models.annual_fee import AnnualFeeRuleUpdate
                            rule_update = AnnualFeeRuleUpdate(**rule_update_data)
                            annual_fee_rule = self.annual_fee_service.update_annual_fee_rule(
                                card.annual_fee_rule_id, 
                                rule_update
                            )
                        else:
                            # 创建新规则
                            from models.annual_fee import AnnualFeeRuleCreate
                            rule_data = AnnualFeeRuleCreate(
                                fee_type=fee_type,
                                base_fee=base_fee,
                                waiver_condition_value=waiver_condition_value,
                                points_per_yuan=points_per_yuan,
                                annual_fee_month=annual_fee_month,
                                annual_fee_day=annual_fee_day,
                                description=fee_description
                            )
                            
                            annual_fee_rule = self.annual_fee_service.create_annual_fee_rule(rule_data)
                            card.annual_fee_rule_id = annual_fee_rule.id
                            
                            # 创建当年年费记录
                            from models.annual_fee import AnnualFeeRecordCreate, WaiverStatus
                            current_year = datetime.now().year
                            due_date = annual_fee_rule.get_annual_due_date(current_year) or date(current_year, 12, 31)
                            record_data = AnnualFeeRecordCreate(
                                card_id=card.id,
                                fee_year=current_year,
                                due_date=due_date,
                                fee_amount=annual_fee_rule.base_fee,
                                waiver_status=WaiverStatus.PENDING,
                                waiver_condition_met=False,
                                current_progress=0
                            )
                            self.annual_fee_service.create_annual_fee_record(record_data)
            
            self.db.commit()
            self.db.refresh(card)
            
            # 获取最新的年费规则信息
            if card.annual_fee_rule_id and not annual_fee_rule:
                annual_fee_rule = self.annual_fee_service.get_annual_fee_rule(card.annual_fee_rule_id)
            
            # 构建响应数据
            card_response = CardWithAnnualFee(
                **Card.from_orm(card).dict(),
                annual_fee_rule=annual_fee_rule,
                has_annual_fee=annual_fee_rule is not None,
                current_year_fee_status="pending" if annual_fee_rule else None,
                next_fee_due_date=annual_fee_rule.get_annual_due_date(datetime.now().year) if annual_fee_rule else None
            )
            
            logger.info(f"信用卡（含年费）更新成功: {card_id}")
            return card_response
            
        except Exception as e:
            logger.error(f"更新信用卡（含年费）失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"更新信用卡（含年费）失败: {str(e)}")

    def delete_card(self, card_id: UUID, user_id: UUID) -> bool:
        """
        删除信用卡（软删除）
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            logger.info(f"删除信用卡: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return False
            
            # 删除相关年费规则和记录
            if card.annual_fee_rule_id:
                self.annual_fee_service.delete_annual_fee_rule(card.annual_fee_rule_id)
            
            # 软删除信用卡
            card.is_deleted = True
            self.db.commit()
            
            logger.info(f"信用卡删除成功: {card_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除信用卡失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"删除信用卡失败: {str(e)}")

    def _create_card_db(self, card_data: dict):
        """创建信用卡数据库记录"""
        # 这里应该导入实际的CreditCard模型
        # 为了避免循环导入，使用动态导入
        from db_models.cards import CreditCard
        return CreditCard(**card_data)

    def _get_credit_card_model(self):
        """获取信用卡数据库模型"""
        from db_models.cards import CreditCard
        return CreditCard
    
    def _get_fee_type_display(self, fee_type) -> str:
        """获取年费类型的中文显示名称"""
        type_display = {
            "rigid": "刚性年费",
            "transaction_count": "刷卡次数减免",
            "transaction_amount": "刷卡金额减免",
            "points_exchange": "积分兑换减免"
        }
        return type_display.get(fee_type, "未知类型") 